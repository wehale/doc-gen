from openai import OpenAI
import time
from sys import stdout
import jsonlines
import glob
import os
import logging
import util.code_utils as code_utils
import concurrent

class output_delimiters:
  START_DESCRIPTION = "[SD]"
  START_FUNCTIONS = "[SF]"
  START_SV = "[SSV]"

class OpenAIGenerator:

    ASSISTANT_NAME = "doc-gen"
    LOG_PREFIX = "[oai-gen]>"
    PBAR_COLOR = "lightgreen"

    def __init__(self, args, key, config, manager):
        self._client = OpenAI(api_key=key)
        self._args = args
        self._config = config
        self._files = code_utils.get_code_files_from_glob(glob.glob(self._config['input']['doc_path']+"/**/*", recursive=True))
        self._prompts_file_str = self._config['oaillm']['doc_prompts']
        self._log = logging.getLogger(__name__)
        self._pbar = manager.counter(total=len(self._files)*3, desc=self.LOG_PREFIX, unit="prompts", color=self.PBAR_COLOR)

    def generate(self) -> None:        
        if self._args.clean_files:
            self._delete_files()
        if self._args.clean_assistants:
            self._delete_assistants()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self._files))
        for lf in self._files:
            if not os.path.isfile(lf):
                continue
            executor.submit(self._gen_markdown_file, lf)
        # Wait for all the threads to complete
        executor.shutdown(wait=True)

    def _gen_markdown_file(self, lf):
        assistant = self._find_or_create_assistant()
        thread = self._create_thread()
        rf = self._find_or_create_remote_file(thread, lf)
        self._delete_local_markdown_file(rf)
        ps = jsonlines.open(self._prompts_file_str) #can't loop jsonlines reader more than once
        for p in ps:
            self._create_prompt_message(p, thread)
            run = self._create_run(assistant, thread, self._args.stream)
            if self._args.stream:
                self._run_stream(run)
            else:
                self._run_markdown(rf, p, run, thread)

    def _delete_files(self):
        self._log.log(code_utils.LOG_LEVEL, "Deleting all files from the project...")
        if self._client.files.list() != None:
            for f in self._client.files.list():
                self._client.files.delete(file_id=f.id)
                self._log.log(code_utils.LOG_LEVEL, "Deleted file " + f.filename + ": " + f.id)
    
    def _delete_assistants(self):
        self._log.log(code_utils.LOG_LEVEL, "Deleting all assistants from the project...")
        if self._client.beta.assistants.list() != None:
            for a in self._client.beta.assistants.list():
                self._log.log(code_utils.LOG_LEVEL, "Deleting assistant " + a.name + ": " + a.id)                
                self._client.beta.assistants.delete(assistant_id=a.id)
                time.sleep(2)
    
    def _find_or_create_assistant(self) -> any:
        # Create or reuse the assistant, just grabs the first assistant it finds in the project that has the ASSISTANT_NAME
        assistant = None
        if self._client.beta.assistants.list() != None:
            for a in self._client.beta.assistants.list():
                if a.name == self.ASSISTANT_NAME:
                    assistant = a
                    self._log.log(code_utils.LOG_LEVEL, "Found and using existing assistant " + assistant.name)
                    break
        # If no assistant was found, create a new one
        if assistant is None: 
            assistant = self._client.beta.assistants.create(
                name=self.ASSISTANT_NAME,
                instructions="You are a code documentation generator. Given a code file, write the documentation for it.",
                tools=[{"type": "code_interpreter"}],
                model=self._config['oaillm']['model'],
                # temperature=0.15 # Can't do this yet in the beta api unfortunately, even though it says you can in the API Docs (ironic?)
                # https://community.openai.com/t/how-to-set-temperature-and-other-sampling-parameters-of-model-in-open-ai-assistant-api/486368/22
            )
            self._log.log(code_utils.LOG_LEVEL, self.LOG_PREFIX+"Failed to find existing assistant, created assistant " + assistant.name)
        return assistant

    def _create_thread(self) -> any:
        thread = self._client.beta.threads.create()
        self._log.log(code_utils.LOG_LEVEL, "Created thread " + thread.id)
        return thread

    def _find_or_create_remote_file(self, thread, lf: str):
        remote_code_file = None
        # Find the remote code file to use if it is already uploaded
        if self._client.files.list() != None:
            for rf in self._client.files.list():
                lf_split = lf.split("/")
                if rf.purpose == "assistants" and rf.filename == lf_split[len(lf_split) - 1]:
                    remote_code_file = rf
                    self._log.log(code_utils.LOG_LEVEL, "Found and using existing code file " + remote_code_file.filename + ": " + remote_code_file.id)
                    break

        if remote_code_file is None:
            remote_code_file = self._client.files.create(file=open(lf, "rb"), purpose="assistants")
            self._log.log(code_utils.LOG_LEVEL, "Created code file " + remote_code_file.filename + ": " + remote_code_file.id)
            time.sleep(2) # DEBUG: Wait for the file to be uploaded to remote before continuing, snippet problem?
  
        # Create file message for the thread
        self._client.beta.threads.messages.create(
            thread.id,
            role="user", 
            content="Code file", 
            attachments=[{"file_id": remote_code_file.id, "tools": [{"type": "code_interpreter"}]}]
        )
        time.sleep(2) # DEBUG: Trying to resolve snippet problem

        return remote_code_file

    def _delete_local_markdown_file(self, rf):
        if not self._args.stream:
            output_file_path = (self._config['output']['doc_path']+ "/" +
                 self._config['oaillm']['gen_file_prefix'] +
                 rf.filename.split(".")[0]+".md")
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            open(output_file_path, "w").close()


    def _create_prompt_message(self, p, thread):
        self._client.beta.threads.messages.create(
            thread.id,
            role="user",
            content=p['description']
        )

    def _create_run(self, assistant, thread, stream: bool):
        return self._client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            stream=stream
        )

    def _run_stream(self, run):
        for event in run:
            match event.event:
                case "thread.message.delta":
                    val = event.data.delta.content[0].text.value
                    if (val != None):
                        stdout.write(val)
                case default:
                    stdout.write(".")
            stdout.flush()

    def _run_markdown(self, rf, p, run, thread):
        # We are writing markdown files
        # Open the markdown file for the output with mode append
        markdown_file = open(self._config['output']['doc_path']+ "/" +
                             self._config['oaillm']['gen_file_prefix'] +
                             rf.filename.split(".")[0]+".md", "a")

        # Wait for the run to complete and print out the messages
        while (run.status != "completed"):
            run = self._client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(2)
            self._log.log(code_utils.LOG_LEVEL, "Processing " + p["title"] + " for " + rf.filename + "...")

        # Write out only the messages from the thread
        messages = self._client.beta.threads.messages.list(run_id=run.id, thread_id=thread.id)
        for m in messages.data:
            for c in m.content:
                if c.text.value.startswith(output_delimiters.START_DESCRIPTION):
                    markdown_file.write("\n" + "# "+ self._config['oaillm']['description_prefix'] +
                                         ": " + rf.filename + "\n")
                    markdown_file.write("\n" + "## Description of "+ rf.filename + "\n")
                    c.text.value = c.text.value.replace(output_delimiters.START_DESCRIPTION, "")
                    markdown_file.write(c.text.value + "\n")
                elif c.text.value.startswith(output_delimiters.START_FUNCTIONS):
                    markdown_file.write("\n" + "## Functions in " + rf.filename + "\n")
                    c.text.value = c.text.value.replace(output_delimiters.START_FUNCTIONS, "")
                    markdown_file.write(c.text.value + "\n")
                elif c.text.value.startswith(output_delimiters.START_SV):
                    markdown_file.write("\n" + "## Security Vulnerabilities in " + rf.filename + "\n")
                    c.text.value = c.text.value.replace(output_delimiters.START_SV, "")
                    markdown_file.write(c.text.value + "\n")
                # DEBUG
                self._log.log(code_utils.LOG_LEVEL, c.text.value)
      
        # Write the bottom tag
        markdown_file.write("\n" + "(Generated by "+ self._config['author'] + 
                            " using " + self._config['oaillm']['name'] + " " + 
                            self._config['oaillm']['model'] +")\n")
        # Close the markdown file
        markdown_file.close()
        self._log.log(code_utils.LOG_LEVEL, "Wrote markdown file " + markdown_file.name)
        self._pbar.update()
