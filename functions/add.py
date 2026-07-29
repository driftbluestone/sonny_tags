"""
Creates a tag while having safeguards to prevent overwriting
"""
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent.parent / "data/extensions/sonny_tags/tags"

@CallableModule
async def tag_add(ctx: commands.Context, message: list[str]):
    if not await tag_utils.check_creation_permission(ctx):
        return
    tag = message[0].lower().strip()
    if not tag:
        return await ctx.reply(":information_source: %t add `name` `body`")

    message = f"{" ".join(message[1:])}\n{" ".join([attatchment.url for attatchment in ctx.message.attachments])}".strip()
    
    if tag in SPECIAL_TAGS or tag == "admin":
        return await ctx.reply(":warning: That tag is reserved.")
    
    owner = tag_utils.get_tag_owner(tag)
    if owner:
        return await ctx.reply(f":warning: Tag {tag} already exists and is owned by <@{owner}>")
    
    tag = tag.split("\n")[0]
    if any(char not in VALID_NAME_CHARS for char in tag):
        return await ctx.reply(f":warning: Tag name must consist of characters a-z, 0-9, _, or -. ")
    
    if not message:
        return await ctx.reply(f":warning: Tag body cannot be empty.")
    if not await tag_utils.create_tag(ctx.author.id, tag, message):
        return await ctx.reply(f":warning: Cannot create tag, you are out of storage.")
    return await ctx.reply(f":white_check_mark: Created tag **{tag}**")