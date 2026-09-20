"""
Legacy experimental Multimedia / Voice (mv) cog.
Preserved from original project for historical completeness.
"""
from typing import Optional
from discord.ext import commands

from src.bot.utils.embeds import info_embed


class Multimedia(commands.Cog, name="Multimedia (Legacy)"):
    """Legacy experimental audio and video features."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="yt", brief="[Legacy] Experimental YouTube video voice channel activity.")
    async def yt_stream(self, ctx: commands.Context, url: Optional[str] = None):
        embed = info_embed(
            title="Feature Status: Legacy Experimental",
            description=(
                "The `yt` command was an early prototype for Discord voice channel video sharing. "
                "Following Discord's native YouTube Watch Together activities integration, "
                "this command is archived in open-source as an educational milestone."
            ),
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Multimedia(bot))
