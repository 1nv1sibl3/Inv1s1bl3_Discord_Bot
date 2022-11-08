import os

from discord.ext import commands
from discord import Intents

from settings import *
from webserver import keep_alive
bot = commands.Bot(command_prefix="i.", intents=Intents.all())

for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(BOT_TOKEN)
