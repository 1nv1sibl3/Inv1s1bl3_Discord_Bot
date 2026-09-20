from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.bot.utils.formatting import text_to_owo
from src.config.settings import settings


class Basic(commands.Cog, name="General"):
    """Fundamental and introductory bot commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", brief="Check bot response latency.")
    async def ping(self, ctx: commands.Context):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(embed=info_embed("Pong! 🏓", f"Gateway latency is **{latency_ms}ms**."))

    @commands.hybrid_command(name="owo", brief="Translate text into playful OwO speak.")
    @app_commands.describe(text="The message text you want to OwO-ify")
    async def owo(self, ctx: commands.Context, *, text: str):
        converted = text_to_owo(text)
        await ctx.send(converted)

    @commands.hybrid_command(name="invite", brief="Get an invite link for the bot or server channel.")
    @commands.guild_only()
    async def invite(self, ctx: commands.Context):
        client_id = settings.discord_client_id or (self.bot.user.id if self.bot.user else 0)
        bot_invite_url = (
            f"https://discord.com/oauth2/authorize?client_id={client_id}"
            f"&permissions=8&scope=bot%20applications.commands"
        )
        try:
            channel_invite = await ctx.channel.create_invite(max_age=86400, max_uses=10)
            channel_url = channel_invite.url
        except Exception:
            channel_url = "Unable to create channel invite (missing permissions)."

        embed = branded_embed(
            title="Inv1s1bl3 Bot Invitations",
            description="Invite the bot to your server or invite friends to this channel!",
        )
        embed.add_field(name="🤖 Bot Invite Link", value=f"[Click Here to Invite Bot]({bot_invite_url})", inline=False)
        embed.add_field(name="📢 Channel Invite", value=channel_url, inline=False)
        if settings.support_server_url:
            embed.add_field(name="💬 Support Server", value=f"[Join Support Community]({settings.support_server_url})", inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="poke", brief="Send a playful poke notification to a member via DM.")
    @commands.guild_only()
    @app_commands.describe(member="The server member you want to poke")
    async def poke(self, ctx: commands.Context, member: discord.Member):
        if member.id == ctx.author.id:
            await ctx.send(embed=error_embed("Cannot Poke Yourself", "You cannot poke yourself! Mention a friend instead."))
            return

        if member.bot:
            await ctx.send(embed=error_embed("Cannot Poke Bots", "Bots don't feel pokes! Poke a human member."))
            return

        poke_msg = f"👉 **{ctx.author.display_name}** poked you from **{ctx.guild.name}**!"
        try:
            channel = member.dm_channel or await member.create_dm()
            await channel.send(poke_msg)
            await ctx.send(embed=success_embed("Poked!", f"Successfully poked {member.mention}!"))
        except discord.Forbidden:
            await ctx.send(embed=error_embed("Poke Failed", f"Could not poke {member.mention}. Their direct messages are disabled."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Basic(bot))
