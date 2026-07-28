"""
Ban users from creating tags, viewing tags, and using sed
"""
from discord.ext import commands
from api import users, db
from ..strong_tag_data import *

@CallableModule
async def admin_ban(ctx: commands.Context, message: list[str]):
    user = message[0]
    type = message[1]
    if (user == "") or (type == "") or (type not in ["add", "view"]):
        return await ctx.reply(":information_source: %t admin ban `user` `add|view`")
    user, _ = await users.resolve_user(user)
    if not user:
        return await ctx.reply(":warning: Couldn't find user.")\
    
    if type == "add":
        type = "create"
    
    ban = ""
    banned, = db.get("permissions", (ctx.guild.id, user.id, type), ("server_id", "user_id", "type"), ("value",))
    db.insert("permissions", ("server_id", "user_id", "type"), ("value",), (ctx.guild.id, user.id, type, not banned))
    if not banned:
        ban = "un"
    return await ctx.reply(f":white_check_mark: <@{user["id"]}> {ban}banned.")