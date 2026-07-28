import os, subprocess, asyncio
from api import config, permission, db
from utils.logger import Logger
logger = Logger()
from pathlib import Path
DIR = Path(__file__).resolve().parent
DATA_DIR = config.datadir()

permission.create("view", "View Tags", True, True)
permission.create("create", "Create Tags", True, True)
permission.create("admin", "Tag Admin", True, False)
permission.create("manage", "Manage Tags", False, False)
config.create_field("limit_creation_to_admins", False)
if not os.path.exists(DATA_DIR / "tags"):
    os.mkdir(DATA_DIR)

db.table("tags", ["name TEXT PRIMARY KEY",
                  "owner BIGINT",
                  "type TEXT",
                  "content TEXT",
                  "aliases TEXT[] DEFAULT NULL",
                  "args TEXT[] DEFAULT NULL"
                ])

db.table("users", ["user_id BIGINT PRIMARY KEY",
                   "tags TEXT[]",
                   "space INT"])

db.table("hidden_tags", ["server_id BIGINT",
                         "tag TEXT",
                         "PRIMARY KEY (server_id, tag)"])

db.run("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

def build_images():
    for dockerfile in os.listdir(f"{DIR}/docker"):
        file = f"sonny_{dockerfile[:-11]}"
        result = subprocess.run(
            ["docker", "images", "-q", file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if bool(result.stdout.strip()):
            logger._logger.log(10, f"Skipped building {file}, as it already exists")
            continue
        result = subprocess.run(
            ["docker", "build", "-f", f"{DIR}/docker/{dockerfile}", "-t", file, "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        logger._logger.log(10, result.stdout)
asyncio.to_thread(build_images)