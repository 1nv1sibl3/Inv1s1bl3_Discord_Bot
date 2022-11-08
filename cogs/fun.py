import discord
from discord import *
from discord.ext import commands
import os
import json
import datetime
import requests
from requests import get
import google
from googlesearch import search
from settings import NASA_TOKEN


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Gives a random fact")
    async def fact(self, ctx):
        start="Did u know?"
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        json_data = json.loads(response.text)
        fact = json_data["text"]
        embed = Embed(title=start, description=fact, color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(brief="Get answer of any question in form of yes/no")
    async def yesno(self, ctx, *, question):
        response = requests.get("https://yesno.wtf/api")
        json_data = json.loads(response.text)
        answer = json_data["answer"]
        image = json_data["image"]
        embed = Embed(title=question, description=answer, color=discord.Color.red())
        embed.set_image(url=image)
        embed.set_footer(text="| Powered by yesno.wtf | Answers may or may not be correct |")
        await ctx.send(embed=embed)
    
    @commands.command(brief="Get information from wikipedia")
    async def wiki(self, ctx, *, query):
        response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
        json_data = json.loads(response.text)
        title = json_data["title"]
        description = json_data["description"]
        embed = Embed(title=title, description=description, color=discord.Color.red())
        if "thumbnail" in json_data:
            image = json_data["thumbnail"]["source"]
            embed.set_image(url=image)
        else:
            pass
        embed.set_footer(text=f" Powered by Wikipedia | Requested by {ctx.author.name}",icon_url=ctx.author.display_avatar) 
        await ctx.send(embed=embed)
    
    @commands.command(brief="Get answer of any question from Google in form of link!")
    async def gsearch(self, ctx, *, query):
        if query == "":
            await ctx.send("Please enter a query")
        else:
            author = ctx.author.mention
            await ctx.send(f"Searching for {query}...")
            async with ctx.typing():
                try:
                    search_results = search(query, tld="co.in", num=1, stop=1, pause=2)
                    for result in search_results:
                        embed = Embed(title=f"Search results for {query}", description=result, color=discord.Color.red())
                        embed.set_footer(text=f"Powered by Google | Requested by {author}")
                        await ctx.send(embed=embed)
                except:
                    await ctx.send("No results found")
    
    @commands.command(brief="Get updates of latest NASA pics!")
    async def apod(ctx,date = None):
        if date == None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_TOKEN}&date={date}"
        response = requests.get(url)
        json_data = json.loads(response.text)
        if title in json_data:
            title = json_data["title"]
            if explanation in json_data:
                explanation = json_data["explanation"]
                if url in json_data:
                    url = json_data["url"]
                    embed = Embed(title=title, description=explanation, color=discord.Color.red())
                    embed.set_image(url=url)
                    embed.set_footer(text=f"Powered by NASA | Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar)
                    await ctx.send(embed=embed)
        else:
            await ctx.send("No results found")






def setup(bot):
    bot.add_cog(Fun(bot))
