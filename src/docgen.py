import argparse
import docgen.oaigen as oai_doc_gen
import docgen.ggen as g_doc_gen
import docgen.hfgen as hf_doc_gen
import docgen.origgen as orig_doc_gen
import os
import yaml
import util.check_env as checkenv
import util.code_utils as code_utils
import concurrent
import logging
import enlighten

# Parse incoming arguments
parser = argparse.ArgumentParser(prog="docgen.py", description="Generate documentation for code files using a given LLM configuration")
parser.add_argument('-cf', "--clean-files", help="Delete all remote files from the OpenAI project, use CAUTION when invoking this option!!", action="store_true")
parser.add_argument('-ca', "--clean-assistants", help="Delete all assistants from the OpenAI project, use CAUTION when invoking this option!!", action="store_true")
parser.add_argument('-s', "--stream", help="Stream the output of the OpenAI assistant", action="store_true")
args = parser.parse_args()  


# Get the yaml configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

futures = [] # List of futures for the threads
# Create a thread pool executor for processing the doc generation
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

logging.basicConfig(level=logging.WARN) # Set to ERROR to suppress debug messages
logger = logging.getLogger(__name__)
manager = enlighten.get_manager()

if (config['orig']['use']):
    # Use the original generator to generate the doc for the original code files
    # This just copies the original code files to the output directory as .md files
    orig_doc_generator = orig_doc_gen.OriginalGenerator(config, args, manager)
    futures.append(executor.submit(orig_doc_generator.generate))

if (config['oaillm']['use'] and checkenv.checkOpenAIKey()):
    key = os.environ['OPENAI_API_KEY']
    if (config['oaillm']['doc_run']):
        # Run the doc generation on the OpenAI project
        oai_doc_generator = oai_doc_gen.OpenAIGenerator(args, key, config, manager)
        futures.append(executor.submit(oai_doc_generator.generate))

if (config['gllm']['use'] and checkenv.checkGoogleAIKey()):
    key = os.environ['GOOGLE_API_KEY']
    if (config['gllm']['doc_run']):
        # Use Google's LLM to generate the doc
        g_doc_generator = g_doc_gen.GoogleAIGenerator(args, key, config, manager)
        futures.append(executor.submit(g_doc_generator.generate))

if (config['hfllm']['use'] and checkenv.checkHuggingFaceKey()):
    key = os.environ['HF_API_KEY']
    if (config['hfllm']['doc_run']):
        # Use HuggingFace's LLM to generate the doc
        hf_doc_generator = hf_doc_gen.HuggingFaceGenerator(args, key, config, manager)
        futures.append(executor.submit(hf_doc_generator.generate))

# Wait for all the threads to complete
executor.shutdown(wait=True)

# Print the results of the threads (processing time)
for future in futures:
    logger.log(code_utils.LOG_LEVEL, future.result())