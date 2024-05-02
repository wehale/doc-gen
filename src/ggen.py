import google.generativeai as gai
import jsonlines as jsonl
import glob



class GoogleAIGenerator:

    LOG_PREFIX = "[gai-gen]>"

    def __init__(self, args, key, config):
        self._args = args
        self._key = key
        self._config = config
        self._model = gai.GenerativeModel(self._config['gllm']['model'])
        self._files = glob.glob(self._config['input']['path']+"/*")
        self._prompts_file_str = self._config['gllm']['prompts']

    def generate(self):
        print(self.LOG_PREFIX + f"{self._config['gllm']['name']} is generating...")
        for f in self._files:
            input_file = open(f, 'r')
            input_file_split = f.split("/")
            input_file_name = input_file_split[len(input_file_split)-1]
            output_file_name = self._config['gllm']['gen_file_prefix'] + input_file_split[len(input_file_split)-1].split(".")[0] + ".md"
            open(self._config['output']['path']+"/"+output_file_name, 'w').close() #clear output file
            output_file = open(self._config['output']['path']+"/"+output_file_name, 'a') # append the output file
            output_file.write("\n" + "# "+ self._config['gllm']['description_prefix'] + ": " + input_file_name + "\n")
            code_file_str_for_prompt = "Consider the following code: \n" + input_file.read()
            chat = self._model.start_chat()
            chat.send_message(code_file_str_for_prompt)
            ps = jsonl.open(self._prompts_file_str)
            for prompt in ps:
                content = chat.send_message(prompt['description'])
                print(self.LOG_PREFIX + content.text)
                output_file.write("\n" + "## "+ prompt['title']+ ": " + input_file_name + "\n")
                output_file.write(content.text)
                output_file.write("\n")
                output_file.write("\n" + "(Generated by "+ self._config['author'] + 
                            " using " + self._config['gllm']['name'] + " " + 
                            self._config['gllm']['model'] +")\n")
            input_file.close()
            output_file.close()
        