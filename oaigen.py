from openai import OpenAI
import time

class OpenAIGenerator:

    ASSISTANT_NAME = "doc-gen"
    LOG_PREFIX = "[oai-gen]>"

    def __init__(self, args, key, files, prompts):
        self._client = OpenAI(api_key=key)
        self._args = args
        self._files = files
        self._prompts = prompts
        self._fragment_error = False
        self._assistant = None
        self._thread = None

    def generate(self, prompt: str) -> str:
        if self._args.clean_files:
            self._delete_files()
        if self._args.clean_assistants:
            self._delete_assistants()
        self._find_or_create_assistant()
        self._create_thread()
        for lf in self._files:
           self._find_or_create_remote_file(lf)
    
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
                self._client.beta.assistants.delete(assistant_id=a.id)
                print(self.LOG_PREFIX + "Deleted assistant " + a.name + ": " + a.id)
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
                model="gpt-4-turbo",
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
                if rf.purpose == "assistants" and rf.filename == lf.split("/")[2]:
                    remote_code_file = rf
                    print(self.LOG_PREFIX + "Found and using existing code file " + remote_code_file.filename + ": " + remote_code_file.id)
                    break

        if remote_code_file is None:
            remote_code_file = self._client.files.create(file=open(lf, "rb"), purpose="assistants")
            print(self.LOG_PREFIX + "Created code file " + remote_code_file.filename + ": " + remote_code_file.id)
            time.sleep(2) # Wait for the file to be uploaded to remote before continuing
  
        # Create file message for the thread
        file_message = self._client.beta.threads.messages.create(
            self._thread.id,
            role="user", 
            content="Code file", 
            attachments=[{"file_id": remote_code_file.id, "tools": [{"type": "code_interpreter"}]}]
        )

  # If we are writing markdown and there is a local markdown file, clear it
  if args.stream == False:
    open("./doc/"+remote_code_file.filename.split(".")[0]+".md", "w").close()

  # Iterate over the prompts passing them to the thread one at a time and streaming back the output
  # Or write the output to a markdown file depending on the passed -s argument
  prompts = jsonlines.open("./prompt/prompts.jsonl", "r")
  for p in prompts.iter():
  
    # Create a prompt message for the thread
    thread_message = client.beta.threads.messages.create(
      thread.id,
      role="user",
      content=p['description']
    )
    
    # Run the thread run and get back a stream for output
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      stream=args.stream
    )

    # If we are streaming, write the stream of tokens out to the console
    if args.stream:
      # Stream out the tokens from the run
      for event in run:
          match event.event:
              case "thread.message.delta":
                val = event.data.delta.content[0].text.value
                if (val != None):
                      stdout.write(val)
              case default:
                stdout.write(".")
          stdout.flush()
    else:
      # We are writing markdown files
      # Open the markdown file for the output with mode append
      markdown_file = open("./doc/"+remote_code_file.filename.split(".")[0]+".md", "a")

      # Wait for the run to complete and print out the messages
      while (run.status != "completed"):
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(2)
        print(LOG_PREFIX + "Processing " + p["title"] + " for " + remote_code_file.filename + "...")

      # Write out only the messages from the thread
      messages = client.beta.threads.messages.list(run_id=run.id, thread_id=thread.id)
      for m in messages.data:
        for c in m.content:
          if c.text.value.startswith(output_delimiters.ERROR_FRAGMENT):
            print(LOG_PREFIX + "Error Fragment: " + remote_code_file.filename + "\n")
            file_fragment_error = True
          elif c.text.value.startswith(output_delimiters.START_DESCRIPTION):
            markdown_file.write("\n" + "# "+ remote_code_file.filename + "\n")
            markdown_file.write("\n" + "## Description of "+ remote_code_file.filename + "\n")
            c.text.value = c.text.value.replace(output_delimiters.START_DESCRIPTION, "")
            markdown_file.write(c.text.value + "\n")
          elif c.text.value.startswith(output_delimiters.START_FUNCTIONS):
            markdown_file.write("\n" + "## Functions in " + remote_code_file.filename + "\n")
            c.text.value = c.text.value.replace(output_delimiters.START_FUNCTIONS, "")
            markdown_file.write(c.text.value + "\n")
          elif c.text.value.startswith(output_delimiters.START_SV):
            markdown_file.write("\n" + "## Security Vulnerabilities in " + remote_code_file.filename + "\n")
            c.text.value = c.text.value.replace(output_delimiters.START_SV, "")
            markdown_file.write(c.text.value + "\n")
          # DEBUG
          print(LOG_PREFIX + c.text.value)
          if (file_fragment_error):
            exit(1) #no need to keep parsing due to openai errors
      
      # Close the markdown file
      markdown_file.close()
      print(LOG_PREFIX + "Wrote markdown file " + markdown_file.name)
