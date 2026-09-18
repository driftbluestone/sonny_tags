import re
from discord.ext import commands
from psycopg import sql
from api import users, config, db
from utils import jsonIO
from utils.utils import DIR
tag_config = config.get()

languages = jsonIO.load(f"{DIR}/extensions/sonny_tags/code_tags/aliases.json")

def get_tag_data(tag: str) -> tuple[str, int, str, str, list | None, list | None] | None:
    """
    Returns ALL tag data or None if tag does not exist.
    
    Name, Owner, Type, Content, Aliases, Args (code tags only).
    """
    data = db.get("sonny_tags$tags", (tag,), ("name",), ("name", "owner", "type", "content", "aliases", "args"))

    if data is None:
        return data
    name, owner, type, content, aliases, args = data
    return name, int(owner), type, content, aliases, args

def get_tag_owner(tag: str) -> int | None:
    """Returns tag owner or None if the tag does not exist."""
    data = db.get("sonny_tags$tags", (tag,), ("name",), ("owner",))
    return data

def get_tag_type(tag: str) -> str | None:
    """Returns tag type or None if the tag does not exist."""
    data = db.get("sonny_tags$tags", (tag,), ("name",), ("type",))
    return data

async def check_creation_permission(ctx: commands.Context):
    ban = await users.has_permission(ctx.guild.id, ctx.author.id, "sonny_tags:create")
    if not ban:
        await ctx.reply(":warning: You are banned from creating tags.")
        return False
    
    admin = await users.has_permission(ctx.guild.id, ctx.author.id, "sonny_tags:admin")
    if tag_config["limit_creation_to_admins"] and (not admin):
        await ctx.reply(":information_source: Only admins can add tags")
        return False
    
    return True

async def create_tag(user_id: int, name: str, body: str):
    """Creates a tag."""
    space = db.get("sonny_tags$users", (user_id,), ("user_id",), ("space",))
    if space is not None and space >= 1024*1024:
        return False

    # get type
    if re.match(r"https:\/\/discord\.com\/channels\/\d+\/\d+\/\d+", body):
        tag_type = "message"
    elif body.startswith("```") and body.endswith("```"):
        tag_type = f"code:{languages[body[3:].split("\n")[0]]}"
    else:
        tag_type = "plaintext"

    # create additional args if code tag
    args = []
    if tag_type.startswith("code:"):
        body: str = "\n".join(body.split("\n")[1:-1])
        args = [arg for arg in body.split("\n")[0].split(" ")[1:] if arg in ["user", "channel", "role"]]
    insert_tag(name, user_id, tag_type, body, args)
    return True

def tag_size(name):
    # get size of tag
    query = sql.SQL("""SELECT pg_column_size(t)
        AS total_row_bytes
        FROM {schema}.sonny_tags$tags AS t
        WHERE name::text = {name};""").format(
            schema = db.SCHEMA,
            name = sql.Placeholder()
        )
    size = db.single(query, (name,))
    return size

def insert_tag(name: str, user_id: int, tag_type: str, body: str, args: list = []):
    # insert into database
    db.insert("sonny_tags$tags", ("name",), ("owner", "type", "content", "aliases", "args"), (name, user_id, tag_type, body, [], args))

    size = tag_size(name)

    # ensure user exists
    user = db.get("sonny_tags$users", (user_id,), ("user_id",), ("user_id",))
    if user is None:
        db.insert("sonny_tags$users", ("user_id",), ("tags", "space"), (user_id, [], 0))

    query = sql.SQL("""UPDATE {schema}.sonny_tags$users
        SET tags = array_append(tags, {tag}),
        space = space + {tag_size}
        WHERE user_id = {user_id}""").format(
            schema = db.SCHEMA,
            tag = sql.Placeholder(),
            tag_size = sql.Placeholder(),
            user_id = sql.Placeholder()
        )
    db.run(query, (name, size, user_id))

def hidden(server_id: int, tag: str) -> bool:
    hidden = db.get("sonny_tags$hidden_tags", (server_id, tag), ("server_id", "tag"), ("tag",),)
    if hidden is None:
        return False
    return True

async def search(query: str, amount: int) -> str:
    """
    Searches for any matching tags
    """
    db.run("SET pg_trgm.similarity_threshold = 0.5;")
    db_query = sql.SQL("""
        SELECT name from {schema}.sonny_tags$tags
        WHERE name %% {query}
        ORDER BY name <-> {query}
        LIMIT {amount};""").format(
            schema = db.SCHEMA,
            query = sql.Placeholder("query"),
            amount = sql.Placeholder("amount")
        )
    results = db.multiple(db_query, {"query": query, "amount": amount})
    if results is None:
        results = []
    results = [i for i, in results]
    return results