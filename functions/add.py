"""
Creates a tag while having safeguards to prevent overwriting
"""
import random
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent.parent / "data/extensions/sonny_tags/tags"

@CallableModule
async def tag_add(ctx: commands.Context, message: list):
    if not await tag_utils.check_creation_permission(ctx):
        return
    tag = message[0].lower().strip()
    if not tag:
        return await ctx.reply(":information_source: %t add `name` `body`")
    if random.randint(1, 100) == 100:
        return await ctx.reply("no")

    user_id = str(ctx.author.id)
    
    message = f"{" ".join(message[1:])}\n{" ".join([attatchment.url for attatchment in ctx.message.attachments])}".strip()
    
    if tag in SPECIAL_TAGS or tag == "admin":
        return await ctx.reply(":warning: That tag is reserved.")
    data, _, exists, _ = await tag_utils.get_tag_data(user_id, tag)
    if exists:
        return await ctx.reply(f":warning: Tag {tag} already exists and is owned by <@{data["owner"]}>")
    if any(char not in VALID_NAME_CHARS for char in tag):
        return await ctx.reply(f":warning: Tag name must consist of characters a-z, 0-9, _, or -. ")
    sucess = await tag_utils.create_tag(user_id, tag, message, f"{DIR}/{tag}.json")
    if not sucess:
        return await ctx.reply(f":warning: Tag body cannot be empty.")
    return await ctx.reply(f":white_check_mark: Created tag **{tag}**")