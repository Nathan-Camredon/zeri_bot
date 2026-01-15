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
        cursor.execute(query, (member.id, member.name, game, team))
        conn.commit()
        print(f"Success: {member.name} added to DB.")
    except Exception as e:
        print(f"Error in add_player: {e}")
        # Global handler might catch this if it propagates, but since we catch it here:
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Failed to add player. Please try again.", ephemeral=True)
            else:
                await interaction.followup.send("Failed to add player. Please try again.", ephemeral=True)
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
        if cursor.rowcount == 0:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"{member.name} was not found in the database.", ephemeral=True)
            else:
                await interaction.followup.send(f"{member.name} was not found in the database.", ephemeral=True)
            return

        # Also remove from availability table
        query_availability = "DELETE FROM availability WHERE discord_id = ?"
        cursor.execute(query_availability, (member.id,))

        conn.commit()
        print(f"Success: {member.name} removed from DB.")
        
        if not interaction.response.is_done():
            await interaction.response.send_message(f"{member.name} has been successfully removed.", ephemeral=True)
        else:
            await interaction.followup.send(f"{member.name} has been successfully removed.", ephemeral=True)
    except Exception as e:
        print(f"Error in remove_player: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Failed to remove player. Please try again.", ephemeral=True)
            else:
                await interaction.followup.send("Failed to remove player. Please try again.", ephemeral=True)
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
        
        # Check if availability already exists for this user and day to avoid duplicates? 
        # For now, let's just insert. The table doesn't have a unique constraint on (discord_id, day) yet.
        # Ideally we should probably delete previous availability for that day or allow multiple slots.
        # Let's assume one slot per day for simplicity as a start, deleting old one for that day.
        
        cursor.execute("DELETE FROM availability WHERE discord_id = ? AND day = ?", (member.id, day))
        
        query = """
            INSERT INTO availability (discord_id, day, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (member.id, day, start_time, end_time))
        conn.commit()
        print(f"Success: Availability added for {member.name} on day {day}.")
        
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Availability added for {member.name}!", ephemeral=True)
        else:
            await interaction.followup.send(f"Availability added for {member.name}!", ephemeral=True)
            
    except Exception as e:
        print(f"Error in add_availability: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("Failed to add availability. Please try again.", ephemeral=True)
            else:
                await interaction.followup.send("Failed to add availability. Please try again.", ephemeral=True)
        except Exception:
            pass
