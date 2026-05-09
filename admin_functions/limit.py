"""
Limit tag creation to admins
"""
from discord.ext import commands
from api import config
from ..tag_utils import tag_config
from ..strong_tag_data import *

@CallableModule
async def admin_limit(ctx: commands.Context, _):
    
    msg = ":white_check_mark: "
    if tag_config["limit_creation_to_admins"]:
        msg += "Only admins"
        tag_config["limit_creation_to_admins"] = False
    else:
        msg += "Any user"
        tag_config["limit_creation_to_admins"] = True
    await config.overwrite(tag_config)
    return await ctx.reply(f"{msg} can now create tags.")