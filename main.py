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
from modules.affichages import affichage_team
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
#jour_int =  conversion_jours[jour]

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
    GUILD_ID = os.getenv('GUILD_ID')
    mon_serveur = discord.Object(id=int(GUILD_ID))
    bot.tree.copy_global_to(guild=mon_serveur)
    try:
        synced = await bot.tree.sync(guild=mon_serveur)
        print(f"Synchronisé {len(synced)} commande(s).")
    except Exception as e:
        print(f"Erreur de synchro : {e}")
        
    print(f'Connecté en tant que {bot.user} !')

#------------------------------------------------------
#           Commandes Slash 
#------------------------------------------------------
@bot.tree.command(name="add", description="Ajouter un joueur au planning")
async def add(interaction: discord.Interaction,
               membre: discord.Member, 
               jeu: Literal['League of Legend'], 
               groupe: str):
    await interaction.response.send_message("Joueurs add!")
    add_player(interaction, membre, jeu, groupe, conn)


@bot.tree.command(name="liste", description="Montre tout les joeurs inscrit")
async def liste(interaction: discord.Interaction):
    await affichage_team(interaction, conn)
#------------------------------------------------------
#           LANCEMENT
#------------------------------------------------------
if TOKEN:
    try:
        # lance le bot
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Arrêt du bot par l'utilisateur...")
    finally:
        # dernière sauvegarde de sécurité
        if conn:
            conn.commit()
            conn.close()
            print("Base de données sauvegardéet. 👋")
else:
    print("ERREUR : Pas de Token trouvé !")