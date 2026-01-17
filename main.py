#------------------------------------------------------
#           Imports
#------------------------------------------------------
import os
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Local Modules
from modules.database import conn, init_database
from modules.player_management import add_player, remove_player, add_availability
from modules.affichages import display_team
from modules.tasks import start_tasks
from modules.planning import calculate_common_availability, get_player_availability
from modules.session_management import schedule_session, list_sessions, delete_session

#------------------------------------------------------
#           Configuration & Variables
#------------------------------------------------------
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

#------------------------------------------------------
#           Events
#------------------------------------------------------
@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready. 
    Syncs the slash commands.
    """
    # 1. Initialize Database
    init_database()

    # 2. Start Background Tasks
    start_tasks(bot)
    
    if GUILD_ID:
        my_guild = discord.Object(id=int(GUILD_ID))
        
        # 3. Copy global commands to the specific guild to insure instant updates during dev
        bot.tree.copy_global_to(guild=my_guild)
        
        # 4. Sync guild commands
        try:
            synced = await bot.tree.sync(guild=my_guild)
            print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}.")
        except Exception as e:
            print(f"Guild Sync error: {e}")

        # 5. Clear global commands to avoid duplicates ("ghost commands")
        # useful if we previously synced global commands and now want to restrict to guild only.
        bot.tree.clear_commands(guild=None)
        try:
            await bot.tree.sync(guild=None)
            print("Cleared global commands.")
        except Exception as e:
            print(f"Global Sync error: {e}")
    else:
        print("Warning: GUILD_ID not found in .env, skipping guild sync.")
        
    print(f'Connected as {bot.user}!')

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
    Global error handler for all app commands (slash commands).
    """
    if interaction.response.is_done():
        await interaction.followup.send(f"Une erreur est survenue : {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Une erreur est survenue : {error}", ephemeral=True)
    print(f"App command error: {error}")

#------------------------------------------------------
#           Slash Commands : Player Management
#------------------------------------------------------
@bot.tree.command(name="ajouter", description="Ajouter un joueur au planning")
async def add(interaction: discord.Interaction,
               member: discord.Member, 
               game: Literal['League of Legends'], 
               team: str):
    """
    Slash command to add a player to the database.
    """
    await interaction.response.send_message("Joueur ajouté !")
    await add_player(interaction, member, game, team, conn)


@bot.tree.command(name="retirer", description="Retirer un joueur de la base de données")
async def remove(interaction: discord.Interaction, member: discord.Member):
    """
    Slash command to remove a player from the database.
    """
    await interaction.response.send_message("Suppression du joueur...")
    await remove_player(interaction, member, conn)


#------------------------------------------------------
#           Slash Commands : Availability
#------------------------------------------------------
@bot.tree.command(name="ajout_dispo", description="Ajouter un créneau de disponibilité")
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

    # Validation: Check range 0-23
    if not (0 <= start_time <= 23) or not (0 <= end_time <= 23):
         await interaction.response.send_message("Les heures doivent être comprises entre 0 et 23.", ephemeral=True)
         return
         
    # Validation: Check consistency
    if start_time >= end_time:
         await interaction.response.send_message("L'heure de début doit être avant l'heure de fin.", ephemeral=True)
         return

    await interaction.response.send_message("Traitement de la disponibilité...")
    await add_availability(interaction, interaction.user, day_int, start_time, end_time, conn)


#------------------------------------------------------
#           Slash Commands : Sessions
#------------------------------------------------------
@bot.tree.command(name="planifier_session", description="Planifier une session de jeu")
async def session_add(interaction: discord.Interaction, team: str, day: str, start: int, end: int):
    """
    Slash command to schedule a session.
    """
    await schedule_session(interaction, team, day, start, end, conn)

@bot.tree.command(name="liste_sessions", description="Voir les prochaines sessions d'une équipe")
async def session_list(interaction: discord.Interaction, team: str):
    """
    Slash command to list upcoming sessions.
    """
    await list_sessions(interaction, team, conn)

@bot.tree.command(name="supprimer_session", description="Supprimer une session par son ID")
async def session_delete(interaction: discord.Interaction, id: int):
    """
    Slash command to delete a session.
    """
    await delete_session(interaction, id, conn)


#------------------------------------------------------
#           Slash Commands : General Views
#------------------------------------------------------
@bot.tree.command(name="voir_dispo", description="Afficher les disponibilités pour une équipe ou un joueur")
async def disponibilite(interaction: discord.Interaction, team: str = None, member: discord.Member = None):
    """
    Slash command to show availability.
    """
    # Import locally to avoid circular imports? 
    # Not strictly necessary if imports are well organized, but keeping it safe as in original.
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
        # Check if user exists in DB
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM players WHERE discord_id = ?", (member.id,))
        res = cursor.fetchone()
        if not res:
             await interaction.followup.send(f"⚠️ Le joueur **{member.display_name}** n'est pas inscrit dans la base.")
             return
             
        schedule = get_player_availability(member.id, conn)
        title = f"📅 Disponibilités - {member.display_name}"
        description = "Voici les créneaux disponibles :"

    # Display Logic
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )
    
    has_slots = False
    
    # schedule is dict {day_int: [(start, end), ...]}
    for day_idx, slots in schedule.items():
        if slots:
            has_slots = True
            slots_str = "\n".join([f"• {s[0]}h - {s[1]}h" for s in slots])
            embed.add_field(name=DAYS[day_idx], value=slots_str, inline=False)
    
    if not has_slots:
        embed.description = "❌ Aucun créneau trouvé."
        embed.color = discord.Color.red()
        
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="liste_joueurs", description="Afficher tous les joueurs enregistrés")
async def list_players(interaction: discord.Interaction):
    """
    Slash command to list all registered players and teams.
    """
    await display_team(interaction, conn)

#------------------------------------------------------
#           Main Execution
#------------------------------------------------------
if __name__ == "__main__":
    if TOKEN:
        try:
            bot.run(TOKEN)
        except KeyboardInterrupt:
            print("Bot stopped by user...")
        finally:
            if conn:
                conn.commit()
                conn.close()
                print("Database saved. 👋")
    else:
        print("ERROR: No Token found!")
