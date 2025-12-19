import os
import discord
from dotenv import load_dotenv

# 1. On charge le coffre-fort (.env)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. On configure les "Intents" (Les autorisations du bot)
intents = discord.Intents.default()
intents.message_content = True # Important pour lire les messages !

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user} !')

# 3. Lancement
client.run(TOKEN)