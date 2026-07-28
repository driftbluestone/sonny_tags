"""
Creates an alias of another tag
"""
from discord.ext import commands
from psycopg import sql
from api import users, db
from ..strong_tag_data import *
from .. import tag_utils

@CallableModule
async def tag_alias(ctx: commands.Context, message: list[str]):
    if not await tag_utils.check_creation_permission(ctx):
        return
    
    new_tag: str = message[0].lower()
    tag: str = message[1].lower()

    if not new_tag:
        return await ctx.reply(":information_source: %t alias `new` `existing`")
    if not tag:
        return await ctx.reply(":warning: Please provide a tag to alias to.")

    type = tag_utils.get_tag_type(tag)
    if (not type) and (tag not in SPECIAL_TAGS) and (tag != "admin"):
        return await ctx.reply(f":warning: Tag **{tag}** does not exist.")
    
    # If the tag is an alias, alias the new tag to the tag it's an alias of
    if type == "alias":
        return await tag_alias(ctx, [new_tag, tag_utils.get_tag_data(tag)[3]])

    owner = tag_utils.get_tag_owner(new_tag)
    if owner:
        return await ctx.reply(f":warning: Tag {new_tag} already exists and is owned by <@{owner}>")
    
    query = sql.SQL("UPDATE {schema}.sonny_tags$tags SET aliases = array_append(aliases, '{new_tag}') WHERE name = {tag}").format(
        schema = db.SCHEMA,
        new_tag = sql.Placeholder(),
        tag = sql.Placeholder()
    )
    db.run(query (new_tag, tag))

    tag_utils.insert_tag(new_tag, ctx.author.id, "alias", tag)

    return await ctx.reply(f":white_check_mark: Aliased **{new_tag}** to **{tag}**.")