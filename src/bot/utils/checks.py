from typing import Callable, Union
import discord
from discord.ext import commands

from src.config.settings import settings


def is_owner_or_admin():
    """Check if the user is a bot owner or guild administrator."""
    async def predicate(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        user = ctx.author if isinstance(ctx, commands.Context) else ctx.user

        # Bot owner bypass
        if user.id in settings.owner_ids or (ctx.bot and await ctx.bot.is_owner(user)):
            return True

        if isinstance(ctx, commands.Context):
            if ctx.guild and ctx.author.guild_permissions.administrator:
                return True
        elif ctx.guild and ctx.user.guild_permissions.administrator:
            return True

        return False

    return commands.check(predicate)


def is_mod_or_owner():
    """Check if the user is a moderator, administrator, or bot owner."""
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        # Owner bypass
        if ctx.author.id in settings.owner_ids or await ctx.bot.is_owner(ctx.author):
            return True

        # Administrator or Manage Guild
        perms = ctx.author.guild_permissions
        if perms.administrator or perms.manage_guild or perms.manage_messages:
            return True

        # Check moderator role names
        mod_role_names = ["moderator", "mod", "admin", "administrator"]
        for role in ctx.author.roles:
            if role.name.lower() in mod_role_names:
                return True

        return False

    return commands.check(predicate)
