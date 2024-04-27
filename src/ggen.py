

class GoogleAIGenerator:
    def __init__(self, args, key, config):
        self._args = args
        self._key = key
        self._config = config

    def generate(self):
        print(f"{self._config['gllm']['name']} is generating...")