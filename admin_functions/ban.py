"""
Ban users from creating tags, viewing tags, and using sed
"""
from discord.ext import commands
from api import users
from ..strong_tag_data import *

@CallableModule
async def admin_ban(ctx: commands.Context, message: list):
    user = message[0]
    type = message[1]
    if (user == "") or (type == "") or (type not in ["add", "view"]):
        return await ctx.reply(":information_source: %t admin ban `user` `add|view`")
    user, _ = await users.resolve_user(user)
    if not user:
        return await ctx.reply(":warning: Couldn't find user.")
    if type == "add":
        type = "create"
    elif type == "view":
        type = "view"
    ban = ""
    banned = users.toggle_permission(user["id"], type, user["permissions"][type])
    if not banned:
        ban = "un"
    return await ctx.reply(f":white_check_mark: <@{user["id"]}> {ban}banned.")