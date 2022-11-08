import discord
from discord import *
from discord.ext import commands
import os

import datetime

from settings import MODERATOR_ROLE_NAME


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        unload_embed = Embed(description=f"**:loading: {self.bot.user.mention} is unloading the cog {cog}..**",color=discord.Color.red(),)
        msg = await ctx.send(embed=unload_embed) 
        try:
            get_cog=f"cogs.{cog}"
            self.bot.unload_extension(get_cog)
            await msg.edit(embed=unload_embed)
        
        
        except Exception as e:
            unload_failed_embed = Embed(description=f"**{self.bot.user.mention} failed to unload the cog {cog} :x:..**",color=discord.Color.red(),    )
            await msg.edit(embed=unload_failed_embed)
            return
        unloaded_embed = Embed(description=f"**{self.bot.user.mention} unloaded the cog {cog} successfully :white_check_mark: ..**",
            color=discord.Color.red(),
        )    
        await msg.edit(embed=unloaded_embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        load_embed = Embed(description=f"**{self.bot.user.mention} is loading the cog {cog}..**",color=discord.Color.red(),)
        msg = await ctx.send(embed=load_embed) 
        
        try:
            get_cog=f"cogs.{cog}"
            self.bot.load_extension(get_cog)
            await msg.edit(embed=load_embed)

        except Exception as e:
            unload_failed_embed = Embed(description=f"**{self.bot.user.mention} failed to load the cog {cog} :x:..**",color=discord.Color.red(),    )
            await msg.edit(embed=unload_failed_embed)
            return
        loaded_embed = Embed(description=f"**{self.bot.user.mention} loaded the cog {cog} successfully :white_check_mark: ..**",color=discord.Color.red() )    
        await msg.edit(embed=loaded_embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        reload_embed = Embed(description=f"**{self.bot.user.mention} is reloading the cog {cog}..**",color=discord.Color.red(),)
        msg = await ctx.send(embed=reload_embed)
        try:
            get_cog=f"cogs.{cog}"
            self.bot.unload_extension(get_cog)
            self.bot.load_extension(get_cog)
            await msg.edit(embed=reload_embed)

        except Exception as e:
            reload_failed_embed = Embed(description=f"**{self.bot.user.mention} failed to reload the cog {cog} :x:..**",color=discord.Color.red(),    )
            await msg.edit(embed=reload_failed_embed)
            return
        reloaded_embed = Embed(description=f"**{self.bot.user.mention} reloaded the cog {cog} successfully :white_check_mark: ..**",
            color=discord.Color.red(),
        )  
        await msg.edit(embed=reloaded_embed)


    @commands.slash_command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await ctx.bot.close()



def setup(bot):
    bot.add_cog(Admin(bot))
