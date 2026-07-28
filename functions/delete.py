"""
Deletes a tag \n
Using override will make it ignore the owner \n
Using silent will stop it from sending a message
"""
from discord.ext import commands
from psycopg import sql
from api import db
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_delete(ctx: commands.Context, tag: list, override: bool = False, silent: bool = False):
    return await delete(ctx, tag, override, silent)

async def delete(ctx: commands.Context, tag: list, override: bool = False, silent: bool = False):
    tag = tag[0]
    if not tag:
        return await ctx.reply(":information_source: %t delete `tag`")

    data = tag_utils.get_tag_data(tag)
    if data is None:
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    tag, owner, type, _, aliases, _ = data
    if not (override or ctx.author.id == owner):
        return await ctx.reply(f":warning: Tag **{tag}** is owned by <@{owner}>")

    # If the tag is not an alias, remove all aliases it has
    deleted_aliases = ""
    if type != "alias":
        for alias in aliases:
            deleted_aliases = " and surrounding aliases"
            await delete(ctx, alias, True, True)
    # If the tag is an alias, remove it from the parent tag
    else:
        query = sql.SQL("UPDATE {schema}.sonny_tags$tags SET aliases = array_remove(aliases, {tag})").format(
            schema = db.SCHEMA, tag = sql.Placeholder())
        db.run(query, (tag,))
    
    # Remove tag from user profiles
    size = tag_utils.tag_size(tag)
    query = sql.SQL("""UPDATE {schema}.sonny_tags$users
    SET tags = array_remove(tags, {tag}),
    space = space - {size}
    WHERE user_id = {user_id};""").format(
        schema = db.SCHEMA,
        tag = sql.Placeholder(),
        size = sql.Placeholder(),
        user_id = sql.Placeholder()
    )
    db.run(query, (tag, size, owner))

    # Remove tag from database
    db.delete("sonny_tags$tags", ("name",), (tag,))

    if not silent:
        return await ctx.reply(f":white_check_mark: Tag **{tag}**{deleted_aliases} deleted.")