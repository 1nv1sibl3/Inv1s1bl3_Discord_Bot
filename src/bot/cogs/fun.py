from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, error_embed, info_embed
from src.bot.utils.api_clients import (
    get_fact,
    get_yesno,
    get_wikipedia_summary,
    get_nasa_apod,
    get_pokedex,
    get_ai_chat_response,
)


class Fun(commands.Cog, name="Fun & Media"):
    """Entertainment, knowledge queries, and media commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="fact", brief="Get a random interesting or useless fact.")
    async def fact(self, ctx: commands.Context):
        fact_text = await get_fact()
        embed = branded_embed(
            title="💡 Did You Know?",
            description=fact_text,
            footer="Powered by Useless Facts",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="yesno", brief="Ask a question and receive a definitive Yes or No with a GIF.")
    @app_commands.describe(question="The yes/no question to ask")
    async def yesno(self, ctx: commands.Context, *, question: str):
        data = await get_yesno()
        answer = data.get("answer", "maybe").upper()
        image = data.get("image")

        embed = branded_embed(
            title=f"❓ {question}",
            description=f"The cosmos says: **{answer}**",
            image=image,
            footer=f"Requested by {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="wiki", brief="Search Wikipedia and retrieve an article summary.")
    @app_commands.describe(query="Topic to search on Wikipedia")
    async def wikipedia(self, ctx: commands.Context, *, query: str):
        async with ctx.typing():
            data = await get_wikipedia_summary(query)

        if not data or "extract" not in data:
            await ctx.send(embed=error_embed("Article Not Found", f"No Wikipedia article found matching `{query}`."))
            return

        title = data.get("title", query)
        extract = data.get("extract", "No description available.")
        if len(extract) > 1000:
            extract = extract[:997] + "..."

        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{query}")
        thumbnail = data.get("thumbnail", {}).get("source")

        embed = branded_embed(
            title=f"📖 {title}",
            description=f"{extract}\n\n[Read full article on Wikipedia]({page_url})",
            thumbnail=thumbnail,
            footer="Powered by Wikipedia",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="nasa", brief="Get NASA's Astronomy Picture of the Day.")
    @app_commands.describe(date="Optional date in YYYY-MM-DD format")
    async def nasa(self, ctx: commands.Context, date: Optional[str] = None):
        async with ctx.typing():
            data = await get_nasa_apod(date)

        if not data or "title" not in data:
            await ctx.send(embed=error_embed("NASA Data Unavailable", "Could not fetch Astronomy Picture of the Day for that date."))
            return

        title = data.get("title", "NASA Astronomy Picture of the Day")
        explanation = data.get("explanation", "")
        if len(explanation) > 1000:
            explanation = explanation[:997] + "..."

        image_url = data.get("hdurl") or data.get("url")

        embed = branded_embed(
            title=f"🚀 {title}",
            description=explanation,
            image=image_url if image_url and (image_url.endswith(".jpg") or image_url.endswith(".png")) else None,
            footer=f"NASA APOD • {data.get('date', '')}",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pokedex", brief="Look up details and statistics on a Pokemon.")
    @app_commands.describe(pokemon="Name or ID of the Pokemon")
    async def pokedex(self, ctx: commands.Context, *, pokemon: str):
        async with ctx.typing():
            data = await get_pokedex(pokemon)

        if not data:
            await ctx.send(embed=error_embed("Pokemon Not Found", f"No Pokemon matching `{pokemon}` was found."))
            return

        name = data.get("name", pokemon).capitalize()
        poke_id = data.get("id", "???")
        height = data.get("height", 0) / 10.0  # decimeters to meters
        weight = data.get("weight", 0) / 10.0  # hectograms to kg

        types = [t["type"]["name"].capitalize() for t in data.get("types", [])]
        abilities = [a["ability"]["name"].capitalize() for a in data.get("abilities", [])]
        sprite = data.get("sprites", {}).get("front_default")

        embed = branded_embed(
            title=f"🔴 Pokédex: #{poke_id} {name}",
            thumbnail=sprite,
            footer="Powered by PokéAPI",
        )
        embed.add_field(name="Type(s)", value=", ".join(types) if types else "Unknown", inline=True)
        embed.add_field(name="Height", value=f"{height} m", inline=True)
        embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
        embed.add_field(name="Abilities", value=", ".join(abilities) if abilities else "None", inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="chat", brief="Talk to Inv1s1bl3 Bot's AI brain.")
    @app_commands.describe(message="What do you want to say to the bot?")
    async def chat(self, ctx: commands.Context, *, message: str):
        async with ctx.typing():
            reply = await get_ai_chat_response(message, ctx.author.display_name)

        embed = branded_embed(
            title="💬 Inv1s1bl3 AI",
            description=reply,
            footer=f"Responding to {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="wouldyourather", aliases=["wyr", "wr"], brief="Pose a tough 'Would You Rather' question.")
    async def wouldyourather(self, ctx: commands.Context):
        dilemmas = [
            ("Have the ability to fly", "Have the ability to be invisible"),
            ("Be able to speak all human languages", "Be able to speak to all animals"),
            ("Always be 15 minutes early", "Always be 20 minutes late"),
            ("Live without music", "Live without video games"),
            ("Have unlimited free food for life", "Have unlimited free travel for life"),
            ("Know every secret of the universe", "Know how to fix every bug in your code instantly"),
        ]
        import random
        choice_a, choice_b = random.choice(dilemmas)

        embed = branded_embed(
            title="🤔 Would You Rather?",
            description=f"**1️⃣ {choice_a}**\n\n*— OR —*\n\n**2️⃣ {choice_b}**",
            footer="React with 1️⃣ or 2️⃣ to vote!",
        )
        msg = await ctx.send(embed=embed)
        try:
            await msg.add_reaction("1️⃣")
            await msg.add_reaction("2️⃣")
        except Exception:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
