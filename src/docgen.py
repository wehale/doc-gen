import argparse
import oaigen
import ggen
import os
import yaml

# Parse incoming arguments
parser = argparse.ArgumentParser(prog="docgen.py", description="Generate documentation for code files using a given LLM configuration")
parser.add_argument('-cf', "--clean-files", help="Delete all files from the project", action="store_true")
parser.add_argument('-ca', "--clean-assistants", help="Delete all assistants from the project", action="store_true")
parser.add_argument('-s', "--stream", help="Stream the output of the assistant", action="store_true")
args = parser.parse_args()  

# Get the yaml configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if (config['oaillm']['use']):
    # Use OpenAI's LLM to generate the doc
    key = os.environ['OPENAI_API_KEY']
    oaigenerator = oaigen.OpenAIGenerator(args, key, config)
    oaigenerator.generate()
elif (config['gllm']['use']):
    # Use Google's LLM to generate the doc
    key = os.environ['GOOGLEAI_API_KEY']
    ggenerator = ggen.GoogleAIGenerator(args, key, config)
    ggenerator.generate()
  