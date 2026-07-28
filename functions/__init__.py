import importlib, os
from pathlib import Path
DIR = Path(__file__).resolve().parent
ls = os.listdir(DIR)
ls.remove("__init__.py")
try:
    ls.remove("__pycache__")
except:
    pass
for file in ls:
    importlib.import_module("." + file.replace(".py", ""), "extensions.sonny_tags.functions")
