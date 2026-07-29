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
async def edit(ctx: commands.Context, message: list[str], override: bool = False):
    if not await tag_utils.check_creation_permission(ctx):
        return
    tag: str = message[0].strip().lower()
    message = f"{" ".join(message[1:])}\n{" ".join([attatchment.url for attatchment in ctx.message.attachments])}".strip()
    if not tag:
        return await ctx.reply(":information_source: %t edit `name` `new body`")

    # Guardrails to prevent overwriting a tag you do not own.
    owner = tag_utils.get_tag_owner(tag)
    if owner is None:
        return await add(ctx, message)
    if not (override or ctx.author.id == owner):
        return await ctx.reply(f":warning: Tag **{tag}** is owned by <@{owner}>")

    if not message:
        return await ctx.reply(f":warning: Tag body cannot be empty.")
    if not await tag_utils.create_tag(ctx.author.id, tag, message):
        return await ctx.reply(f":warning: Cannot create tag, you are out of storage.")
    return await ctx.reply(f":white_check_mark: Edited tag **{tag}**")