import logging
import time
from typing import Literal, Optional

import discord
from discord.ext import commands
import psutil

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.bot.utils.formatting import format_timespan
from src.bot.utils.api_clients import (
    get_http_session,
    get_fact,
    get_joke,
    get_yesno,
    get_nasa_apod,
)
from src.database.session import get_db_session
from src.database import crud

logger = logging.getLogger("inv1s1bl3.cogs.admin")


class Admin(commands.Cog, name="Admin"):
    """Developer and Bot Owner administrative commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="load", brief="Load a bot cog extension.")
    async def load_extension(self, ctx: commands.Context, cog: str):
        target = f"src.bot.cogs.{cog}" if not cog.startswith("src.") else cog
        try:
            await self.bot.load_extension(target)
            await ctx.send(embed=success_embed("Extension Loaded", f"Successfully loaded `{cog}`."))
            logger.info(f"Extension {cog} loaded by {ctx.author}.")
        except Exception as e:
            await ctx.send(embed=error_embed("Load Failed", f"Error loading `{cog}`:\n```{e}```"))

    @commands.command(name="unload", brief="Unload a bot cog extension.")
    async def unload_extension(self, ctx: commands.Context, cog: str):
        target = f"src.bot.cogs.{cog}" if not cog.startswith("src.") else cog
        try:
            await self.bot.unload_extension(target)
            await ctx.send(embed=success_embed("Extension Unloaded", f"Successfully unloaded `{cog}`."))
            logger.info(f"Extension {cog} unloaded by {ctx.author}.")
        except Exception as e:
            await ctx.send(embed=error_embed("Unload Failed", f"Error unloading `{cog}`:\n```{e}```"))

    @commands.command(name="reload", brief="Reload a bot cog extension.")
    async def reload_extension(self, ctx: commands.Context, cog: str):
        target = f"src.bot.cogs.{cog}" if not cog.startswith("src.") else cog
        try:
            await self.bot.reload_extension(target)
            await ctx.send(embed=success_embed("Extension Reloaded", f"Successfully reloaded `{cog}`."))
            logger.info(f"Extension {cog} reloaded by {ctx.author}.")
        except Exception as e:
            await ctx.send(embed=error_embed("Reload Failed", f"Error reloading `{cog}`:\n```{e}```"))

    @commands.command(name="sync", brief="Synchronize application slash commands with Discord.")
    async def sync_tree(self, ctx: commands.Context, scope: Optional[Literal["guild", "global"]] = "global"):
        msg = await ctx.send("🔄 Synchronizing application commands...")
        try:
            if scope == "guild" and ctx.guild:
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
                await msg.edit(content=None, embed=success_embed("Commands Synced", f"Synced **{len(synced)}** guild commands."))
            else:
                synced = await self.bot.tree.sync()
                await msg.edit(content=None, embed=success_embed("Commands Synced", f"Synced **{len(synced)}** global commands."))
        except Exception as e:
            await msg.edit(content=None, embed=error_embed("Sync Failed", f"Failed to sync command tree:\n```{e}```"))

    @commands.command(name="shutdown", brief="Safely shut down the bot.")
    async def shutdown_bot(self, ctx: commands.Context):
        await ctx.send(embed=info_embed("Shutting Down", "Bot shutdown initiated by administrator."))
        logger.info(f"Shutdown initiated by {ctx.author}.")
        await self.bot.close()

    @commands.command(name="system", brief="Display system diagnostics and API health.")
    async def system_diagnostics(self, ctx: commands.Context):
        async with ctx.typing():
            # Check APIs asynchronously
            fact_ok = (await get_fact()) is not None
            yesno_ok = (await get_yesno()) is not None
            joke_ok = bool((await get_joke()).get("setup"))
            nasa_ok = (await get_nasa_apod()) is not None

            # Database health
            db_status = "❌ Disconnected"
            try:
                async with get_db_session() as session:
                    await crud.users.get_user_data(session, ctx.author.id, ctx.guild.id if ctx.guild else 0)
                    db_status = "✅ Connected"
            except Exception as e:
                db_status = f"❌ Error: {e}"

            uptime_seconds = int(time.time() - getattr(self.bot, "start_time", time.time()))
            total_channels = sum(len(g.channels) for g in self.bot.guilds)

            embed = branded_embed(
                title="System & Health Diagnostics",
                description="Comprehensive diagnostic metrics and service availability status.",
            )
            embed.add_field(name="Bot Version", value=f"`v{getattr(self.bot, 'version', '2.0.0')}`", inline=True)
            embed.add_field(name="Uptime", value=f"`{format_timespan(uptime_seconds)}`", inline=True)
            embed.add_field(name="Gateway Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)

            embed.add_field(name="Total Guilds", value=str(len(self.bot.guilds)), inline=True)
            embed.add_field(name="Total Users", value=str(len(self.bot.users)), inline=True)
            embed.add_field(name="Total Channels", value=str(total_channels), inline=True)

            embed.add_field(name="CPU Usage", value=f"`{psutil.cpu_percent()}%`", inline=True)
            embed.add_field(name="Memory Usage", value=f"`{psutil.virtual_memory().percent}%`", inline=True)
            embed.add_field(name="Database", value=db_status, inline=True)

            embed.add_field(
                name="External APIs",
                value=(
                    f"• Useless Facts: {'✅' if fact_ok else '❌'}\n"
                    f"• YesNo.wtf: {'✅' if yesno_ok else '❌'}\n"
                    f"• Joke API: {'✅' if joke_ok else '❌'}\n"
                    f"• NASA APOD: {'✅' if nasa_ok else '❌'}"
                ),
                inline=False,
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

    @commands.command(name="addmoney", brief="Grant economy currency to a user.")
    async def add_money(
        self,
        ctx: commands.Context,
        member: discord.Member,
        account_type: Literal["wallet", "bank"],
        amount: int,
    ):
        if amount <= 0:
            await ctx.send(embed=error_embed("Invalid Amount", "Amount must be greater than zero."))
            return

        async with get_db_session() as session:
            account = await crud.economy.get_or_create_account(session, member.id)
            if account_type == "wallet":
                account.wallet += amount
            else:
                account.bank += amount
            await session.commit()

        await ctx.send(
            embed=success_embed(
                "Funds Granted",
                f"Granted **{amount:,} iC** to {member.mention}'s **{account_type}**.",
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
