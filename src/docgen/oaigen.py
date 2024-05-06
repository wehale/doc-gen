from openai import OpenAI
import time
from sys import stdout
import jsonlines
import glob
import os

class output_delimiters:
  START_DESCRIPTION = "[SD]"
  START_FUNCTIONS = "[SF]"
  START_SV = "[SSV]"

class OpenAIGenerator:

    ASSISTANT_NAME = "doc-gen"
    LOG_PREFIX = "[oai-gen]>"

    def __init__(self, args, key, config):
        self._client = OpenAI(api_key=key)
        self._args = args
        self._config = config
        self._files = glob.glob(self._config['input']['doc_path']+"/*")
        self._prompts_file_str = self._config['oaillm']['doc_prompts']
        self._assistant = None
        self._thread = None

    def generate(self) -> dict:        
        if self._args.clean_files:
            self._delete_files()
        if self._args.clean_assistants:
            self._delete_assistants()
        self._find_or_create_assistant()
        self._create_thread()
        stats = {self._config['oaillm']['description_prefix']: {}}
        for lf in self._files:
            t1 = time.time()
            rf = self._find_or_create_remote_file(lf)
            self._delete_local_markdown_file(rf)
            ps = jsonlines.open(self._prompts_file_str) #can't loop jsonlines reader more than once
            for p in ps:
                self._create_prompt_message(p)
                run = self._create_run(self._args.stream)
                if self._args.stream:
                    self._run_stream(run)
                else:
                    self._run_markdown(rf, p, run)
            t2 = time.time()
            lf_split = lf.split("/")
            stats[self._config['oaillm']['description_prefix']][lf_split[len(lf_split)-1]] = t2-t1
        return stats

    def _delete_files(self):
        print(self.LOG_PREFIX + "Deleting all files from the project...")
        if self._client.files.list() != None:
            for f in self._client.files.list():
                self._client.files.delete(file_id=f.id)
                print(self.LOG_PREFIX + "Deleted file " + f.filename + ": " + f.id)
    
    def _delete_assistants(self):
        print(self.LOG_PREFIX + "Deleting all assistants from the project...")
        if self._client.beta.assistants.list() != None:
            for a in self._client.beta.assistants.list():
                print(self.LOG_PREFIX + "Deleting assistant " + a.name + ": " + a.id)                
                self._client.beta.assistants.delete(assistant_id=a.id)
                time.sleep(2)
    
    def _find_or_create_assistant(self):
        # Create or reuse the assistant, just grabs the first assistant it finds in the project that has the ASSISTANT_NAME
        if self._client.beta.assistants.list() != None:
            for a in self._client.beta.assistants.list():
                if a.name == self.ASSISTANT_NAME:
                    self._assistant = a
                    print(self.LOG_PREFIX + "Found and using existing assistant " + self._assistant.name)
                    break

        # If no assistant was found, create a new one
        if self._assistant is None: 
            self._assistant = self._client.beta.assistants.create(
                name=self.ASSISTANT_NAME,
                instructions="You are a code documentation generator. Given a code file, write the documentation for it.",
                tools=[{"type": "code_interpreter"}],
                model=self._config['oaillm']['model'],
                # temperature=0.15 # Can't do this yet in the beta api unfortunately, even though it says you can in the API Docs (ironic?)
                # https://community.openai.com/t/how-to-set-temperature-and-other-sampling-parameters-of-model-in-open-ai-assistant-api/486368/22
            )
            print(self.LOG_PREFIX+"Failed to find existing assistant, created assistant " + self._assistant.name)

    def _create_thread(self):
        self._thread = self._client.beta.threads.create()
        print(self.LOG_PREFIX + "Created thread " + self._thread.id)

    def _find_or_create_remote_file(self, lf: str):
        remote_code_file = None
        # Find the remote code file to use if it is already uploaded
        if self._client.files.list() != None:
            for rf in self._client.files.list():
                lf_split = lf.split("/")
                if rf.purpose == "assistants" and rf.filename == lf_split[len(lf_split) - 1]:
                    remote_code_file = rf
                    print(self.LOG_PREFIX + "Found and using existing code file " + remote_code_file.filename + ": " + remote_code_file.id)
                    break

        if remote_code_file is None:
            remote_code_file = self._client.files.create(file=open(lf, "rb"), purpose="assistants")
            print(self.LOG_PREFIX + "Created code file " + remote_code_file.filename + ": " + remote_code_file.id)
            time.sleep(2) # DEBUG: Wait for the file to be uploaded to remote before continuing, snippet problem?
  
        # Create file message for the thread
        self._client.beta.threads.messages.create(
            self._thread.id,
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


    def _create_prompt_message(self, p):
        self._client.beta.threads.messages.create(
            self._thread.id,
            role="user",
            content=p['description']
        )

    def _create_run(self, stream: bool):
        return self._client.beta.threads.runs.create(
            thread_id=self._thread.id,
            assistant_id=self._assistant.id,
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

    def _run_markdown(self, rf, p, run):
        # We are writing markdown files
        # Open the markdown file for the output with mode append
        markdown_file = open(self._config['output']['doc_path']+ "/" +
                             self._config['oaillm']['gen_file_prefix'] +
                             rf.filename.split(".")[0]+".md", "a")

        # Wait for the run to complete and print out the messages
        while (run.status != "completed"):
            run = self._client.beta.threads.runs.retrieve(thread_id=self._thread.id, run_id=run.id)
            time.sleep(2)
            print(self.LOG_PREFIX + "Processing " + p["title"] + " for " + rf.filename + "...")

        # Write out only the messages from the thread
        messages = self._client.beta.threads.messages.list(run_id=run.id, thread_id=self._thread.id)
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
                print(self.LOG_PREFIX + c.text.value)
      
        # Write the bottom tag
        markdown_file.write("\n" + "(Generated by "+ self._config['author'] + 
                            " using " + self._config['oaillm']['name'] + " " + 
                            self._config['oaillm']['model'] +")\n")
        # Close the markdown file
        markdown_file.close()
        print(self.LOG_PREFIX + "Wrote markdown file " + markdown_file.name)
