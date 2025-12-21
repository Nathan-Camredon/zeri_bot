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
jour_int =  conversion_jours[jour]


#------------------------------------------------------
#           BOT
#------------------------------------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user} !')
#------------------------------------------------------
#           TOKEN
#------------------------------------------------------
client.run(TOKEN)