import json, re, heapq
from Levenshtein import ratio
from discord.ext import commands
from os import listdir
from api import users, config
from pathlib import Path
tag_config = config.get()
DIR = Path(__file__).resolve().parent.parent.parent

async def get_tag_data(user_id: str, tag: str):
    """
    Returns tag metadeta, the filepath to the tag, if the tag exists or not, and if the user owns the tag, as a list
    """
    filepath = f"{DIR}/data/extensions/sonny_tags/tags/{tag}.json"
    if not Path(filepath).exists():
        return [None, filepath, False, False]

    with open(filepath, "r") as file:
        data = json.load(file)
    if data["owner"] == user_id:
        owned = True
    else: owned = False
    return [data, filepath, True, owned]

async def check_creation_permission(ctx: commands.Context):
    ban = await users.has_permission(ctx.author.id, "sonny_tags:create")
    if not ban:
        await ctx.reply(":warning: You are banned from creating tags.")
        return False
    admin = users.has_permission(ctx.author.id, "sonny_tags:admin")
    if tag_config["limit_creation_to_admins"] and (not admin):
        await ctx.reply(":information_source: Only admins can add tags")
        return False
    return True

async def create_tag(user_id: str, name: str, body: str, filepath: str) -> bool:
    """
    Creates a tag. Returns a bool based on success
    """
    if body == "": return False

    # message tags
    if re.match(r"https:\/\/discord\.com\/channels\/\d+\/\d+\/\d+", body):
        tag = {"name":name,"type":"message","aliases":[],"message_link":body, "owner":user_id}
        with open(filepath, "w") as file:
            json.dump(tag, file)

    # code tags
    elif body.startswith("```") and body.endswith("```"):
        body = body[3:-3]
        if body.startswith("py"):
            body = body[2:]
        if body.startswith("thon"):
            body = body[4:]
        tag = {"name":name,"type":"code","aliases":[],"owner":user_id}
        with open(filepath, "w") as file:
            json.dump(tag, file)
        with open(f"{filepath[:-5]}.py", "w", encoding="utf-8") as file:
            file.write(body)

    # plaintext tags
    else:
        tag = {"name":name,"type":"plaintext","aliases":[],"owner":user_id}
        with open(filepath, "w") as file:
            json.dump(tag, file)
        with open(f"{filepath[:-5]}.txt", "w", encoding="utf-8") as file:
            file.write(body)

    user = users.get(user_id)
    if name not in user["tags"]:
        user["tags"].append(name)
        users.set_field(user_id, "tags", user["tags"])

    return True

async def search(query: str, amount: int) -> str:
    """
    Searches for any matching tags
    """
    tags = listdir(f"{DIR}/data/extensions/sonny_tags/tags")
    tags = [tag for tag in tags if tag.endswith(".json")]
    distances = {}
    for tag in tags:
        tag = tag[:-5]
        distance = ratio(tag, query)
        distances[tag] = distance
    closest_match = heapq.nlargest(amount, distances.items(), key=lambda item: item[1])
    out = ""
    for k, _ in closest_match:
        out += f"`{k}`, "
    return out[:-2]