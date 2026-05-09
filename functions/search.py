"""
Outputs tag_utils.search to Discord
"""
from discord.ext import commands
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_search(ctx: commands.Context, message: list):
    
    search = message[0]
    if not search: return await ctx.reply(":information_source: %t search `query`")
    try: amount = int(message[1])
    except: amount = 5
    out = await tag_utils.search(message[0], amount)
    await ctx.reply(f":information_source: {out}")