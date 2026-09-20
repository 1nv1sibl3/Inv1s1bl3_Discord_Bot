import asyncio
import logging
import random
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.bot.utils.formatting import format_currency
from src.bot.utils.api_clients import get_joke, get_bored_activity, get_truth_or_dare
from src.bot.games.gaw import gaw_manager
from src.database.session import get_db_session
from src.database import crud

logger = logging.getLogger("inv1s1bl3.cogs.games")

HANGMAN_STAGES = [
    """
    +---+
    |   |
        |
        |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
        |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
    |   |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|   |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
   /    |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
   / \\  |
        |
    =========
    """,
]

EIGHT_BALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]


class RPSView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def _handle_choice(self, interaction: discord.Interaction, player_choice: str):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original challenger can play!", ephemeral=True)
            return

        choices = ["rock", "paper", "scissors"]
        emojis = {"rock": "🪨 Rock", "paper": "📄 Paper", "scissors": "✂️ Scissors"}
        bot_choice = random.choice(choices)

        if player_choice == bot_choice:
            result = "It's a draw! 🤝"
        elif (
            (player_choice == "rock" and bot_choice == "scissors")
            or (player_choice == "paper" and bot_choice == "rock")
            or (player_choice == "scissors" and bot_choice == "paper")
        ):
            result = "You win! 🎉"
        else:
            result = "I win! 🤖"

        embed = branded_embed(
            title=f"Rock Paper Scissors: {result}",
            description=(
                f"You chose: **{emojis[player_choice]}**\n"
                f"I chose: **{emojis[bot_choice]}**"
            ),
        )
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.secondary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_choice(interaction, "rock")

    @discord.ui.button(label="Paper", emoji="📄", style=discord.ButtonStyle.secondary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_choice(interaction, "paper")

    @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.secondary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_choice(interaction, "scissors")


class Games(commands.Cog, name="Games & Social"):
    """Community parlor games, word puzzles, and trivia."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener for counting game channels."""
        if message.author.bot or not message.guild:
            return

        text = message.content.strip()
        if not text.isdigit():
            return

        number = int(text)
        async with get_db_session() as session:
            game = await crud.countgame.get_count_game(session, message.guild.id, message.channel.id)
            if game is None:
                return

            ok, count, reason = await crud.countgame.process_count(
                session, message.guild.id, message.channel.id, message.author.id, number
            )

        if ok:
            try:
                await message.add_reaction("✅")
            except Exception:
                pass
        else:
            try:
                await message.add_reaction("❌")
            except Exception:
                pass

            if reason == "consecutive":
                await message.channel.send(
                    f"❌ **{message.author.display_name}** counted twice in a row! Count reset to `0`."
                )
            elif reason == "wrong_number":
                await message.channel.send(
                    f"❌ **{message.author.display_name}** broke the sequence! Expected `{count + 1}`, got `{number}`. Count reset to `0`."
                )

    @commands.hybrid_command(name="rps", brief="Play Rock Paper Scissors against the bot.")
    async def rock_paper_scissors(self, ctx: commands.Context):
        embed = branded_embed(
            title="✂️ Rock Paper Scissors",
            description="Choose your move below:",
        )
        view = RPSView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="eightball", aliases=["8ball"], brief="Ask the mystical 8-ball a question.")
    @app_commands.describe(question="Your question for the 8-ball")
    async def eightball(self, ctx: commands.Context, *, question: str):
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = branded_embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {response}",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="joke", brief="Tell a funny joke.")
    async def tell_joke(self, ctx: commands.Context):
        joke = await get_joke()
        embed = branded_embed(
            title="😂 Joke Time",
            description=f"**{joke['setup']}**\n\n||{joke['punchline']}||",
            footer="Click spoiler to reveal punchline",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bored", brief="Get an activity idea when you are bored.")
    async def bored_activity(self, ctx: commands.Context):
        act = await get_bored_activity()
        embed = branded_embed(
            title="🎯 Activity Suggestion",
            description=f"**{act['activity']}**",
        )
        embed.add_field(name="Category", value=act["type"].capitalize(), inline=True)
        embed.add_field(name="Participants", value=act["participants"], inline=True)
        embed.add_field(name="Price Level", value=act["price"], inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="truthordare", aliases=["tod"], brief="Get a Truth or Dare prompt.")
    @app_commands.describe(kind="Select 'truth' or 'dare'")
    async def truth_or_dare(self, ctx: commands.Context, kind: Literal["truth", "dare"] = "truth"):
        prompt = await get_truth_or_dare(kind)
        emoji = "😇" if kind == "truth" else "😈"
        embed = branded_embed(
            title=f"{emoji} {kind.capitalize()}",
            description=prompt,
            footer=f"Requested by {ctx.author.display_name}",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="riddle", brief="Answer a brain-teaser riddle.")
    async def riddle(self, ctx: commands.Context):
        riddles = [
            ("What has to be broken before you can use it?", "egg"),
            ("I’m tall when I’m young, and I’m short when I’m old. What am I?", "candle"),
            ("What month of the year has 28 days?", "all"),
            ("What is full of holes but still holds water?", "sponge"),
            ("What is always in front of you but can’t be seen?", "future"),
        ]
        q, answer = random.choice(riddles)
        embed = branded_embed(
            title="🧩 Riddle",
            description=f"**{q}**\n\nYou have 30 seconds to answer in chat!",
        )
        await ctx.send(embed=embed)

        def check(m: discord.Message) -> bool:
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            if answer in msg.content.lower():
                await ctx.send(embed=success_embed("Riddle Solved!", f"Spot on, {ctx.author.mention}! The answer was **{answer}**."))
            else:
                await ctx.send(embed=error_embed("Incorrect", f"Not quite! The answer was **{answer}**."))
        except asyncio.TimeoutError:
            await ctx.send(embed=info_embed("Time's Up!", f"Time expired! The answer was **{answer}**."))

    @commands.hybrid_command(name="unscramble", brief="Unscramble the jumbled word.")
    async def unscramble(self, ctx: commands.Context):
        words = ["python", "discord", "developer", "algorithm", "database", "security", "framework", "keyboard"]
        word = random.choice(words)
        scrambled = list(word)
        random.shuffle(scrambled)
        if "".join(scrambled) == word:
            random.shuffle(scrambled)

        embed = branded_embed(
            title="🔤 Word Unscramble",
            description=f"Unscramble this word: **{' '.join(scrambled).upper()}**\n\nYou have 30 seconds!",
        )
        await ctx.send(embed=embed)

        def check(m: discord.Message) -> bool:
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            if msg.content.lower().strip() == word:
                await ctx.send(embed=success_embed("Correct!", f"Well done {ctx.author.mention}! The word was **{word}**."))
            else:
                await ctx.send(embed=error_embed("Incorrect", f"Nice try! The word was **{word}**."))
        except asyncio.TimeoutError:
            await ctx.send(embed=info_embed("Time's Up!", f"Time expired! The word was **{word}**."))

    @commands.hybrid_command(name="ecogame", brief="Bet your iCoin on a single dice roll.")
    @app_commands.describe(bet="Amount of coins to wager")
    async def ecogame(self, ctx: commands.Context, bet: int):
        if bet <= 0:
            await ctx.send(embed=error_embed("Invalid Bet", "Bet amount must be greater than zero."))
            return

        async with get_db_session() as session:
            bal = await crud.economy.get_balance(session, ctx.author.id)
            if bal["wallet"] < bet:
                await ctx.send(embed=error_embed("Insufficient Wallet Funds", f"You only have **{format_currency(bal['wallet'])}** in your wallet."))
                return

            roll = random.randint(1, 6)
            won = roll > 3

            account = await crud.economy.get_or_create_account(session, ctx.author.id)
            if won:
                account.wallet += bet
                outcome = f"🎲 You rolled a **{roll}** (> 3)! You won **+{format_currency(bet)}**!"
                embed = success_embed("You Won!", outcome)
            else:
                account.wallet -= bet
                outcome = f"🎲 You rolled a **{roll}** (<= 3). You lost **-{format_currency(bet)}**."
                embed = error_embed("You Lost", outcome)

            await session.commit()

        await ctx.send(embed=embed)

    # Guess A Word commands
    @commands.hybrid_group(name="gaw", brief="Play Guess A Word (GAW) in this channel.")
    async def gaw_group(self, ctx: commands.Context):
        embed = branded_embed(
            title="🎮 Guess A Word (GAW)",
            description=(
                f"Commands:\n"
                f"• `{ctx.prefix}gaw start` — Start a new word game in this channel\n"
                f"• `{ctx.prefix}gaw guess <word/letter>` — Guess a word or letter\n"
                f"• `{ctx.prefix}gaw end` — Terminate active game"
            ),
        )
        await ctx.send(embed=embed)

    @gaw_group.command(name="start", brief="Start a Guess A Word game session.")
    async def gaw_start(self, ctx: commands.Context):
        existing = gaw_manager.get_game(ctx.channel.id)
        if existing:
            await ctx.send(embed=info_embed("Game Active", f"A game is already underway! Progress: `{existing.mask}`"))
            return

        game = gaw_manager.start_game(ctx.channel.id)
        embed = success_embed(
            "New Game Commenced!",
            f"**Category:** `{game.category}`\n**Word:** `{game.mask}` ({len(game.word)} letters)\n"
            f"Use `{ctx.prefix}gaw guess <text>` to guess!",
        )
        await ctx.send(embed=embed)

    @gaw_group.command(name="guess", brief="Guess a letter or full word for GAW.")
    @app_commands.describe(guess="The letter or full word guess")
    async def gaw_guess(self, ctx: commands.Context, *, guess: str):
        game = gaw_manager.get_game(ctx.channel.id)
        if not game:
            await ctx.send(embed=error_embed("No Game Running", f"Start a game with `{ctx.prefix}gaw start` first."))
            return

        is_correct, is_close, hint = game.guess(guess)
        if is_correct:
            gaw_manager.end_game(ctx.channel.id)
            await ctx.send(embed=success_embed("Victory! 🎉", f"{ctx.author.mention} solved the puzzle!\n{hint}"))
        elif is_close:
            await ctx.send(embed=info_embed("Close Match!", f"{hint}"))
        else:
            await ctx.send(embed=error_embed("Wrong Guess", f"{hint}"))

    @gaw_group.command(name="end", brief="End active Guess A Word game session.")
    async def gaw_end(self, ctx: commands.Context):
        game = gaw_manager.end_game(ctx.channel.id)
        if game:
            await ctx.send(embed=info_embed("Game Terminated", f"The word was: **{game.word}**."))
        else:
            await ctx.send(embed=info_embed("No Active Game", "No game was running in this channel."))

    # Counting Game Configuration
    @commands.hybrid_group(name="countgame", brief="Setup and manage a counting game channel.")
    @commands.has_permissions(manage_channels=True)
    async def countgame_group(self, ctx: commands.Context):
        embed = branded_embed(
            title="🔢 Counting Game Settings",
            description=(
                f"Commands:\n"
                f"• `{ctx.prefix}countgame channel [channel]` — Designate counting channel\n"
                f"• `{ctx.prefix}countgame remove` — Remove counting game from current channel"
            ),
        )
        await ctx.send(embed=embed)

    @countgame_group.command(name="channel", brief="Designate a text channel for the counting game.")
    @commands.has_permissions(manage_channels=True)
    @app_commands.describe(channel="Text channel to designate (defaults to current)")
    async def countgame_set_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        target = channel or ctx.channel
        async with get_db_session() as session:
            await crud.countgame.set_count_channel(session, ctx.guild.id, target.id)

        await ctx.send(
            embed=success_embed(
                "Counting Channel Configured",
                f"{target.mention} is now the dedicated counting channel! Start from **1**.",
            )
        )

    @countgame_group.command(name="remove", brief="Remove counting game configuration from this channel.")
    @commands.has_permissions(manage_channels=True)
    async def countgame_remove_channel(self, ctx: commands.Context):
        async with get_db_session() as session:
            removed = await crud.countgame.remove_count_channel(session, ctx.guild.id, ctx.channel.id)

        if removed:
            await ctx.send(embed=success_embed("Removed", "Counting game disabled for this channel."))
        else:
            await ctx.send(embed=info_embed("Notice", "This channel was not a counting channel."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Games(bot))
