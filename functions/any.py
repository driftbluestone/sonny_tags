from db import db
from discord.ext import commands
from psycopg import sql
from .. import tags
from ..strong_tag_data import *


@CallableModule
async def tag_any(ctx: commands.Context, message: list):
    q = sql.SQL("SELECT * FROM sonny_tags$tags ORDER BY RANDOM() LIMIT 1;")
    await tags.get_tag(ctx, db.single(q)[0], [""])
