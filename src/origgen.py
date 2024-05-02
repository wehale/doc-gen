import glob
import code_utils

class OriginalGenerator():
    def __init__(self, config, args):
        self._config = config
        self._args = args
        self._files = glob.glob(self._config['input']['path']+"/*")

    def generate(self):
        for f in self._files:
            input_file = open(f, 'r')
            input_file_split = f.split("/")
            input_file_name = input_file_split[len(input_file_split)-1]
            output_file_path = self._config['output']['path']+"/"+self._config['orig']['gen_file_prefix']+input_file_name.split(".")[0] + ".md"
            open(output_file_path, 'w').close()
            output_file = open(output_file_path, 'a')
            output_file.write("\n" + "# "+ self._config['orig']['description_prefix'] + ": " + input_file_name + "\n")
            output_file.write("```"+code_utils.get_language_from_extension(input_file_name.split(".")[1])+"\n")
            output_file.write(input_file.read())
            output_file.write("\n```\n")
            input_file.close()
            output_file.close()