from discord.ext import commands
from pathlib import Path
from . import tags
DIR = Path(__file__).parent.absolute()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tags(bot=bot))

class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="t", aliases=["tag"])
    async def t(self, ctx: commands.Context):
        await tags.context_formatter(ctx)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, (commands.ExpectedClosingQuoteError,
                              commands.InvalidEndOfQuotedStringError,
                              commands.UnexpectedQuoteError)):
            return await tags.context_formatter(ctx)