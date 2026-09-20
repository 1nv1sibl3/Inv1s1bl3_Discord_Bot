from datetime import timedelta
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.database.session import get_db_session
from src.database import crud

logger = logging.getLogger("inv1s1bl3.cogs.moderator")


class Moderator(commands.Cog, name="Moderation"):
    """Server management, moderation enforcement, and configuration."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _notify_member(self, member: discord.Member, guild_name: str, action: str, reason: Optional[str]):
        try:
            channel = member.dm_channel or await member.create_dm()
            reason_text = f" Reason: {reason}" if reason else ""
            await channel.send(f"⚠️ You were **{action}** in **{guild_name}**.{reason_text}")
        except Exception:
            pass

    @commands.hybrid_command(name="kick", brief="Kick a member from the server.")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=error_embed("Hierarchy Error", "You cannot moderate a member with an equal or higher role."))
            return

        if member.id == self.bot.user.id:
            await ctx.send(embed=error_embed("Error", "I cannot kick myself!"))
            return

        await self._notify_member(member, ctx.guild.name, "kicked", reason)
        await member.kick(reason=reason or f"Kicked by {ctx.author}")
        await ctx.send(embed=success_embed("Member Kicked", f"Successfully kicked {member.mention}. Reason: `{reason or 'None'}`"))

    @commands.hybrid_command(name="ban", brief="Ban a member from the server.")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @app_commands.describe(member="Member to ban", reason="Reason for the ban")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=error_embed("Hierarchy Error", "You cannot ban a member with an equal or higher role."))
            return

        if member.id == self.bot.user.id:
            await ctx.send(embed=error_embed("Error", "I cannot ban myself!"))
            return

        await self._notify_member(member, ctx.guild.name, "banned", reason)
        await ctx.guild.ban(member, reason=reason or f"Banned by {ctx.author}")
        await ctx.send(embed=success_embed("Member Banned", f"Successfully banned {member.mention}. Reason: `{reason or 'None'}`"))

    @commands.hybrid_command(name="unban", brief="Unban a user by their ID.")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @app_commands.describe(user_id="Discord User ID to unban", reason="Reason for unban")
    async def unban(self, ctx: commands.Context, user_id: str, *, reason: Optional[str] = None):
        if not user_id.isdigit():
            await ctx.send(embed=error_embed("Invalid ID", "Please provide a valid numerical Discord User ID."))
            return

        target_id = int(user_id)
        found_entry: Optional[discord.BanEntry] = None

        # Modern discord.py async ban iteration
        async for ban_entry in ctx.guild.bans(limit=1000):
            if ban_entry.user.id == target_id:
                found_entry = ban_entry
                break

        if not found_entry:
            await ctx.send(embed=error_embed("Not Found", f"User with ID `{user_id}` was not found in the ban registry."))
            return

        await ctx.guild.unban(found_entry.user, reason=reason or f"Unbanned by {ctx.author}")
        await ctx.send(embed=success_embed("User Unbanned", f"Successfully unbanned **{found_entry.user.name}**."))

    @commands.hybrid_command(name="timeout", aliases=["mute"], brief="Mute/timeout a member for a duration in minutes.")
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to timeout", minutes="Duration in minutes (max: 40320 / 28 days)", reason="Reason for timeout")
    async def timeout(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: Optional[str] = None):
        if minutes <= 0 or minutes > 40320:
            await ctx.send(embed=error_embed("Invalid Duration", "Timeout duration must be between 1 and 40,320 minutes (28 days)."))
            return

        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=error_embed("Hierarchy Error", "You cannot moderate a member with an equal or higher role."))
            return

        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason or f"Timed out by {ctx.author}")
        await self._notify_member(member, ctx.guild.name, f"timed out for {minutes} minutes", reason)

        await ctx.send(
            embed=success_embed(
                "Member Timed Out",
                f"Successfully timed out {member.mention} for **{minutes} minutes**.\nReason: `{reason or 'None'}`",
            )
        )

    @commands.hybrid_command(name="untimeout", aliases=["unmute"], brief="Remove timeout/mute from a member.")
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to remove timeout from", reason="Reason for removing timeout")
    async def untimeout(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        await member.timeout(None, reason=reason or f"Timeout lifted by {ctx.author}")
        await ctx.send(embed=success_embed("Timeout Cleared", f"Successfully removed timeout for {member.mention}."))

    @commands.hybrid_command(name="clear", aliases=["purge", "clean", "sweep"], brief="Purge messages in this channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @app_commands.describe(amount="Number of messages to clear (1-100)")
    async def clear_messages(self, ctx: commands.Context, amount: int = 10):
        if amount <= 0 or amount > 100:
            await ctx.send(embed=error_embed("Invalid Amount", "Please specify a number between 1 and 100."), ephemeral=True)
            return

        deleted = await ctx.channel.purge(limit=amount + (1 if not ctx.interaction else 0))
        count = len(deleted) - (1 if not ctx.interaction else 0)
        msg = await ctx.send(embed=success_embed("Messages Cleared", f"Purged **{max(0, count)}** messages."))
        await asyncio.sleep(4)
        try:
            await msg.delete()
        except Exception:
            pass

    @commands.hybrid_command(name="lock", brief="Lock channel preventing @everyone from sending messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        target = channel or ctx.channel
        await target.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=success_embed("Channel Locked 🔒", f"{target.mention} is now locked."))

    @commands.hybrid_command(name="unlock", brief="Unlock channel allowing @everyone to send messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        target = channel or ctx.channel
        await target.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=success_embed("Channel Unlocked 🔓", f"{target.mention} is now open."))

    @commands.hybrid_command(name="announce", brief="Send a stylized announcement to a designated channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(channel="Destination text channel", message="Announcement text")
    async def announce(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        embed = branded_embed(
            title="📢 Server Announcement",
            description=message,
            footer=f"Announced by {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url,
        )
        await channel.send(embed=embed)
        await ctx.send(embed=success_embed("Announcement Dispatched", f"Sent announcement to {channel.mention}."))

    @commands.hybrid_command(name="giverole", brief="Assign a role to a member.")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def give_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=error_embed("Hierarchy Error", "You cannot assign a role higher or equal to your own."))
            return

        await member.add_roles(role)
        await ctx.send(embed=success_embed("Role Granted", f"Assigned {role.mention} to {member.mention}."))

    @commands.hybrid_command(name="removerole", brief="Remove a role from a member.")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def remove_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=error_embed("Hierarchy Error", "You cannot remove a role higher or equal to your own."))
            return

        await member.remove_roles(role)
        await ctx.send(embed=success_embed("Role Removed", f"Revoked {role.mention} from {member.mention}."))

    @commands.hybrid_command(name="setprefix", brief="Configure a custom bot command prefix for this server.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(new_prefix="New command prefix (e.g. ! or ?)")
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        new_prefix = new_prefix.strip()
        if len(new_prefix) > 5 or not new_prefix:
            await ctx.send(embed=error_embed("Invalid Prefix", "Prefix must be between 1 and 5 characters."))
            return

        async with get_db_session() as session:
            await crud.server.set_prefix(session, ctx.guild.id, new_prefix)

        await ctx.send(
            embed=success_embed(
                "Prefix Updated",
                f"Server prefix updated to **`{new_prefix}`**!\nExample: `{new_prefix}ping`",
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderator(bot))
