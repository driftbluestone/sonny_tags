from utils import callable_module as CallableModule, jsonIO
from pathlib import Path
DIR = Path(__file__).resolve().parent
SPECIAL_TAGS, DISPLAYED_SPECIAL_TAGS, ADMIN_TAGS, DISPLAYED_ADMIN_TAGS = jsonIO.load(f"{DIR}/special_tags.json")
VALID_NAME_CHARS = set("0123456789abcdefghijklmnopqrstuvwxyz_-")
__all__ = ["CallableModule", "SPECIAL_TAGS", "DISPLAYED_SPECIAL_TAGS", "ADMIN_TAGS", "DISPLAYED_ADMIN_TAGS", "VALID_NAME_CHARS"]