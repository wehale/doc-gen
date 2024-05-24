import argparse
import docgen.oaigen as oai_doc_gen
import docgen.az_oaigen as az_oai_doc_gen
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

# Create a thread pool executor for processing the doc generation
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

logging.basicConfig(format='[%(name)s]:%(message)s', level=logging.WARN) # Set to ERROR to suppress debug messages
logger = logging.getLogger(__name__)
manager = enlighten.get_manager()

if (config['orig']['use']):
    # Use the original generator to generate the doc for the original code files
    # This just copies the original code files to the output directory as .md files
    orig_doc_generator = orig_doc_gen.OriginalGenerator(config, args, manager)
    executor.submit(orig_doc_generator.generate)

if (config['oaillm']['use'] and checkenv.checkOpenAIKey()):
    key = os.environ['OPENAI_API_KEY']
    if (config['oaillm']['doc_run']):
        # Run the doc generation on the OpenAI project
        oai_doc_generator = oai_doc_gen.OpenAIGenerator(args, key, config, manager)
        executor.submit(oai_doc_generator.generate)

if (config['az_oaillm']['use'] and checkenv.checkAzOpenAIKey()):
    key = os.environ['AZ_OAI_API_KEY']
    endpoint = os.environ['AZ_OAI_ENDPOINT']
    model_name = os.environ['AZ_OAI_MODEL_NAME']
    if (config['az_oaillm']['doc_run']):
        # Run the doc generation on the OpenAI project
        az_oai_doc_generator = az_oai_doc_gen.AzureOpenAIGenerator(args, key, endpoint, model_name, config, manager)
        executor.submit(az_oai_doc_generator.generate)


if (config['gllm']['use'] and checkenv.checkGoogleAIKey()):
    key = os.environ['GOOGLE_API_KEY']
    if (config['gllm']['doc_run']):
        # Use Google's LLM to generate the doc
        g_doc_generator = g_doc_gen.GoogleAIGenerator(args, key, config, manager)
        executor.submit(g_doc_generator.generate)

if (config['hfllm']['use'] and checkenv.checkHuggingFaceKey()):
    key = os.environ['HF_API_KEY']
    if (config['hfllm']['doc_run']):
        # Use HuggingFace's LLM to generate the doc
        hf_doc_generator = hf_doc_gen.HuggingFaceGenerator(args, key, config, manager)
        executor.submit(hf_doc_generator.generate)

# Wait for all the threads to complete
executor.shutdown(wait=True)
