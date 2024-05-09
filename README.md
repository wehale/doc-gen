# doc-gen

Doc-gen is an open source utility for testing the use of Artificial Intelligence (AI) in the Software Development Life Cycle (SDLC). Version 0.1 allows the user to generate documentation from a set of source code using three different Inference Providers and their associated Large Language Models (LLMs). The Inference Providers that are supported are: OpenAI, Google AI and Hugging Face. The LLMs used can be configured in the root `config.yaml` file.

## Usage

### Platforms supported

Doc-gen 0.1 is a command line utility. It has been created and tested on Linux, however it should also run on MacOS and Windows under Windows Subsystem for Linux (WSL) with Ubuntu 22.

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

#### OpenAI

In order to use OpenAI as an Inference Provider you will need to set up an OpenAI account. Comprehensive information on OpenAI account setup is available here: https://platform.openai.com/docs/quickstart/account-setup. OpenAI has a free tier which is rate limited, or you can choose a pay as you go plan. More information on pricing options at OpenAI are available here: https://openai.com/api/pricing/. The pricing is not too terribly expensive (I spent $30 getting Doc-gen to the 0.1 release). But having said that, it is not free either. If free is what you are looking for you may wish to opt for one of the other Inference Providers listed below.

Once you have set up your account you will need an `API Key`. Information on getting an API Key for OpenAI is available here: https://platform.openai.com/api-keys

Once you have your OpenAI API Key, you will need to store it in an environment variable. Doc-gen looks for it in the `OPENAI_API_KEY` environment variable. For example can add it to your environment by adding the following line to your ~/.profile file:

    export OPENAI_API_KEY="sk-proj-wLMaFKEothis-is-a-fake-key-so-dont-use-it-it-is-only-an-exampleX"

In OpenAI, API Keys are attached to projects. You will want to create a new project and API Key for any testing you do with Doc-gen so that you have a clean sandbox in which to do your work.

