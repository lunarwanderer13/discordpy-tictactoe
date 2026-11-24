import discord
import discord.abc
import random
import pickle
from pathlib import Path

class TicTacToe:
    def __init__(self) -> None:
        self.active: bool = False
        self.phase: str | None = None
        self.board: list[list[int]] = [[0, 0, 0] for _ in range(3)]
        self.board_nums: list[list[int]] = [[0, 0, 0] for _ in range(2)]
        self.game_author: discord.User | discord.Member | None = None
        self.opponent: discord.User | discord.Member | None = None
        self.turn: int = 1
        self.turn_counter: int = 0
        self.channel: discord.abc.MessageableChannel | None = None

        self.scores: dict[str, list[int]] = {}
        self.load_scores()

    def load_scores(self) -> None:
        path = Path("scores.dat")

        if path.exists():
            with path.open("rb") as file:
                self.scores = pickle.load(file)

    def save_scores(self) -> None:
        with open("scores.dat", "wb") as file:
            pickle.dump(self.scores, file)

    def reset_game(self) -> None:
        self.active = False
        self.phase = None
        self.board = [[0, 0, 0] for _ in range(3)]
        self.board_nums = [[0, 0, 0] for _ in range(2)]
        self.game_author = None
        self.opponent = None
        self.turn = 1
        self.turn_counter = 0
        self.channel = None

    async def flip_coin(self, face: str) -> None:
        if not self.active or not self.channel or not self.game_author or not self.opponent:
            return

        coin: str = random.choice(["heads", "tails"])
        await self.channel.send(f"**{coin.capitalize()}!**")

        if face == coin:
            await self.channel.send(f"{self.opponent.mention} starts!")
            self.turn = 2
        else:
            await self.channel.send(f"{self.game_author.mention} starts!")
            self.turn = 1

        self.phase = "pregame"

    def get_cell(self, cell: str) -> str:
        row: int = ord(cell[0]) - ord("a")
        col: int = int(cell[1]) - 1

        value: int = self.board[row][col]
        
        match value:
            case 1:
                return "❌"
            case 2:
                return "⭕"
            case _:
                return "  "

    def set_cell(self, cell: str) -> None:
        if self.get_cell(cell) == "  ":
            row: int = ord(cell[0]) - ord("a")
            col: int = int(cell[1]) - 1

            self.board[row][col] = self.turn
            self.board_nums[0][row] += 1 if self.turn == 1 else -1
            self.board_nums[1][col] += 1 if self.turn == 1 else -1
        else:
            raise Exception

    async def send_board(self) -> None:
        if not self.channel:
            return

        response: str = ("```\n"
                         "  1  2  3\n"
                         f"a {self.get_cell("a1")} {self.get_cell("a2")} {self.get_cell("a3")}\n"
                         f"b {self.get_cell("b1")} {self.get_cell("b2")} {self.get_cell("b3")}\n"
                         f"c {self.get_cell("c1")} {self.get_cell("c2")} {self.get_cell("c3")}\n"
                         "```\n")

        await self.channel.send(response)

    async def end_turn(self) -> None:
        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 1

        self.turn_counter += 1
        await self.send_board()
        await self.check_board()

    async def end_game(self, result: str) -> None:
        if not self.channel:
            return

        await self.channel.send(result)
        self.save_scores()
        self.reset_game()

    async def check_board(self) -> None:
        if not self.game_author or not self.opponent:
            return

        if not self.scores.get(str(self.game_author.id)):
            self.scores[str(self.game_author.id)] = [0, 0]

        if not self.scores.get(str(self.opponent.id)):
            self.scores[str(self.opponent.id)] = [0, 0]

        if 3 in self.board_nums[0] or 3 in self.board_nums[1] \
           or (self.board[0][0] == 1 and self.board[1][1] == 1 and self.board[2][2] == 1) \
           or (self.board[0][2] == 1 and self.board[1][1] == 1 and self.board[2][0] == 1):
            self.scores[str(self.game_author.id)][0] += 1
            self.scores[str(self.opponent.id)][1] += 1
            await self.end_game(f"{self.game_author.mention} wins!")
        elif -3 in self.board_nums[0] or -3 in self.board_nums[1] \
           or (self.board[0][0] == 2 and self.board[1][1] == 2 and self.board[2][2] == 2) \
           or (self.board[0][2] == 2 and self.board[1][1] == 2 and self.board[2][0] == 2):
            self.scores[str(self.opponent.id)][0] += 1
            self.scores[str(self.game_author.id)][1] += 1
            await self.end_game(f"{self.opponent.mention} wins!")
        elif self.turn_counter >= 9:
            await self.end_game(f"Tie, nobody wins.")

    async def start_game(
        self, 
        player1: discord.User | discord.Member,
        player2: discord.User | discord.Member,
        channel: discord.abc.MessageableChannel
    ) -> None:
        self.active = True
        self.phase = "coin"
        self.game_author = player1
        self.opponent = player2
        self.channel = channel

        await channel.send(f"*{player1.mention} challenged {player2.mention}*")
        await channel.send(f"{player2.mention}, heads or tails?")

game = TicTacToe()
