from discord.ext import commands

from tictactoe import game

class Scores(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def scores(self, ctx: commands.Context[commands.Bot]) -> None:
        game.load_scores()

        content: str = ""
        for key, value in sorted(game.scores.items(), key=lambda x: x[1][0], reverse=True):
            content += f"<@{key}> - {value[0]}:{value[1]}\n"

        await ctx.reply(content)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Scores(bot))
