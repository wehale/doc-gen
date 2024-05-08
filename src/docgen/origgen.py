import glob
import util.code_utils as code_utils
import os
import logging
import concurrent

class OriginalGenerator():
    
    LOG_PREFIX = "[orig-gen]>"
    PBAR_COLOR = "lightblue"
    
    def __init__(self, config, args, manager):
        self._config = config
        self._args = args
        self._files = code_utils.get_code_files_from_glob(glob.glob(self._config['input']['doc_path']+"/**/*", recursive=True))
        self._log = logging.getLogger(__name__)
        self._pbar = manager.counter(total=len(self._files), desc=self.LOG_PREFIX, unit="prompts", color=self.PBAR_COLOR)

    def generate(self) -> None:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self._files))
        for f in self._files:
            if not os.path.isfile(f):
                continue
            executor.submit(self._gen_markdown_file, f)
        # Wait for all the threads to complete
        executor.shutdown(wait=True)

    def _gen_markdown_file(self, f):
        input_file = open(f, 'r')
        input_file_split = f.split("/")
        input_file_name = input_file_split[len(input_file_split)-1]
        output_file_path = self._config['output']['doc_path']+"/"+self._config['orig']['gen_file_prefix']+input_file_name.split(".")[0] + ".md"
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        open(output_file_path, 'w').close()
        output_file = open(output_file_path, 'a')
        output_file.write("\n" + "# "+ self._config['orig']['description_prefix'] + ": " + input_file_name + "\n")
        output_file.write("```"+code_utils.get_language_from_extension(input_file_name.split(".")[1])+"\n")
        output_file.write(input_file.read())
        output_file.write("\n```\n")
        input_file.close()
        output_file.close()
        self._log.log(code_utils.LOG_LEVEL, "Generated file: " + output_file_path)
        self._pbar.update()