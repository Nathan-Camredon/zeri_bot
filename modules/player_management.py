#------------------------------------------------------
#           Import
#------------------------------------------------------
import sqlite3
import discord

#------------------------------------------------------
#           Functions
#------------------------------------------------------

async def add_player(interaction, member, game, team, conn):
    """
    Adds a player to the database.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member to add.
        game: The game the player plays.
        team: The team the player belongs to.
        conn: The database connection.
    """
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO players (discord_id, username, game, team)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (member.id, member.name, game, team.lower()))
        conn.commit()
        print(f"Success: {member.name} added to DB.")
    except Exception as e:
        print(f"Error in add_player: {e}")
        # Global handler might catch this if it propagates, but since we catch it here:
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Échec de l'ajout du joueur. Veuillez réessayer.", ephemeral=True)
            else:
                await interaction.followup.send("Échec de l'ajout du joueur. Veuillez réessayer.", ephemeral=True)
        except Exception:
            pass

async def remove_player(interaction, member, conn):
    """
    Removes a player from the database.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member to remove.
        conn: The database connection.
    """
    try:
        cursor = conn.cursor()
        query = "DELETE FROM players WHERE discord_id = ?"
        cursor.execute(query, (member.id,))
        player_deleted = cursor.rowcount > 0

        # Also remove from availability table (do this regardless of player table result to ensure cleanup)
        query_availability = "DELETE FROM availability WHERE discord_id = ?"
        cursor.execute(query_availability, (member.id,))
        availability_deleted = cursor.rowcount > 0

        conn.commit()
        
        if player_deleted:
            print(f"Success: {member.name} removed from DB.")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"{member.name} a été supprimé avec succès.", ephemeral=True)
            else:
                await interaction.followup.send(f"{member.name} a été supprimé avec succès.", ephemeral=True)
        elif availability_deleted:
             # Case where player wasn't in 'players' but had leftover availability
             print(f"Success: {member.name} availability cleaned up.")
             if not interaction.response.is_done():
                await interaction.response.send_message(f"{member.name} n'était pas dans la liste des joueurs, mais ses disponibilités ont été nettoyées.", ephemeral=True)
             else:
                await interaction.followup.send(f"{member.name} n'était pas dans la liste des joueurs, mais ses disponibilités ont été nettoyées.", ephemeral=True)
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"{member.name} n'a pas été trouvé dans la base de données.", ephemeral=True)
            else:
                await interaction.followup.send(f"{member.name} n'a pas été trouvé dans la base de données.", ephemeral=True)
        return


    except Exception as e:
        print(f"Error in remove_player: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Échec de la suppression du joueur. Veuillez réessayer.", ephemeral=True)
            else:
                await interaction.followup.send("Échec de la suppression du joueur. Veuillez réessayer.", ephemeral=True)
        except Exception:
            pass

async def add_availability(interaction, member, day, start_time, end_time, conn):
    """
    Adds player availability to the database.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member.
        day: Day of the week (0-6).
        start_time: Start hour (0-23).
        end_time: End hour (0-23).
        conn: The database connection.
    """
    try:
        cursor = conn.cursor()

        # Check if player exists
        cursor.execute("SELECT 1 FROM players WHERE discord_id = ?", (member.id,))
        if cursor.fetchone() is None:
            if not interaction.response.is_done():
                 await interaction.response.send_message(f"Erreur : Vous n'êtes pas enregistré.", ephemeral=True)
            else:
                 await interaction.followup.send(f"Erreur : Vous n'êtes pas enregistré.", ephemeral=True)
            return
        
        # Check for existing availability. 
        # Currently, we enforce one slot per day per user by deleting any previous entry for that day.
        # Future improvement: Allow multiple slots or update existing ones.
        
        cursor.execute("DELETE FROM availability WHERE discord_id = ? AND day = ?", (member.id, day))
        
        query = """
            INSERT INTO availability (discord_id, day, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (member.id, day, start_time, end_time))
        conn.commit()
        print(f"Success: Availability added for {member.name} on day {day}.")
        
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Disponibilité ajoutée pour {member.name} !", ephemeral=True)
        else:
            await interaction.followup.send(f"Disponibilité ajoutée pour {member.name} !", ephemeral=True)
            
    except Exception as e:
        print(f"Error in add_availability: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Échec de l'ajout de la disponibilité. Veuillez réessayer.", ephemeral=True)
            else:
                await interaction.followup.send("Échec de l'ajout de la disponibilité. Veuillez réessayer.", ephemeral=True)
        except Exception:
            pass
