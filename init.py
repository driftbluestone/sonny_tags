import os
from api import config, permission, users
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data/extensions/sonny_tags/tags"

permission.create(["view", "create", "admin"], [None, None, "administrator"])
users.new_data_field("tags", list)
config.create_field("limit_creation_to_admins", False)
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)