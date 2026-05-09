"""
Gives a user the tag_admin permission
"""
from discord.ext import commands
from ..strong_tag_data import *
from api import users

@CallableModule
async def admin_promote(ctx: commands.Context, message: str):
    
    user = message[0]
    if user == "":
        return await ctx.reply(":information_source: %t admin promote `user`")
    user, _ = await users.resolve_user(user)
    if not user:
        return await ctx.reply(":warning: Couldn't find user.")
    msg = ":white_check_mark: Sucessfully "
    if user["permissions"]["tag_admin"]:
        msg += "demoted"
        user["permissions"]["tag_admin"] = False
    else:
        msg += "promoted"
        user["permissions"]["tag_admin"] = True
    users.set_permission(user["id"], "admin", )
    return await ctx.reply(f"{msg} <@{user["id"]}>.")