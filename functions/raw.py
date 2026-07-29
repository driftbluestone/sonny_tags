"""
Returns the files for a tag
"""
import discord, io
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_raw(ctx: commands.Context, message: list):
    
    tag = message[0]
    if tag == "": return await ctx.reply(":information_source: %t raw `tag`")
    if tag in SPECIAL_TAGS or tag == "admin":
        if tag == "raw":
            return await ctx.reply("why dont you raw some bitches")
        elif tag == "search":
            return await ctx.reply("why dont you search for some bitches")
        elif tag == "owner":
            return await ctx.reply("why dont you own some bitches")
        return await ctx.reply(f"{tag} is a special tag.")
    data = tag_utils.get_tag_data(tag)
    if data is None:
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")

    if data[2] == "message":
        return await ctx.reply(f":information_source: Tag **{tag}** is a message tag for message {data[3]}")
    elif data[2] == "alias":
        return await ctx.reply(f":information_source: Tag **{tag}** is an alias of {data[3]}")
    elif data[2] == "plaintext":
        file = discord.File(fp=io.StringIO(data[3]), filename=f"{tag}.txt")
        return await ctx.reply(f":information_source: Raw data for **{tag}**", file=file)
    elif data[2].startswith("code:"):
        extension = data[2][5:]
        file = discord.File(fp=io.StringIO(data[3]), filename=f"{tag}.{extension}")
        return await ctx.reply(f":information_source: Raw data for **{tag}**", file=file)