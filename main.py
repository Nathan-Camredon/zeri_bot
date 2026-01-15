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
from modules.player_management import add_player, remove_player, add_availability
from modules.affichages import display_team
#------------------------------------------------------
#           VARIABLES
#------------------------------------------------------

day_conversion = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}
#day_int =  day_conversion[day]

#------------------------------------------------------
#           TABLE SQL
#------------------------------------------------------
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        discord_id INTEGER PRIMARY KEY,
        username TEXT,
        game TEXT,
        team TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS availability (
        discord_id INTEGER,
        day INTEGER,
        start_time INTEGER,
        end_time INTEGER
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
    
    # 1. Copy global commands to the specific guild
    bot.tree.copy_global_to(guild=my_guild)
    
    # 2. Sync guild commands (updates the guild instantly)
    try:
        synced = await bot.tree.sync(guild=my_guild)
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}.")
    except Exception as e:
        print(f"Guild Sync error: {e}")

    # 3. Clear and sync global commands to remove "ghost" duplicates
    # (Only do this if you want to be strictly guild-only due to dev)
    bot.tree.clear_commands(guild=None)
    try:
        await bot.tree.sync(guild=None)
        print("Cleared global commands.")
    except Exception as e:
        print(f"Global Sync error: {e}")
        
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
@bot.tree.command(name="add", description="Ajouter un joueur au planning")
async def add(interaction: discord.Interaction,
               member: discord.Member, 
               game: Literal['League of Legends'], 
               team: str):
    """
    Slash command to add a player to the database.
    
    Args:
        interaction: The interaction object.
        member: The Discord member to add.
        game: The game to register for.
        team: The team name.
    """
    await interaction.response.send_message("Joueur ajouté !")
    await add_player(interaction, member, game, team, conn)


@bot.tree.command(name="remove", description="Retirer un joueur de la base de données")
async def remove(interaction: discord.Interaction, member: discord.Member):
    """
    Slash command to remove a player from the database.
    
    Args:
        interaction: The interaction object.
        member: The Discord member to remove.
    """
    await interaction.response.send_message("Suppression du joueur...")
    await remove_player(interaction, member, conn)


#------------------------------------------------------
#           Availability Commands
#------------------------------------------------------
availability_group = app_commands.Group(name="availability", description="Gérer les disponibilités")

@availability_group.command(name="add", description="Ajouter un créneau de disponibilité")
async def availability_add(interaction: discord.Interaction, 
                           day: Literal['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 
                           start_time: int, 
                           end_time: int):
    """
    Slash command to add availability for a specific day.
    
    Args:
        interaction: The interaction object.
        day: The day of the week.
        start_time: Start hour (0-23).
        end_time: End hour (0-23).
    """
    day_int = day_conversion[day]
    # Simple validation: Check if hours are within valid range
    if not (0 <= start_time <= 23) or not (0 <= end_time <= 23):
         await interaction.response.send_message("Les heures doivent être comprises entre 0 et 23.", ephemeral=True)
         return
    # Simple validation: Check if start time is before end time
    if start_time >= end_time:
         await interaction.response.send_message("L'heure de début doit être avant l'heure de fin.", ephemeral=True)
         return

    await interaction.response.send_message("Traitement de la disponibilité...")
    await add_availability(interaction, interaction.user, day_int, start_time, end_time, conn)

bot.tree.add_command(availability_group)


@bot.tree.command(name="list", description="Afficher tous les joueurs enregistrés")
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
        # Start the bot using the token from .env
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot stopped by user...")
    finally:
        # Final safety save on exit
        if conn:
            conn.commit()
            conn.close()
            print("Database saved. 👋")
else:
    print("ERROR : No Token found !")