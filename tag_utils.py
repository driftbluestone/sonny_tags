import re, heapq, os, Levenshtein
from discord.ext import commands
from api import users, config
from pathlib import Path
from utils import jsonIO
from utils.utils import DIR
tag_config = config.get()

languages = jsonIO.load(f"{DIR}/extensions/sonny_tags/code_tags/aliases.json")

async def get_tag_data(user_id: str, tag: str):
    """
    Returns tag metadeta, the filepath to the tag, if the tag exists or not, and if the user owns the tag, as a list
    """
    filepath = f"{DIR}/data/extensions/sonny_tags/tags/{tag}.json"
    if not Path(filepath).exists():
        return [None, filepath, False, False]

    data = jsonIO.load(filepath)
    if data["owner"] == user_id:
        owned = True
    else: owned = False
    return [data, filepath, True, owned]

async def check_creation_permission(ctx: commands.Context):
    ban = await users.has_permission(ctx.author.id, "sonny_tags:create")
    if not ban:
        await ctx.reply(":warning: You are banned from creating tags.")
        return False
    admin = await users.has_permission(ctx.author.id, "sonny_tags:admin")
    if tag_config["limit_creation_to_admins"] and (not admin):
        await ctx.reply(":information_source: Only admins can add tags")
        return False
    return True

async def create_tag(user_id: str, name: str, body: str, filepath: str) -> bool:
    """
    Creates a tag. Returns a bool based on success
    """
    if not body:
        return False

    # message tags
    if re.match(r"https:\/\/discord\.com\/channels\/\d+\/\d+\/\d+", body):
        tag = {"name":name,"type":"message","aliases":[],"message_link":body, "owner":user_id}
        jsonIO.dump(filepath)

    # code tags
    elif body.startswith("```") and body.endswith("```"):
        lang = get_lang(body, name, user_id, filepath)
        if not lang:
            tag = {"name":name,"type":"plaintext","aliases":[],"owner":user_id}
            jsonIO.dump(filepath, tag)
            with open(f"{filepath[:-5]}.txt", "w", encoding="utf-8") as file:
                file.write(body)

    # plaintext tags
    else:
        tag = {"name":name,"type":"plaintext","aliases":[],"owner":user_id}
        jsonIO.dump(filepath, tag)
        with open(f"{filepath[:-5]}.txt", "w", encoding="utf-8") as file:
            file.write(body)

    user = users.get(user_id)
    if name not in user["sonny_tags:tags"]:
        user["sonny_tags:tags"].append(name)
        users.set_field(user_id, "sonny_tags:tags", user["sonny_tags:tags"])

    return True

def get_lang(body, name, user_id, filepath):
    body: str = body[3:-3]
    lines = body.split("\n")
    lang = lines[0]

    args = lines[1].split(" ")[1:]
    cleaned_args = []
    for arg in args:
        if arg in ["user", "channel", "role"]:
            cleaned_args.append(arg) 

    if lang not in languages:
        return False
    extension = languages[lang]
    body = body[len(lang):]
    tag = {"name": name,"type": "code", "aliases": [], "owner": user_id, "lang": extension, "args": cleaned_args}
    jsonIO.dump(filepath, tag)
    with open(f"{filepath[:-5]}.{extension}", "w", encoding="utf-8") as file:
        file.write(body)
    return True

async def search(query: str, amount: int) -> str:
    """
    Searches for any matching tags
    """
    tags = os.listdir(f"{DIR}/data/extensions/sonny_tags/tags")
    tags = [tag for tag in tags if tag.endswith(".json")]
    distances = {}
    for tag in tags:
        tag = tag[:-5]
        distance = Levenshtein.ratio(tag, query)
        distances[tag] = distance
    closest_match = heapq.nlargest(amount, distances.items(), key=lambda item: item[1])
    out = ""
    for k, _ in closest_match:
        out += f"`{k}`, "
    return out[:-2]