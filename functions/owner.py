"""
Get tag owner
"""
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_owner(ctx: commands.Context, message: list):
    tag: str = message[0]
    if not tag:
        return await ctx.reply(":information_source: %t owner `tag`")
    data = (await tag_utils.get_tag_data(ctx, tag))[0]
    if not data:
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    return await ctx.reply(f":information_source: Tag **{tag}** is owned by <@{data["owner"]}>.")