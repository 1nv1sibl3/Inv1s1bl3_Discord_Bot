import discord
from discord import *
from discord.ext import commands
import os
import random
import datetime

from settings import MODERATOR_ROLE_NAME


class Server_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Gives Server Stats")
    async def status(self, ctx):
        guild = ctx.guild
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        total_channels = text_channels + voice_channels
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = guild.member_count
        embed = Embed(title=f"**{guild.name}**",
                      description="Server Status",
                      color=0x00ff00,
                      timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Text Channels", value=text_channels)
        embed.add_field(name="Voice Channels", value=voice_channels)
        embed.add_field(name="Categories", value=categories)
        embed.add_field(name="Total Channels", value=total_channels)
        embed.add_field(name="Online", value=online)
        embed.add_field(name="Total Users", value=total_users)
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(brief="Gives Bot Stats")
    async def stats(self, ctx):
        embed = discord.Embed(title="**Bot Stats**",description="`i.stats` or `/stats` gives Bot Stats",colour=discord.Colour.dark_purple())

        embed.add_field(name="Bot Name", value=f"`{self.bot.user.name}`")

        embed.add_field(name="Bot ID", value=f"`{self.bot.user.id}`")

        embed.add_field(name="Bot Version", value=f"`0.0.1`")

        embed.add_field(name="Bot Creator", value=f"`Inv1s1bl3#7047`")

        embed.add_field(name="Bot Library", value=f"`Pycord`")

        embed.add_field(name="Bot Language", value=f"`Python`")

        embed.add_field(name="Bot Host", value=f"`Linux`")

        embed.add_field(name="Bot Uptime", value=f"`N/A`")

        embed.add_field(name="Bot Ping", value=f"`{round(self.bot.latency * 1000)}ms`")

        embed.add_field(name="Bot Servers", value=f"`{len(self.bot.guilds)}`")

        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=datetime.datetime.now())
        await ctx.send(embed=embed)    
    
    @commands.command(aliases=["hi"],brief="Gives Inv1s1bl3 testing community Invite Link")
    async def help_invite(self, ctx):
        embed = discord.Embed(title="**Invite Link**",description="`i.invite` or `/invite` gives Invite Link",colour=discord.Colour.dark_purple())
        embed.add_field(name="Invite Link", value=f"[Click Here](https://discord.gg/UQ6Uh4d4nM)")
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=datetime.datetime.now())
        await ctx.send(embed=embed)
    
    @commands.command(brief="Get more info on a user or yourself")
    async def whois(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        roles = [role for role in member.roles]
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Display Name:", value=member.display_name)
        embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top Role:", value=member.top_role.mention)
        await ctx.send(embed=embed)
    
    @commands.command(brief="Play a game of Rock Paper Scissors")
    async def rps(self, ctx, choice: str):
        choices = ["rock", "paper", "scissors"]
        if choice.lower() not in choices:
            await ctx.send("Please choose rock, paper or scissors")
        else:
            bot_choice = random.choice(choices)
            if choice.lower() == bot_choice:
                await ctx.send("It's a tie!")
            elif choice.lower() == "rock":
                if bot_choice == "paper":
                    await ctx.send("I win!")
                else:
                    await ctx.send("You win!")
            elif choice.lower() == "paper":
                if bot_choice == "scissors":
                    await ctx.send("I win!")
                else:
                    await ctx.send("You win!")
            elif choice.lower() == "scissors":
                if bot_choice == "rock":
                    await ctx.send("I win!")
                else:
                    await ctx.send("You win!")

    

    

      




def setup(bot):
    bot.add_cog(Server_Commands(bot))
