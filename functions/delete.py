"""
Deletes a tag \n
Using override will make it ignore the owner \n
Using silent will stop it from sending a message
"""
import os
from discord.ext import commands
from api import users
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_delete(ctx: commands.Context, tag: list, override: bool = False, silent: bool = False):
    tag = tag[0]
    if not tag:
        return await ctx.reply(":information_source: %t delete `tag`")

    user_id = str(ctx.author.id)
    data, filepath, exists, owned = await tag_utils.get_tag_data(user_id, tag)
    if not exists:
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    if not (owned or override):
        return await ctx.reply(f":warning: Tag **{tag}** is owned by <@{data["owner"]}>")

    # If the tag is not an alias itself, remove all aliases it has
    deleted_aliases = ""
    if data["type"] != "alias":
        aliases = data["aliases"]
        for alias in aliases:
            deleted_aliases = " and surrounding aliases"
            await tag_delete(ctx, alias, True, True)
    # If the tag is an alias, remove it from the parent tag
    else:
        alias_of, alias_filepath, _, _ = await tag_utils.get_tag_data(ctx, data["alias_of"])
        alias_of["aliases"].remove(tag)
        with open(alias_filepath, "w") as file:
            json.dump(alias_of, file)
    
    # Remove other files from other tag types
    if data["type"] == "code":
        os.remove(f"{filepath[:-5]}.{data["lang"]}")
    if data["type"] == "plaintext":
        os.remove(f"{filepath[:-5]}.txt")
    os.remove(filepath)

    # Save the data
    user = users.get(int(data["owner"]))
    user["sonny_tags:tags"].remove(tag)
    users.set_field(user["id"], "sonny_tags:tags", user["sonny_tags:tags"])

    if not silent:
        return await ctx.reply(f":white_check_mark: Tag **{tag}**{deleted_aliases} deleted.")