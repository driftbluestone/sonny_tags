import os
from api import config, permission, users
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data/extensions/sonny_tags/tags"

permission.create("view", "View Tags", None, True, True, True)
permission.create("create", "Create Tags", None, True, True, True)
permission.create("admin", "Tag Admin", "administrator", True, False, True)
users.new_data_field("tags", list)
config.create_field("limit_creation_to_admins", False)
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)