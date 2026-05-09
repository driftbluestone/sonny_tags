"""
Returns the files for a tag
"""
import discord
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_raw(ctx: commands.Context, message: list):
    
    tag = message[0]
    if tag == "": return await ctx.reply(":information_source: %t raw `tag`")
    if tag in SPECIAL_TAGS or tag == "admin":
        return await ctx.reply(f"{tag} is a special tag.")
    data, filepath, exists, _ = await tag_utils.get_tag_data(ctx, tag)
    if not exists: return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    file = [discord.File(filepath)]
    if data["type"] == "code":
        file.append(discord.File(f"{filepath[:-5]}.py"))
    if data["type"] == "plaintext":
        file.append(discord.File(f"{filepath[:-5]}.txt"))
    return await ctx.reply(f":information_source: Raw data for **{tag}**.", files=file)