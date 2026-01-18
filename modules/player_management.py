#------------------------------------------------------
#           Imports
#------------------------------------------------------
import sqlite3
import discord

#------------------------------------------------------
#           Functions
#------------------------------------------------------

from modules.utils import check_permission_and_respond

async def add_player(interaction, member, game, team, conn):
    """
    Adds a player to the database for the specific guild.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member to add.
        game: The game the player plays.
        team: The team the player belongs to.
        conn: The database connection.
    """
    if not await check_permission_and_respond(interaction):
        return

    if not interaction.guild_id:
         await interaction.response.send_message("Cette commande doit être utilisée sur un serveur.", ephemeral=True)
         return

    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO players (discord_id, guild_id, username, game, team)
            VALUES (?, ?, ?, ?, ?)
        """
        # Lowercase team name for consistency within guild
        cursor.execute(query, (member.id, interaction.guild_id, member.name, game, team.strip().lower()))
        conn.commit()
        print(f"Success: {member.name} added to DB (Guild {interaction.guild_id}).")
    except Exception as e:
        print(f"Error in add_player: {e}")
        try:
            msg = "Échec de l'ajout du joueur. Veuillez réessayer."
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass

async def remove_player(interaction, member, conn):
    """
    Removes a player from the database for the specific guild.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member to remove.
        conn: The database connection.
    """
    if not await check_permission_and_respond(interaction):
        return

    if not interaction.guild_id:
         await interaction.response.send_message("Cette commande doit être utilisée sur un serveur.", ephemeral=True)
         return

    try:
        cursor = conn.cursor()
        # Only remove from THIS guild
        query = "DELETE FROM players WHERE discord_id = ? AND guild_id = ?"
        cursor.execute(query, (member.id, interaction.guild_id))
        player_deleted = cursor.rowcount > 0

        # Note: We DO NOT remove availability because it is GLOBAL.
        # Unless the user is not in ANY guild anymore? 
        # For simplicity (V2.0 plan), we keep availability global and persistent.
        
        conn.commit()
        
        msg = ""
        if player_deleted:
            print(f"Success: {member.name} removed from DB (Guild {interaction.guild_id}).")
            msg = f"{member.name} a été supprimé de l'équipe avec succès."
        else:
            msg = f"{member.name} n'a pas été trouvé dans l'équipe de ce serveur."
            
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)
        return

    except Exception as e:
        print(f"Error in remove_player: {e}")
        try:
            msg = "Échec de la suppression du joueur. Veuillez réessayer."
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass

async def add_availability(interaction, member, day, start_time, end_time, conn):
    """
    Adds player availability to the database (Global).
    
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

        # Check if player exists in AT LEAST ONE guild (optional validation?)
        # Or just let them add availability even if not in a team yet?
        # Let's check if they are in THIS guild to be polite, or just allow it.
        # To strictly follow "User must be registered", we check if they are in 'players' table for ANY guild?
        # Or current guild? Logic: "You must be registered (in a team) to add availability".
        
        # New Validation: Check if user is in 'players' table (ignoring guild for now, or check current guild?)
        # If we check current guild, then a user must be added to team first. That makes sense.
        if interaction.guild_id:
             cursor.execute("SELECT 1 FROM players WHERE discord_id = ? AND guild_id = ?", (member.id, interaction.guild_id))
             if cursor.fetchone() is None:
                # Fallback: Check if they are in ANY guild? 
                # If they are not in this guild, they shouldn't be managing stuff here maybe?
                # But availability is global... 
                # Decision: Allow adding availability if they are registered in AT LEAST one place?
                # Simpler: Require registration in CURRENT guild to interact.
                msg = "Erreur : Vous n'êtes pas enregistré dans une équipe sur ce serveur."
                if not interaction.response.is_done():
                     await interaction.response.send_message(msg, ephemeral=True)
                else:
                     await interaction.followup.send(msg, ephemeral=True)
                return
        
        # Check for existing availability. 
        cursor.execute("DELETE FROM availability WHERE discord_id = ? AND day = ?", (member.id, day))
        
        query = """
            INSERT INTO availability (discord_id, day, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (member.id, day, start_time, end_time))
        conn.commit()
        print(f"Success: Availability added for {member.name} on day {day}.")
        
        msg = f"Disponibilité ajoutée pour {member.name} (Global) !"
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)
            
    except Exception as e:
        print(f"Error in add_availability: {e}")
        try:
            msg = "Échec de l'ajout de la disponibilité. Veuillez réessayer."
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass
