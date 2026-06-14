"""
Creates an alias of another tag
"""
from discord.ext import commands
# from utils.users import get_user_profile, save_user_profile
from api import users
from utils import jsonIO
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_alias(ctx: commands.Context, message: list):
    
    can_create = await tag_utils.check_creation_permission(ctx)
    if not can_create: return
    new_tag: str = message[0].lower()
    tag: str = message[1].lower()
    if not new_tag:
        return await ctx.reply(":information_source: %t alias `new` `existing`")
    if not tag:
        return await ctx.reply(":warning: Please provide a tag to alias to.")
    print(message)
    user_id = str(ctx.author.id)
    data, filepath, exists, _ = await tag_utils.get_tag_data(user_id, tag)
    if (not exists) and (tag not in SPECIAL_TAGS) and (tag != "admin"):
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    # If the tag is an alias, alias the new tag to the tag it's an alias of, as alias tags do not support being aliased
    if data["type"] == "alias":
        return await tag_alias(ctx, new_tag, data["alias_of"])

    data["aliases"].append(new_tag)
    jsonIO.dump(filepath, data)
    new_data, new_filepath, exists, _  = await tag_utils.get_tag_data(ctx, new_tag)
    if exists:
        return await ctx.reply(f":warning: Tag {new_tag} already exists and is owned by <@{new_data["owner"]}>")

    new_data = {"name":new_tag, "type":"alias", "alias_of":tag, "owner":str(ctx.author.id)}
    jsonIO.dump(new_filepath, new_data)
    
    user = users.get(ctx.author.id)
    user["sonny_tags:tags"].append(new_tag)
    users.set_field(user["id"], "sonny_tags:tags", user["sonny_tags:tags"])

    return await ctx.reply(f":white_check_mark: Aliased **{new_tag}** to **{tag}**.")