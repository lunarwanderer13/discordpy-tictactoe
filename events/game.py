import discord
from discord.ext import commands

from tictactoe import game

class Challenge(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot:
            return

        message_content: str = message.content.lower().strip().replace(",", "").replace(".", "").replace("!", "").replace("?", "").replace("-", " ")
    
        if "reset" in message_content and message.author.id == 489418032368713728:
            game.reset_game()
            await message.add_reaction("✅")
            return

        if message_content[message_content.find("i challenge you"):] == "i challenge you to a game of tic tac toe" \
           or message_content[message_content.find("how about"):] == "how about a game of tic tac toe" \
           or message_content[message_content.find("how about"):] == "how about a round of gwent":
            if game.active:
                await message.add_reaction("❌")
                return
            else:
                try:
                    challenge_author: discord.User | discord.Member = message.author
                    challenged_user: discord.User | discord.Member = await message.guild.fetch_member(int(message_content[message_content.find("<@")+2:message_content.find(">")]))

                    if challenge_author.id == challenged_user.id:
                        await message.add_reaction("❌")
                        return

                    await game.start_game(challenge_author, challenged_user, message.channel)
                    return
                except ValueError:
                    await message.add_reaction("❌")

        if game.channel and message.channel.id != game.channel.id:
            return

        if game.active:
            if game.phase == "coin":
                if "head" in message_content and not "tail" in message_content:
                    await game.flip_coin("heads")
                elif "tail" in message_content and not "head" in message_content:
                    await game.flip_coin("tails")
                else:
                    await message.channel.send(f"We both know very well that *\"{message_content}\"* ain't an option.")

            if game.phase == "pregame":
                await message.channel.send("Select position (a1, b2, etc.)")
                await game.send_board()
                game.phase = "game"
                return

            if game.phase == "game":
                if message_content not in ["a1", "a2", "a3",
                                           "b1", "b2", "b3",
                                           "c1", "c2", "c3"]:
                    return

                if (game.turn == 1 and game.game_author and message.author.id == game.game_author.id) \
                   or (game.turn == 2 and game.opponent and message.author.id == game.opponent.id):
                    try:
                        game.set_cell(message_content)
                        await game.end_turn()
                    except Exception:
                        await message.add_reaction("❌")
                else:
                    await message.add_reaction("❌")
                
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Challenge(bot))
