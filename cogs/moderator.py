from discord.ext import commands
import discord
import asyncio

from utils import mods_or_owner, notify_user


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Kick a member")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, reason: str = "Because you were bad. We kicked you."):
        if member is not None:
            await ctx.guild.kick(member, reason=reason)
        else:
            await ctx.send("Please specify user to kick via mention")

    @commands.command(brief="Ban a member")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None , reason: str = "Because you are naughty. We banned you."):
        
        if member is not None:
          bans = await ctx.guild.bans(limit=150).flatten()
          print(bans)
          for b in bans:
            if b.user.id == member:
              await ctx.reply("Already banned!")
            elif b.user.name or b.user.id == member :  
              message=f"You have been banned because {reason}"
              await notify_user(member,message)
              await ctx.guild.ban(member, reason=reason)
            
              await ctx.reply(":white_check_mark: User has been banned!")
            else:
              await ctx.reply("Please specify user to ban via mention or ID")

    @commands.command(brief="Unban a member")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: str = "", reason: str = "You have been unbanned. Time is over. Please behave"):
        if member == "":
            await ctx.reply("Please specify user ID.")
            return


        bans = await ctx.guild.bans(limit=150).flatten()
        #print(bans)
        for b in bans:
            if b.user.id == member:
               # print(b.user.id)
               # print(b.user.name)
                await ctx.guild.unban(b.user or b.id, reason=reason)
                await ctx.reply(":white_check_mark: User was unbanned")
                return
        await ctx.reply("User was not found in ban list.")
    
    @commands.command(brief="Announce something to the server")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx,channel: discord.TextChannel, message: str):
      try :
        await channel.send(message)
        await ctx.reply(":white_check_mark: announcement sent successfully!")
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid channel..")
      
    @commands.command(brief="Give a role to someone")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member: discord.Member, role: discord.Role):
      try:
        await member.add_roles(role)
        await ctx.reply(":white_check_mark: Role was given successfully!")
        await notify_user(member,f"You have been given a role {role} in {ctx.guild.name}!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid role..")
    
    @commands.command(brief="Remove a role from someone")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
      try:
        await member.remove_roles(role)
        await ctx.reply(":white_check_mark: Role was removed successfully!")
        await notify_user(member,f"You have been removed a role {role} in {ctx.guild.name}!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid role..")

    @commands.command(brief="Mute a member")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, reason: str = "You have been muted. Please behave"):
      try:
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.reply(":white_check_mark: User was muted successfully!")
        await notify_user(member,f"You have been muted in {ctx.guild.name} because {reason}!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid role..")

    @commands.command(brief="Unmute a member")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, reason: str = "You have been unmuted. Time is over. Please behave"):
      try:
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.reply(":white_check_mark: User was unmuted successfully!")
        await notify_user(member,f"You have been unmuted in {ctx.guild.name} because {reason}!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid role..")
    
    @commands.command(brief="Timeout a member for certain limit of time")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def timeout(self, ctx, member: discord.Member, time: str, reason: str = "You have been timed out. Please behave"):
      try:
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.reply(":white_check_mark: User was timed out successfully!")
        await notify_user(member,f"You have been timed out in {ctx.guild.name} because {reason}!")
        await asyncio.sleep(time)
        await member.remove_roles(role)
        await notify_user(member,f"You have been unmuted in {ctx.guild.name} because {reason}!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid role..")
    
    @commands.command(brief="Lock a channel")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
      try:
        if channel is None:
          channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.reply(":white_check_mark: Channel was locked successfully!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid channel..")
    
    @commands.command(brief="Unlock a channel")
    @mods_or_owner()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
      try:
        if channel is None:
          channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.reply(":white_check_mark: Channel was unlocked successfully!")
        
      except Exception as e:
        await ctx.reply(f"Error : {e} \n Please send a valid channel..")
    
    @commands.command(aliases=['clean','cls','sweep'],brief="Clear messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1000):
        await ctx.channel.purge(limit=amount+1)



def setup(bot):
    bot.add_cog(Moderator(bot))
