#------------------------------------------------------
#           Import
#------------------------------------------------------
import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Literal
from modules.add import add_player
from modules.affichages import display_team
#------------------------------------------------------
#           VARIABLES
#------------------------------------------------------

day_conversion = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}
#day_int =  day_conversion[day]

#------------------------------------------------------
#           TABLE SQL
#------------------------------------------------------
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS joueurs (
        discord_id INTEGER PRIMARY KEY,
        pseudo TEXT,
        jeu TEXT,
        groupe TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispo (
        discord_id INTEGER,
        jour INTEGER,
        heure_debut INTEGER,
        heure_fin INTEGER
    )
""")
conn.commit()
#------------------------------------------------------
#           BOT
#------------------------------------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready. 
    Syncs the slash commands with the configured Guild.
    """
    GUILD_ID = os.getenv('GUILD_ID')
    my_guild = discord.Object(id=int(GUILD_ID))
    bot.tree.copy_global_to(guild=my_guild)
    try:
        synced = await bot.tree.sync(guild=my_guild)
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Sync error: {e}")
        
    print(f'Connected as {bot.user} !')

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
    Global error handler for all app commands (slash commands).
    """
    if interaction.response.is_done():
        await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
    print(f"App command error: {error}")

#------------------------------------------------------
#           Slash Commands 
#------------------------------------------------------
@bot.tree.command(name="add", description="Add a player to the schedule")
async def add(interaction: discord.Interaction,
               member: discord.Member, 
               game: Literal['League of Legend'], 
               group: str):
    """
    Slash command to add a player to the database.
    
    Args:
        interaction: The interaction object.
        member: The Discord member to add.
        game: The game to register for.
        group: The group name.
    """
    await interaction.response.send_message("Players added!")
    await add_player(interaction, member, game, group, conn)


@bot.tree.command(name="list", description="Show all registered players")
async def list_players(interaction: discord.Interaction):
    """
    Slash command to list all registered players and teams.
    """
    await display_team(interaction, conn)
#------------------------------------------------------
#           LAUNCH
#------------------------------------------------------
if TOKEN:
    try:
        # start the bot
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot stopped by user...")
    finally:
        # final safety save
        if conn:
            conn.commit()
            conn.close()
            print("Database saved. 👋")
else:
    print("ERROR : No Token found !")