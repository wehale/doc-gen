import os

LOG_LEVEL= 100

def get_code_files_from_glob(glob: list):
    files = []
    for f in glob:
        if os.path.isfile(f):
            f_split = f.split(".")
            ext = f_split[len(f_split)-1]
            if (get_language_from_extension(ext) != "plaintext") and os.path.getsize(f) > 0:
                files.append(f)
    return files

def get_language_from_extension(ext: str) -> str:
    if ext == "py":
        return "python"
    elif ext == "js":
        return "javascript"
    elif ext == "java":
        return "java"
    elif ext == "rb":
        return "ruby"
    elif ext == "php":
        return "php"
    elif ext == "cs":
        return "csharp"
    elif ext == "cpp":
        return "cpp"
    elif ext == "c":
        return "c"
    elif ext == "swift":
        return "swift"
    elif ext == "kt":
        return "kotlin"
    elif ext == "go":
        return "go"
    elif ext == "rs":
        return "rust"
    elif ext == "ts":
        return "typescript"
    elif ext == "sh":
        return "bash"
    elif ext == "r":
        return "r"
    elif ext == "m":
        return "matlab"
    elif ext == "jl":
        return "julia"
    elif ext == "pl":
        return "perl"
    elif ext == "sql":
        return "sql"
    elif ext == "html":
        return "html"
    elif ext == "css":
        return "css"
    elif ext == "xml":
        return "xml"
    elif ext == "yaml":
        return "yaml"
    elif ext == "json":
        return "json"
    elif ext == "toml":
        return "toml"
    elif ext == "md":
        return "markdown"
    elif ext == "tex":
        return "latex"
    elif ext == "rmd":
        return "rmarkdown"
    elif ext == "ipynb":
        return "python"
    else:
        return "plaintext"