import argparse
import glob
import oaigen
import os
import yaml

# Parse incoming arguments
parser = argparse.ArgumentParser(prog="doc-gen.py", description="Generate documentation for code files using a given LLM configuration")
parser.add_argument('-cf', "--clean-files", help="Delete all files from the project", action="store_true")
parser.add_argument('-ca', "--clean-assistants", help="Delete all assistants from the project", action="store_true")
parser.add_argument('-s', "--stream", help="Stream the output of the assistant", action="store_true")
args = parser.parse_args()  

# Get the yaml configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

#debug
print(config)
exit()

files = glob.glob("./src/*")

prompts_file_str = "./prompt/prompts.jsonl"

key = os.environ['OPENAI_API_KEY']
oaigenerator = oaigen.OpenAIGenerator(args, key, files, prompts_file_str)

oaigenerator.generate()
  