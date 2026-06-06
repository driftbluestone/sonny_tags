import discord, json, asyncio
from uuid import uuid4
from discord.ext import commands
from api import users
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent

with open(f"{DIR}/extensions/sonny_tags/code_tags/args.json", "r") as file:
    langargs: dict = json.load(file)

async def container(ctx: commands.Context, tag: str, data: dict, message: list) -> str:
    """Creates a docker container that will execute a code tag"""
    container_name = uuid4().hex

    # Create the args that are passed into the container
    args = await create_args(ctx, message, data["args"] if "args" in data else [])
    args = json.dumps(args)
    docargs = ['docker', 'run',
               '--name', container_name,
               '--memory', '512m',
               '--memory-swap', '512m',
               '--user', '1000:1000',
               '--pids-limit', '50',
               '--cap-drop', 'ALL',
               '--network', 'none',
               '--rm', '-v', f'{DIR}/data/extensions/sonny_tags/tags:/data/:ro',
               *langargs[data["lang"]], f'/data/{tag}.{data["lang"]}',  
               args
            ]
    try:
        result = await asyncio.create_subprocess_exec(
            *docargs,
            stdout=asyncio.subprocess.PIPE  , 
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(result.communicate(), timeout=5.0)
        output = stdout.decode()
    except asyncio.TimeoutError as e:
        # Force kill the container
        kill_proc = await asyncio.create_subprocess_exec(
            'docker', 'rm', '-f', container_name,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await kill_proc.wait()
        output = "[PROCESS KILLED: exceeded 5s timeout]"
    except Exception as e:
        output = str(e)
    return output

async def create_args(ctx: commands.Context, message: list, extended_args: list) -> dict:
    args = {}
    args["user"] = [ctx.author.id, ctx.author.name, ctx.author.global_name, ctx.author.nick, ctx.author.display_avatar.url]
    args["server"] = [ctx.guild.id, ctx.guild.name]
    args["channel"] = [ctx.channel.id, ctx.channel.name, ctx.channel.category.id, ctx.channel.category.name]
    # Message history
    args["message_history"] = []
    message_history = [message async for message in ctx.message.channel.history(limit=25)]
    for i in message_history:
        i: discord.Message
        args["message_history"].append([i.id, i.content, i.author.id, i.author.name, i.author.global_name, i.author.nick, ctx.author.avatar.url])
    # Message reference, if any
    if ctx.message.reference is not None:
        reference: discord.Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        args["reference"] = [reference.id, reference.author.id, reference.author.name, reference.author.global_name, i.author.nick, i.author.avatar.url]
    # User supplied arguments
    args["args"] = message
    for i, arg in enumerate(extended_args):
        if arg == "user":
            _, user = await users.resolve_user(args["args"][i])
            if user is False:
                additional_args = None
            else:
                additional_args = [user.id, user.name, user.global_name, user.nick, user.display_avatar.url]
        elif arg == "channel":
            try:
                channel: discord.TextChannel = await commands.TextChannelConverter().convert(ctx, args["args"][i])
                additional_args = [channel.id, channel.name, channel.category.id, channel.category.name]
            except commands.BadArgument:
                try:
                    channel: discord.VoiceChannel = await commands.VoiceChannelConverter().convert(ctx, args["args"][i])
                    additional_args = [channel.id, channel.name, channel.category.id, channel.category.name]
                except commands.BadArgument as e:
                    additional_args = str(e)
            
        elif arg == "role":
            try:
                role: discord.Role = await commands.RoleConverter().convert(ctx, args["args"][i])
                additional_args = [role.id, role.name, role._colour, role._secondary_colour, role._tertiary_colour, None if role.icon is None else role.icon.url, role.unicode_emoji]
            except commands.BadArgument as e:
                additional_args = str(e)
            
            
        if i < len(args["args"]):
            args["args"][i] = additional_args
    return args

    # <@&1512724635853127800> role
    # <#1440196612361162804> channel