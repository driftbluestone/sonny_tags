import importlib, os
from pathlib import Path
DIR = Path(__file__).resolve().parent
ls = os.listdir(DIR)
ls.remove("__init__.py")
for file in ls:
    importlib.import_module("." + file.replace(".py", ""), "extensions.sonny_tags.admin_functions")
