"""
Edits a tag, if the tag is not found, it is created\n
If override is enabled, it will ignore whether the user owns the tag or not.
"""
import os
from discord.ext import commands
from ..strong_tag_data import *
from . import add
from .. import tag_utils

@CallableModule
async def edit(ctx: commands.Context, message: list, override: bool = False):
    if not await tag_utils.check_creation_permission(ctx): return
    tag: str = message[0].strip().lower()
    message = message = f"{" ".join(message[1:])}\n{" ".join([attatchment.url for attatchment in ctx.message.attachments])}".strip()
    if not tag: return await ctx.reply(":information_source: %t edit `name` `new body`")

    # Guiderails to prevent overwriting a tag you do not own.
    user_id = str(ctx.author.id)

    data, filepath, exists, owned = await tag_utils.get_tag_data(user_id, tag)
    if not exists:
        return await add(ctx, message)
    if not (owned or override):
        return await ctx.reply(f":warning: Tag **{tag}** is owned by <@{data["owner"]}>")
    if override:
        user_id = data["owner"]

    # Remove the other files in case of a type change
    if data["type"] == "code":
        os.remove(f"{filepath[:-5]}.{data["lang"]}")
    if data["type"] == "plaintext":
        os.remove(f"{filepath[:-5]}.txt")

    sucess = await tag_utils.create_tag(user_id, tag, message, filepath)
    if not sucess: return await ctx.reply(f":warning: Tag body cannot be empty.")
    return await ctx.reply(f":white_check_mark: Edited tag **{tag}**")