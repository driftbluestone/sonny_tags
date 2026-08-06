"""
Edits a tag, if the tag is not found, it is created\n
If override is enabled, it will ignore whether the user owns the tag or not.
"""
from discord.ext import commands
from psycopg import sql
from db import db
from ..strong_tag_data import *
from . import add
from .. import tag_utils

@CallableModule
async def edit(ctx: commands.Context, message: list[str], override: bool = False):
    if not await tag_utils.check_creation_permission(ctx):
        return
    tag: str = message[0].strip().lower()
    message = f"{" ".join(message[1:])}\n{" ".join([attatchment.url for attatchment in ctx.message.attachments])}".strip()
    if not tag:
        return await ctx.reply(":information_source: %t edit `name` `new body`")

    owner = tag_utils.get_tag_owner(tag)
    if owner is None:
        return await add(ctx, message)
    
    # Guardrails to prevent overwriting a tag you do not own.
    if not (override or ctx.author.id == owner):
        return await ctx.reply(f":warning: Tag **{tag}** is owned by <@{owner}>")

    if not message:
        return await ctx.reply(f":warning: Tag body cannot be empty.")

    size = tag_utils.tag_size(tag)
    query = sql.SQL("""UPDATE {schema}.sonny_tags$users
    SET tags = array_append(tags, {tag}),
    space = space - {tag_size}
    WHERE user_id = {user_id}""").format(
        schema = db.SCHEMA,
        tag = sql.Placeholder(),
        tag_size = sql.Placeholder(),
        user_id = sql.Placeholder()
    )
    db.run(query, (tag, size, owner))

    if not await tag_utils.create_tag(ctx.author.id, tag, message):
        return await ctx.reply(f":warning: Cannot create tag, you are out of storage.")
    return await ctx.reply(f":white_check_mark: Edited tag **{tag}**")