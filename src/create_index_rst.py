import glob
import yaml

def _create_index_rst():
    # Get the yaml configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Get all the files in the doc directory
    files = glob.glob(config['output']['path']+"/*")

    # Create the index.rst file
    with open(config['docpub']['path']+"/index.rst", "w") as f:
        f.write("Documentation\n")
        f.write("=============\n")
        f.write("\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("\n")
        files.sort()
        for file in files:
            f_split = file.split("/")
            f.write("   "+ f_split[len(f_split)-1] +"\n")
        f.close()

_create_index_rst()