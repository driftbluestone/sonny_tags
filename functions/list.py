"""
this function is cursed.
"""
import os, discord, io
from discord.ext import commands
from ..strong_tag_data import *
from api import users
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent.parent

@CallableModule
async def tag_list(ctx: commands.Context, message: list):
    message = message[0]
    if message:
        user, _ = await users.resolve_user(message)
        if not user:
            return await ctx.reply(":warning: Couldn't find user.")
        tag_list = user["sonny_tags:tags"]
        tags = f"`{"`, `".join([x for x in tag_list])}`"
    else:
        tag_list = [x[:-5] for x in os.listdir(f"{DIR}/data/extensions/sonny_tags/tags") if x.endswith(".json")]
        tags = f"`{"`, `".join(tag_list)}`"
    tag_count = len(tag_list)
    if (not tag_list) and message:
        return await ctx.reply(f"User <@{user["id"]}> has no tags.")
    if not tag_list and not message:
        return await ctx.reply(f"No tags found.")
    if len(tags) >= 1900:
        file = discord.File(fp=io.StringIO(tags), filename="message.txt")
        if message:
            return await ctx.reply(f"**<@{user["id"]}>'s tags ({tag_count})**:", file=file)
        else:
            return await ctx.reply(f"**Tags in this server ({tag_count})**:", file=file)
    else:
        if message:
            return await ctx.reply(f"**<@{user["id"]}>'s tags ({tag_count})**:\n{tags}")
        else:
            return await ctx.reply(f"**Tags in this server ({tag_count})**:\n{tags}")