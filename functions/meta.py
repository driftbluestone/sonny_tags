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

    return await ctx.reply(f":information_source: Metadata for tag {tag}:\nname: {data[0]}\nowner: <@{data[1]}>\ntype: {data[2]}\naliases: {data[4]}\nargs (code tags only): {data[5]}")