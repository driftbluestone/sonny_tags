import discord
from discord.ext import commands
from api import users, gui
from utils import jsonIO
from . import functions, admin_functions, container, tag_utils
from .strong_tag_data import *

async def context_formatter(ctx: commands.Context):
    message = ctx.message.content
    message = message.split(" ")
    if len(message) != 1:
        tag = message[1]
        message = message[2:]
    else:
        tag = None
    await get_tag(ctx, tag, message)

async def get_tag(ctx: commands.Context, tag: str, message: list[str]):
    if not await users.has_permission(ctx.guild.id, ctx.author.id, "sonny_tags:view"):
        return await ctx.reply(":warning: You have been banned from viewing tags.")
    if not tag:
        return await ctx.reply(f":information_source: %t `{"|".join(DISPLAYED_SPECIAL_TAGS)}`")
    tag = tag.lower()
    if tag in SPECIAL_TAGS:
        if not message: message = ["", ""]
        message[0].lower()
        action =  getattr(functions, tag)
        return await action(ctx, message)
    elif tag == "admin":
        if not message: message = ["", ""]
        return await admin_tag(ctx, message[0].lower(), message[1:])
    
    user_id = str(ctx.author.id)
    data = tag_utils.get_tag_data(user_id, tag)

    if data is None:
        content = f":warning: Tag **{tag}** not found"
        match = await tag_utils.search(tag, 5)
        if match:
            content += f", did you mean `{"`, `".join(match)}`?"
        else:
            content += "."
        return await ctx.reply(content)
    
    if tag_utils.hidden(ctx.guild.id, tag):
        return await ctx.reply(f":warning: Tag **{tag}** is banned in this server.")
    await parse_tag(ctx, data, message)



async def admin_tag(ctx: commands.Context, tag: str, message: list[str]):
    if not await users.has_permission(ctx.guild.id, ctx.author.id, "sonny_tags:admin"):
        return await ctx.reply(":warning: No permission.")
    if not message: message = ["", ""]
    tag = tag.lower()

    if (not tag) or (tag not in ADMIN_TAGS):
        return await ctx.reply(f":information_source: %t `{"|".join(DISPLAYED_ADMIN_TAGS)}`")
    
    if tag in ADMIN_TAGS and tag in SPECIAL_TAGS:
        if not await users.has_permission(ctx.guild.id, ctx.author.id, "sonny_tags:manage"):
            return await ctx.reply(":warning: No permission.")
        action =  getattr(functions, tag)
        return await action(ctx, message, True)
    
    action = getattr(admin_functions, tag)
    return await action(ctx, message, True)

async def parse_tag(ctx: commands.Context, data: tuple, message: list = []):
    """
    From tag data and filepath, will determine how to parse the tag
    """

    # Set a recursion limit for code tag calling
    setattr(ctx, "recursion", getattr(ctx, "recursion", 0)+1)
    if ctx.recursion >= 5:
        return await ctx.reply(":warning: Tag recursion limit reached.")
    
    name = data[0]
    tag = data[2]
    if ":" in tag:
        return await execute_code_tag(ctx, name, data, message)
    elif tag == "alias":
        return await get_tag(ctx, data[3], message)
    elif tag == "message":
        embed = await gui.create_message_embed(data[3])
        return await ctx.reply(embed=embed)
    embed, text = await json_parser(ctx, data[3])
    if not embed and not text: return
    return await ctx.reply(content=text, embed=embed)

async def json_parser(ctx: commands.Context, input: str):
    """
    Returns an embed, calls a tag, or returns plaintext. data is returned as discord.Embed, text
    """
    text = None
    try:
        json_input = jsonIO.loads(input)
        if not isinstance(json_input, dict):
            return None, input[:1995]
        if "call_tag" in json_input:
            await get_tag(ctx, json_input["call_tag"], json_input["args"] if "args" in json_input else [])
            return None, None
        elif "embed" in json_input:
            embed = await embed_builder(json_input["embed"])
        else:
            return None, input[:1995]
        if not isinstance(embed, discord.Embed):
            embed = discord.Embed(description=f"Error creating embed:\n{embed}")

    except jsonIO.JSONDecodeError:
        embed = None
        text = input[:1995]
    return embed, text

async def embed_builder(input: dict):
    """
    Creates an embed from a dictionary input
    """
    embed = discord.Embed()
    for k, v in input.items():
        try:
            if isinstance(v, dict):
                getattr(embed, k)(**v)
            else:
                setattr(embed, k, v) 
        except Exception as e:
            return str(e)  
    return embed

async def execute_code_tag(ctx: commands.Context, tag: str, data: tuple, message: list):
    output = await container.container(ctx, tag, data, message)
    embed, text = await json_parser(ctx, output)
    if embed is None and text is None:
        return
    if text == "":
        text = "[No output]"
    return await ctx.reply(content=text, embed=embed)
