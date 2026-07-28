from discord.ext import commands
from api import db
from .. import tag_utils
from ..strong_tag_data import *

@CallableModule
async def admin_hide(ctx: commands.Context, message: list[str]):
    tag = message[0]
    if not tag:
        return await ctx.reply(":information_source: %t admin hide `tag`")
    hidden = tag_utils.hidden(ctx.guild.id, tag)
    if hidden:
        db.delete("sonny_tags$hidden_tags", ("server_id", "tag"), (ctx.author.id))
        return await ctx.reply(f":white_check_mark: Unbanned tag **{tag}**")
    db.insert("sonny_tags$hidden_tags", ("server_id", "tag"), (), (ctx.author.id))
    return await ctx.reply(f":white_check_mark: Banned tag **{tag}**")