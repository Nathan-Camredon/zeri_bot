#------------------------------------------------------
#           Import
#------------------------------------------------------
import sqlite3
import discord
#------------------------------------------------------
#           Fonction
#------------------------------------------------------

def add_player(interaction, membre, jeu, groupe, conn):
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO joueurs (discord_id, pseudo, jeu, groupe)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (membre.id, membre.name, jeu, groupe))
        conn.commit()
        print(f"Succès : {membre.name} ajouté à la DB.")
    except Exception as e:
        print(f"Erreur dans add_player : {e}")