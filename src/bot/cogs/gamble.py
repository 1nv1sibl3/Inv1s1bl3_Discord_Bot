import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed


class CoinFlipView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    @discord.ui.button(label="Flip Again 🪙", style=discord.ButtonStyle.primary)
    async def flip_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original caller can re-flip!", ephemeral=True)
            return

        result = random.choice(["Heads", "Tails"])
        emoji = "👑" if result == "Heads" else "🪙"
        embed = branded_embed(
            title=f"Coin Toss: {result} {emoji}",
            description=f"{interaction.user.mention} flipped **{result}**!",
        )
        await interaction.response.edit_message(embed=embed, view=self)


class DiceRollView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    @discord.ui.button(label="Roll Again 🎲", style=discord.ButtonStyle.primary)
    async def roll_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original caller can re-roll!", ephemeral=True)
            return

        result = random.randint(1, 6)
        dice_emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        embed = branded_embed(
            title=f"Dice Roll: {result} {dice_emojis.get(result, '')}",
            description=f"{interaction.user.mention} rolled a **{result}** on a standard 6-sided die.",
        )
        await interaction.response.edit_message(embed=embed, view=self)


class Gamble(commands.Cog, name="Chance & Gambling"):
    """Probability, random rolls, and interactive chance games."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="coin", aliases=["flip", "coinflip"], brief="Flip a coin for Heads or Tails.")
    async def coin(self, ctx: commands.Context):
        result = random.choice(["Heads", "Tails"])
        emoji = "👑" if result == "Heads" else "🪙"
        embed = branded_embed(
            title=f"Coin Toss: {result} {emoji}",
            description=f"{ctx.author.mention} flipped **{result}**!",
        )
        view = CoinFlipView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="dice", aliases=["die", "roll6"], brief="Roll a standard 6-sided die.")
    async def dice(self, ctx: commands.Context):
        result = random.randint(1, 6)
        dice_emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        embed = branded_embed(
            title=f"Dice Roll: {result} {dice_emojis.get(result, '')}",
            description=f"{ctx.author.mention} rolled a **{result}** on a 6-sided die.",
        )
        view = DiceRollView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="roll", brief="Generate a random integer between 1 and max_number (default: 100).")
    @app_commands.describe(max_number="Maximum bound for the roll (default: 100)")
    async def roll(self, ctx: commands.Context, max_number: int = 100):
        if max_number <= 1:
            max_number = 100
        number = random.randint(1, max_number)
        embed = branded_embed(
            title="🎲 Random Number Roll",
            description=f"{ctx.author.mention} rolled: **{number:,}** (Range: 1 – {max_number:,})",
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Gamble(bot))
