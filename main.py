#------------------------------------------------------
#           Import
#------------------------------------------------------
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Literal

# Modules
from modules.database import conn, init_database
from modules.player_management import add_player, remove_player, add_availability
from modules.affichages import display_team
from modules.tasks import start_tasks
from modules.planning import calculate_common_availability, get_player_availability
from modules.session_management import schedule_session, list_sessions

#------------------------------------------------------
#           VARIABLES
#------------------------------------------------------
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

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
    # 1. Initialize Database
    init_database()

    # 2. Start Background Tasks
    start_tasks(bot)

    GUILD_ID = os.getenv('GUILD_ID')
    my_guild = discord.Object(id=int(GUILD_ID))
    
    # 3. Copy global commands to the specific guild
    bot.tree.copy_global_to(guild=my_guild)
    
    # 4. Sync guild commands (updates the guild instantly)
    try:
        synced = await bot.tree.sync(guild=my_guild)
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}.")
    except Exception as e:
        print(f"Guild Sync error: {e}")

    # 5. Clear and sync global commands to remove "ghost" duplicates
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
    """
    await interaction.response.send_message("Joueur ajouté !")
    await add_player(interaction, member, game, team, conn)


@bot.tree.command(name="remove", description="Retirer un joueur de la base de données")
async def remove(interaction: discord.Interaction, member: discord.Member):
    """
    Slash command to remove a player from the database.
    """
    await interaction.response.send_message("Suppression du joueur...")
    await remove_player(interaction, member, conn)


#------------------------------------------------------
#           Availability Commands
#------------------------------------------------------
availability_group = app_commands.Group(name="availability", description="Gérer les disponibilités")

@availability_group.command(name="add", description="Ajouter un créneau de disponibilité")
async def availability_add(interaction: discord.Interaction, 
                           day: Literal['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                           start_time: int, 
                           end_time: int):
    """
    Slash command to add availability for a specific day.
    """
    # Use list index for day conversion
    try:
        day_int = DAYS.index(day)
    except ValueError:
        await interaction.response.send_message("Jour invalide.", ephemeral=True)
        return

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


#------------------------------------------------------
#           Session Commands
#------------------------------------------------------
session_group = app_commands.Group(name="session", description="Gérer les sessions de jeu")

@session_group.command(name="add", description="Planifier une session de jeu")
async def session_add(interaction: discord.Interaction, team: str, date: str, time: str):
    """
    Slash command to schedule a session.
    Args:
        team: Team name
        date: DD/MM/YYYY
        time: HH:MM
    """
    await schedule_session(interaction, team, date, time, conn)

@session_group.command(name="list", description="Voir les prochaines sessions d'une équipe")
async def session_list(interaction: discord.Interaction, team: str):
    """
    Slash command to list upcoming sessions.
    """
    await list_sessions(interaction, team, conn)

bot.tree.add_command(session_group)


@bot.tree.command(name="disponibilite", description="Afficher les disponibilités pour une équipe ou un joueur")
async def disponibilite(interaction: discord.Interaction, team: str = None, member: discord.Member = None):
    """
    Slash command to show availability.
    """
    # Import locally to avoid circular imports if needed, though simpler to use global
    from modules.planning import calculate_common_availability, get_player_availability

    if team is None and member is None:
        await interaction.response.send_message("❌ Veuillez spécifier une **équipe** ou un **joueur**.", ephemeral=True)
        return

    await interaction.response.defer()
    
    schedule = None
    title = ""
    description = ""
    
    if team:
        schedule = calculate_common_availability(team, conn)
        title = f"📅 Disponibilités communes - Équipe {team.title()}"
        description = "Voici les créneaux où tous les membres sont disponibles :"
        if schedule is None:
             await interaction.followup.send(f"⚠️ L'équipe **{team}** n'existe pas ou n'a pas de membres.")
             return
             
    elif member:
        # Check if user exists in DB first (optional but good UI)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM players WHERE discord_id = ?", (member.id,))
        res = cursor.fetchone()
        if not res:
             await interaction.followup.send(f"⚠️ Le joueur **{member.display_name}** n'est pas inscrit dans la base.")
             return
             
        schedule = get_player_availability(member.id, conn)
        title = f"📅 Disponibilités - {member.display_name}"
        description = "Voici les créneaux disponibles :"

    # Display Logic (Shared)
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )
    
    days_str = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    has_slots = False
    
    for day_idx, slots in schedule.items():
        if slots:
            has_slots = True
            slots_str = "\n".join([f"• {s[0]}h - {s[1]}h" for s in slots])
            embed.add_field(name=days_str[day_idx], value=slots_str, inline=False)
    
    if not has_slots:
        embed.description = "❌ Aucun créneau trouvé."
        embed.color = discord.Color.red()
        
    await interaction.followup.send(embed=embed)


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