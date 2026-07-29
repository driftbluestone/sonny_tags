from discord.ext import commands
from db import db
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_quota(ctx: commands.Context, message: list[str]):
    space = db.get("sonny_tags$users", (ctx.author.id,), ("user_id",), ("space",))
    if space is None:
        space = 0
    KiB = space / 1024
    percent = 100 * (space / 1048576)
    return await ctx.reply(f":information_source: Using {KiB:.2f}/1024 KiB ({percent:.2f}%)")