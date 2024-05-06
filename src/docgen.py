import argparse
import docgen.oaigen as oaigen
import docgen.ggen as ggen
import docgen.hfgen as hfgen
import docgen.origgen as origgen
import os
import yaml
import util.check_env as checkenv

# Parse incoming arguments
parser = argparse.ArgumentParser(prog="docgen.py", description="Generate documentation for code files using a given LLM configuration")
parser.add_argument('-cf', "--clean-files", help="Delete all remote files from the OpenAI project, use CAUTION when invoking this option!!", action="store_true")
parser.add_argument('-ca', "--clean-assistants", help="Delete all assistants from the OpenAI project, use CAUTION when invoking this option!!", action="store_true")
parser.add_argument('-s', "--stream", help="Stream the output of the OpenAI assistant", action="store_true")
args = parser.parse_args()  

stats = []

# Get the yaml configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if (config['orig']['use']):
    # Use the original generator to generate the doc
    origgenerator = origgen.OriginalGenerator(config, args)
    stats.append(origgenerator.generate())

if (config['oaillm']['use'] and checkenv.checkOpenAIKey()):
    # Use OpenAI's LLM to generate the doc
    key = os.environ['OPENAI_API_KEY']
    oaigenerator = oaigen.OpenAIGenerator(args, key, config)
    stats.append(oaigenerator.generate())

if (config['gllm']['use'] and checkenv.checkGoogleAIKey()):
    # Use Google's LLM to generate the doc
    key = os.environ['GOOGLE_API_KEY']
    ggenerator = ggen.GoogleAIGenerator(args, key, config)
    stats.append(ggenerator.generate())

if (config['hfllm']['use'] and checkenv.checkHuggingFaceKey()):
    # Use HuggingFace's LLM to generate the doc
    key = os.environ['HF_API_KEY']
    hfgenerator = hfgen.HuggingFaceGenerator(args, key, config)
    stats.append(hfgenerator.generate())

for s in stats:
    print(s)