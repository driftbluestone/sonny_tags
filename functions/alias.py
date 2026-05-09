"""
Creates an alias of another tag
"""
from discord.ext import commands
# from utils.users import get_user_profile, save_user_profile
from api import users
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_alias(ctx: commands.Context, message: list):
    
    can_create = await tag_utils.check_creation_permission(ctx)
    if not can_create: return

    new_tag: str = message[0]
    tag: str = message[1]
    if not new_tag: return await ctx.reply(":information_source: %t alias `new` `existing`")
    if not tag: return await ctx.reply(":warning: Please provide a tag to alias to.")
    print(message)
    user_id = str(ctx.author.id)
    data, filepath, exists, _ = await tag_utils.get_tag_data(user_id, tag)
    if not exists: return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    # If the tag is an alias, alias the new tag to the tag it's an alias of, as alias tags do not support being aliased
    if data["type"] == "alias":
        return await tag_alias(ctx, new_tag, data["alias_of"])

    with open(filepath, "w") as file:
        data["aliases"].append(new_tag)
        json.dump(data, file)
    new_data, new_filepath, exists, _  = await tag_utils.get_tag_data(ctx, new_tag)
    if exists: return await ctx.reply(f":warning: Tag {new_tag} already exists and is owned by <@{new_data["owner"]}>")

    new_data = {"name":new_tag,"type":"alias","alias_of":tag, "owner":str(ctx.author.id)}
    with open(new_filepath, "w") as file:
        json.dump(new_data, file)
    
    user = users.get(ctx.author.id)
    user["tags"].append(new_tag)
    users.set_field(user["id"], "tags", user["tags"])

    return await ctx.reply(f":white_check_mark: Aliased **{new_tag}** to **{tag}**.")