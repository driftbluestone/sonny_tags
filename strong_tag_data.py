import json
from utils import callable_module as CallableModule
from pathlib import Path
DIR = Path(__file__).resolve().parent
with open(f"{DIR}/special_tags.json", "r") as file:
    SPECIAL_TAGS, DISPLAYED_SPECIAL_TAGS, ADMIN_TAGS, DISPLAYED_ADMIN_TAGS = json.load(file).values()
VALID_NAME_CHARS = set("0123456789abcdefghijklmnopqrstuvwxyz_-")
