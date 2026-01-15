#------------------------------------------------------
#           Import
#------------------------------------------------------
import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
#------------------------------------------------------
#           VARYABLES
#------------------------------------------------------

conversion_jours = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6
}

#------------------------------------------------------
#           BOT
#------------------------------------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user} !')

#------------------------------------------------------
#           TOKEN
#------------------------------------------------------
bot.run(TOKEN)