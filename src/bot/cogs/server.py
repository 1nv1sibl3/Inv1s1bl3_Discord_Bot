import platform
import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import psutil

from src.bot.utils.embeds import branded_embed
from src.bot.utils.formatting import format_timespan
from src.config.settings import settings


class Server(commands.Cog, name="Server & Bot Info"):
    """Server analytics, bot runtime details, and member inspect commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="status", aliases=["serverinfo", "guildinfo"], brief="Display comprehensive statistics for this server.")
    @commands.guild_only()
    async def server_status(self, ctx: commands.Context):
        guild = ctx.guild
        owner = guild.owner or await self.bot.fetch_user(guild.owner_id)

        text_ch = len(guild.text_channels)
        voice_ch = len(guild.voice_channels)
        categories = len(guild.categories)
        total_ch = text_ch + voice_ch

        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)

        embed = branded_embed(
            title=f"🏰 {guild.name}",
            description=f"**Server ID:** `{guild.id}`\n**Owner:** {owner.mention}",
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👥 Members", value=f"Total: `{guild.member_count}`\nHumans: `{humans}`\nBots: `{bots}`", inline=True)
        embed.add_field(name="💬 Channels", value=f"Text: `{text_ch}`\nVoice: `{voice_ch}`\nCategories: `{categories}`", inline=True)
        embed.add_field(name="🛡️ Roles", value=f"`{len(guild.roles)}`", inline=True)

        created_ts = int(guild.created_at.timestamp())
        embed.add_field(name="📅 Created", value=f"<t:{created_ts}:F> (<t:{created_ts}:R>)", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", footer_icon=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="stats", aliases=["botinfo", "about"], brief="Display bot uptime, library specifications, and resource utilization.")
    async def show_bot_stats(self, ctx: commands.Context):
        uptime_secs = int(time.time() - getattr(self.bot, "start_time", time.time()))
        total_users = sum(len(g.members) for g in self.bot.guilds)

        embed = branded_embed(
            title=f"🤖 {self.bot.user.name} — System Overview",
            description="Revived & modernized open-source Discord bot.",
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="Bot Version", value=f"`v{getattr(self.bot, 'version', '2.0.0')}`", inline=True)
        embed.add_field(name="Library", value=f"`discord.py v{discord.__version__}`", inline=True)
        embed.add_field(name="Python Runtime", value=f"`v{platform.python_version()}`", inline=True)

        embed.add_field(name="Uptime", value=f"`{format_timespan(uptime_secs)}`", inline=True)
        embed.add_field(name="Gateway Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="Hosting Platform", value=f"`{platform.system()} {platform.release()}`", inline=True)

        embed.add_field(name="Guilds Served", value=f"`{len(self.bot.guilds):,}`", inline=True)
        embed.add_field(name="Users Tracked", value=f"`{total_users:,}`", inline=True)
        embed.add_field(name="Total Commands", value=f"`{len(self.bot.commands):,}`", inline=True)

        embed.add_field(name="CPU Usage", value=f"`{psutil.cpu_percent()}%`", inline=True)
        embed.add_field(name="Memory Usage", value=f"`{psutil.virtual_memory().percent}%`", inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="whois", aliases=["userinfo"], brief="Retrieve user identity, account age, join date, and roles.")
    @commands.guild_only()
    @app_commands.describe(member="Member to inspect")
    async def whois(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        roles = [r.mention for r in target.roles if not r.is_default()]
        roles.reverse()

        embed = branded_embed(
            title=f"👤 {target.display_name}",
            description=f"**User ID:** `{target.id}`\n**Username:** `{target.name}`",
            color=target.color.value if target.color.value else 0x5865F2,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        created_ts = int(target.created_at.timestamp())
        embed.add_field(name="🗓️ Account Registered", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=True)

        if target.joined_at:
            joined_ts = int(target.joined_at.timestamp())
            embed.add_field(name="📥 Joined Server", value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", inline=True)

        embed.add_field(name="⭐ Top Role", value=target.top_role.mention, inline=False)

        role_str = " ".join(roles[:15]) if roles else "None"
        if len(roles) > 15:
            role_str += f" *(+{len(roles) - 15} more)*"
        embed.add_field(name=f"🛡️ Roles ({len(roles)})", value=role_str, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author.display_name}", footer_icon=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hinvite", aliases=["support"], brief="Get official community support invite link.")
    async def support_invite(self, ctx: commands.Context):
        url = settings.support_server_url
        embed = branded_embed(
            title="Inv1s1bl3 Community & Support",
            description=f"Join our community for assistance, updates, and open-source collaboration:\n\n👉 [Click Here to Join]({url})",
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))
