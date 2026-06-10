import os, subprocess
from api import config, permission, users
from utils.logger import Logger
logger = Logger()
from pathlib import Path
DIR = Path(__file__).resolve().parent
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data/extensions/sonny_tags/tags"

permission.create("view", "View Tags", True, True, True)
permission.create("create", "Create Tags", True, True, True)
permission.create("admin", "Tag Admin", True, False, True)
users.new_data_field("tags", list)
config.create_field("limit_creation_to_admins", False)
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

for dockerfile in os.listdir(f"{DIR}/docker"):
    file = f"sonny_{dockerfile[:-11]}"
    result = subprocess.run(
        ["docker", "images", "-q", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    if bool(result.stdout.strip()):
        logger.logger.log(10, f"Skipped building {file}, as it already exists")
        continue
    result = subprocess.run(
        ["docker", "build", "-f", f"{DIR}/docker/{dockerfile}", "-t", file, "."],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    logger.logger.log(10, result.stdout)
