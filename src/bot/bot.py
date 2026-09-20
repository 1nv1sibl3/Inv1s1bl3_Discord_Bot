import asyncio
import logging
import math
import sys
import time
import traceback
from typing import List, Union

import discord
from discord import app_commands
from discord.ext import commands

from src.config.settings import settings
from src.database.session import get_db_session, init_db, close_db
from src.database import crud
from src.bot.utils.embeds import error_embed, warning_embed
from src.bot.utils.api_clients import close_http_session

logger = logging.getLogger("inv1s1bl3.bot")

INITIAL_EXTENSIONS = [
    "src.bot.cogs.admin",
    "src.bot.cogs.basic",
    "src.bot.cogs.business",
    "src.bot.cogs.economy",
    "src.bot.cogs.fun",
    "src.bot.cogs.gamble",
    "src.bot.cogs.games",
    "src.bot.cogs.moderator",
    "src.bot.cogs.server",
    "src.bot.cogs.mv",
]


async def determine_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Dynamically determine prefix based on guild settings or defaults."""
    default = settings.default_prefix
    if not message.guild:
        return commands.when_mentioned_or(default)(bot, message)

    try:
        async with get_db_session() as session:
            guild_prefix = await crud.server.get_prefix(
                session, message.guild.id, default_prefix=default
            )
            return commands.when_mentioned_or(guild_prefix)(bot, message)
    except Exception as e:
        logger.warning(f"Error fetching guild prefix: {e}. Falling back to default.")
        return commands.when_mentioned_or(default)(bot, message)


class Inv1s1bl3Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=determine_prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand(dm_help=False),
            case_insensitive=True,
        )

        self.start_time: float = time.time()
        self.version: str = "2.0.0"

    async def setup_hook(self) -> None:
        """Asynchronous initialization hook called before login."""
        logger.info("Initializing database...")
        await init_db()

        logger.info("Loading extensions...")
        for ext in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}", exc_info=True)

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds with {len(self.users)} cached users")

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{settings.default_prefix}help | Revived v{self.version}",
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global command error handler."""
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = warning_embed(
                title="Command On Cooldown",
                description=f"Please wait **{math.ceil(error.retry_after)}s** before retrying.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(f"`{p.replace('_', ' ').title()}`" for p in error.missing_permissions)
            embed = error_embed(
                title="Insufficient Permissions",
                description=f"You need the following permissions to use this command:\n{perms}",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(f"`{p.replace('_', ' ').title()}`" for p in error.missing_permissions)
            embed = error_embed(
                title="Bot Missing Permissions",
                description=f"I need the following permissions to execute this command:\n{perms}",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.UserInputError):
            embed = warning_embed(
                title="Invalid Input",
                description=f"Invalid arguments provided: `{error}`\nUse `{ctx.prefix}help {ctx.command}` for correct usage.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.NoPrivateMessage):
            embed = warning_embed(
                title="Server Only",
                description="This command cannot be used in private messages.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CheckFailure):
            embed = error_embed(
                title="Permission Denied",
                description="You do not have permission to execute this command.",
            )
            await ctx.send(embed=embed)
            return

        # Unexpected errors
        logger.error(f"Ignoring unhandled exception in command {ctx.command}:", exc_info=error)
        embed = error_embed(
            title="Unexpected Error",
            description="An unexpected error occurred while executing this command. The issue has been logged.",
        )
        try:
            await ctx.send(embed=embed)
        except Exception:
            pass

    async def close(self) -> None:
        """Graceful shutdown handler."""
        logger.info("Bot is shutting down...")
        await close_http_session()
        await close_db()
        await super().close()
