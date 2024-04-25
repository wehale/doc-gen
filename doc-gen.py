from openai import OpenAI
from sys import stdout
import argparse
import glob
import os
import time
import jsonlines

ASSISTANT_NAME = "doc-gen"
LOG_PREFIX = "[doc-gen.py]>"

class output_delimiters:
  START_DESCRIPTION = "[SD]"
  END_DESCRIPTION = "[ED]"
  START_FUNCTIONS = "[SF]"
  END_FUNCTIONS = "[EF]"
  START_SV = "[SSV]"
  END_SV = "[ESV]"


# Parse incoming arguments
parser = argparse.ArgumentParser(prog="doc-gen.py", description="Generate documentation for a code file using OpenAI's GPT-4")
parser.add_argument('-cf', "--clean-files", help="Delete all files from the project", action="store_true")
parser.add_argument('-ca', "--clean-assistants", help="Delete all assistants from the project", action="store_true")
parser.add_argument('-s', "--stream", help="Stream the output of the assistant", action="store_true")
args = parser.parse_args()  


# Create the client for Open AI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Delete all files from the project if asked to do so (this is generally a good idea if you want a clean run)
if args.clean_files:
  print(LOG_PREFIX + "Deleting all files from the project...")
  if client.files.list() != None:
    for f in client.files.list():
      client.files.delete(file_id=f.id)
      print(LOG_PREFIX + "Deleted file " + f.filename + ": " + f.id)

# Delete all assistants from the project if asked to do so (this isn't really necessary, but it's here for completeness)
if args.clean_assistants:
  print(LOG_PREFIX + "Deleting all assistants from the project...")
  if client.beta.assistants.list() != None:
    for a in client.beta.assistants.list():
      client.beta.assistants.delete(assistant_id=a.id)
      print(LOG_PREFIX + "Deleted assistant " + a.name + ": " + a.id)
  time.sleep(2) # Wait for the assistants to be deleted from remote before continuing

# Create or reuse the assistant, just grabs the first assistant it finds in the project
assistant = None
if client.beta.assistants.list() != None:
  for a in client.beta.assistants.list():
    if a.name == ASSISTANT_NAME:
        assistant = a
        print(LOG_PREFIX + "Found and using existing assistant " + assistant.name)
        break

# If no assistant was found, create a new one
if assistant is None: 
  assistant = client.beta.assistants.create(
    name=ASSISTANT_NAME,
    instructions="You are a code documentation generator. Given a code file, write the documentation for it.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-turbo",
    # temperature=0.15 # Can't do this yet in the beta api unfortunately, even though it says you can in the API Docs (ironic?)
    # https://community.openai.com/t/how-to-set-temperature-and-other-sampling-parameters-of-model-in-open-ai-assistant-api/486368/22
  )
  print(LOG_PREFIX+"Failed to find existing assistant, created assistant " + assistant.name)

# Read the prompt from prompt.txt file
# file_prompt = open("./prompt/prompt.txt", "r")
# prompt = file_prompt.read()

# Create a thread
thread = client.beta.threads.create()
print(LOG_PREFIX + "Created thread " + thread.id)

local_code_files = glob.glob("./src/*")
for local_code_file in local_code_files:
  remote_code_file = None
  if client.files.list() != None:
    for f in client.files.list():
      if f.purpose == "assistants" and f.filename == local_code_file.split("/")[2]:
        remote_code_file = f
        print(LOG_PREFIX + "Found and using existing code file " + remote_code_file.filename + ": " + remote_code_file.id)
        break

  if remote_code_file is None:
    remote_code_file = client.files.create(file=open(local_code_file, "rb"), purpose="assistants")
    print(LOG_PREFIX + "Created code file " + remote_code_file.filename + ": " + remote_code_file.id)
    time.sleep(2) # Wait for the file to be uploaded to remote before continuing
  
  # Create file message for the thread
  file_message = client.beta.threads.messages.create(
    thread.id,
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
          if c.text.value.startswith(output_delimiters.START_DESCRIPTION):
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
      
      # Close the markdown file
      markdown_file.close()
      print(LOG_PREFIX + "Wrote markdown file " + markdown_file.name)



exit()
