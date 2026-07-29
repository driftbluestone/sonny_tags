import discord, io
from discord.ext import commands
from ..strong_tag_data import *
from api import users, db
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent.parent

@CallableModule
async def tag_list(ctx: commands.Context, message: list):
    message = message[0]
    if message:
        _, user = await users.resolve_user(ctx.guild.id, message)
        if not user:
            return await ctx.reply(":warning: Couldn't find user.")
        tag_list = db.get("sonny_tags$users", (user.id,), ("user_id",), ("tags",))
        if tag_list is None:
            return await ctx.reply(f"User <@{user.id}> has no tags.")
        tags = f"`{"`, `".join([x for x in tag_list])}`"
    else:
        tag_list = db.multiple(f"SELECT name FROM {db.SCHEMA.as_string()}.sonny_tags$tags")
        if tag_list is None:
            return await ctx.reply(f"No tags found.")
        tags = f"`{"`, `".join([tag for tag, in tag_list])}`"
        
    tag_count = len(tag_list)
    if len(tags) >= 1900:
        file = discord.File(fp=io.StringIO(tags), filename="message.txt")
        if message:
            return await ctx.reply(f"**<@{user.id}>'s tags ({tag_count})**:", file=file)
        else:
            return await ctx.reply(f"**Tags in this server ({tag_count})**:", file=file)
    else:
        if message:
            return await ctx.reply(f"**<@{user.id}>'s tags ({tag_count})**:\n{tags}")
        else:
            return await ctx.reply(f"**Tags in this server ({tag_count})**:\n{tags}")