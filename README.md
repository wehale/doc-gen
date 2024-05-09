# doc-gen

Doc-gen is an open source utility for testing the use of Artificial Intelligence (AI) in the Software Development Life Cycle (SDLC). The current version 0.1 allows the user to generate documentation from a set of source code using three different Inference Providers and their associated Large Language Models (LLMs). The Inference Providers that are supported are: [OpenAI](https://openai.com/), [Google AI](https://ai.google/) and [Hugging Face](https://huggingface.co/). The LLMs used can be configured in the root `config.yaml` file.

- [doc-gen](#doc-gen)
  - [Usage](#usage)
    - [Platforms supported](#platforms-supported)
    - [Install Python](#install-python)
    - [Clone the Repo](#clone-the-repo)
    - [Configure Your API Keys](#configure-your-api-keys)
      - [OpenAI API Key](#openai-api-key)
      - [Google AI API Key](#google-ai-api-key)
      - [Hugging Face API Key](#hugging-face-api-key)
  - [Running doc-gen](#running-doc-gen)
  - [Output](#output)

## Usage

### Platforms supported

Doc-gen is a command line utility. It has been created and tested on Linux, however it should also run on MacOS and Windows under Windows Subsystem for Linux (WSL) with Ubuntu 22.

### Install Python

Doc-gen is entirely written in Python so you will need Python 3.10 or later to run this utility. You can install Python on the command line using the following commands:

    $ sudo apt-get update
    $ sudo apt-get install python

### Clone the Repo

Doc-gen is open source and is provided as source code. In order to run it you will need to clone the `doc-gen` repo from GitHub. You can clone the repo with the following command:

    $ git clone git@github.com:wehale/doc-gen.git

In order to do this you will need both `git` and an `SSH key` in your GitHub account. For more information on how to set this up please refer to the following [documentation from GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

### Configure Your API Keys

Doc-gen supports three different Inference Providers, OpenAI, GoogleAI and Hugging Face. The cost of using these providers varies from free to pay as you go, to a monthly fee. Doc-gen is not paying for access to these providers so you will have to set up your own accounts and set the associated `API Keys` in your system's environment variables. For more information on doing this see below:

#### OpenAI API Key

In order to use OpenAI as an Inference Provider you will need to set up an OpenAI account. Comprehensive information on OpenAI account setup is available here: https://platform.openai.com/docs/quickstart/account-setup. OpenAI has a free tier which is rate limited, or you can choose a pay as you go plan. More information on pricing options at OpenAI are available here: https://openai.com/api/pricing/. The pricing is not too terribly expensive (I spent $30 getting Doc-gen to the 0.1 release). But having said that, it is not free either. If free is what you are looking for you may wish to opt for one of the other Inference Providers listed below.

Once you have set up your account you will need an `API Key`. Information on getting an API Key for OpenAI is available here: https://platform.openai.com/api-keys

Once you have your OpenAI API Key, you will need to store it in an environment variable. Doc-gen looks for it in the `OPENAI_API_KEY` environment variable. For example you can add it to your environment by adding the following line to your `~/.profile` file:

    export OPENAI_API_KEY="sk-proj-wLMaFKEothis-is-a-fake-key-so-dont-use-it-it-is-only-an-exampleX"

Once you have added the API key to your `~/.profile` file you'll need to `source` the file to load it into your working environment. To `source` the file use the following command:

    $ source ~/.profile

In OpenAI, API Keys are attached to projects. You will want to create a new project and API Key for any testing you do with Doc-gen so that you have a clean sandbox in which to do your work.

#### Google AI API Key

In order to use Google AI as an Inference Provider you will need a Google AI (for Developers) account, which you can get through your regular Google Login if you have one for GMail. More information on Google AI for Developers is located here: https://ai.google.dev/gemini-api/docs. Use of Google AI Gemini is free ... to a point based on rate and requests per day (RPD) limits. More information on pricing is available here: https://ai.google.dev/pricing

Once you have set up your account you will need an `API Key`. Information on getting your API key for Google AI is located here: https://ai.google.dev/gemini-api/docs/api-key

Once you have your API Key, you'll need to install it as an environment variable. You can do this by adding it to your `~/.profile` file as the following example illustrates:

    export GOOGLE_API_KEY="AIz-this-is-only-an-example-dont-use-this-uQ"

Once you have added the API key to your `~/.profile` file you'll need to `source` the file to load it into your working environment. To `source` the file use the following command:

    $ source ~/.profile

Google AI API Keys are tied to Google Cloud projects. Pricing is also tied to the pricing model chosen for that project. As with OpenAI, if you do a lot of work with this or any other key you'll be gently pushed into pay-as-you-go pricing.

#### Hugging Face API Key

In order to use Hugging Face as an Inference Provider you will need to create a Hugging Face account. Information on creating an account is available here: https://huggingface.co/welcome. Use of Hugging Face has a (severely rate limited) free tier or you can sign up with a `PRO` account for what is currently $9/month. Information on pricing is available here: https://huggingface.co/pricing

As with the Inference Providers listed above, you will need an API key (called an Access Token) from Hugging Face to use the API. You can create an API Key using this documentation: https://huggingface.co/docs/hub/security-tokens

Once you have your API Key, you'll need to install it as an environment variable. You can do this by adding it to your `~/.profile` file as the following example illustrates:

    export HF_API_KEY="hf_sZB-this-is-only-an-example-dont-use-this-WFFG"

Once you have added the API key to your `~/.profile` file you'll need to `source` the file to load it into your working environment. To `source` the file use the following command:

    $ source ~/.profile

`Access Tokens` in Hugging Face are tied to specific use cases and can only be used for that purpose. You can create multiple `Access Tokens` for different use cases.


## Running doc-gen

Once you have set up at least one API Key you can run doc-gen with the following command:

    $ ./run.sh

The firs thing that `run.sh` does is create a Python virtual environment and loads all the dependencies for `doc-gen` into that environment. After running, `run.sh` automatically deactivates the virtual environment. The Python venv is stored in the `dgv` directory.

Doc-gen runs according to the configuration settings in the `config.yaml` file. Complete information on the settings in the `config.yaml` file are located in the file itself. [config.yaml](./config.yaml)

Doc-gen is written to only run against Inference Providers with configured `API Keys`, If the settings in `config.yaml` are set to run against an Inference Provider for which no key is found, doc-gen will not run generation for that IP.

Doc-gen uses Python threading to run all provided files against all Inference Providers at the same time. 

## Output

Currently the output of Doc-gen is a set of markdown `.md` files and an HTML site generated from those `.md` files through Sphinx. All of the output is generated into the `build` directory. 

By default, `doc-gen` runs against the two code files in the `./samples` directory `calc.c` and `SpellChecker.java`. If you would like to run it against some other code, you can either add the code files of your choosing into the `./samples` director OR change the `input.doc_path` setting in the `config.yaml` configuration file.

The last thing that `run.sh` does is to give the user the option to open the created HTML in the default browser of their choosing. This way the generated content can be viewed side by side.

For an example of what `doc-gen`'s html output looks like please see the published output here: https://wehale.github.io/doc-gen-pub/latest/