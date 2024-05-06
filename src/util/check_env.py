import os

def checkOpenAIKey() -> bool:
    if 'OPENAI_API_KEY' not in os.environ:
        print("Please set your OpenAI API key as an environment variable. You can do this by running `export OPENAI_API_KEY=yourkey`")
        return False
    return True

def checkGoogleAIKey() -> bool:
    if 'GOOGLE_API_KEY' not in os.environ:
        print("Please set your Google AI API key as an environment variable. You can do this by running `export GOOGLE_API_KEY=yourkey`")
        return False
    return True

def checkHuggingFaceKey() -> bool:
    if 'HF_API_KEY' not in os.environ:
        print("Please set your Hugging Face API key as an environment variable. You can do this by running `export HF_API_KEY=yourkey`")
        return False
    return True
