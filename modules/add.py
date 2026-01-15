#------------------------------------------------------
#           Import
#------------------------------------------------------
import sqlite3
import discord
#------------------------------------------------------
#           Functions
#------------------------------------------------------

async def add_player(interaction, member, game, group, conn):
    """
    Adds a player to the database.
    
    Args:
        interaction: The Discord interaction object.
        member: The Discord member to add.
        game: The game the player plays.
        group: The group the player belongs to.
        conn: The database connection.
    """
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO joueurs (discord_id, pseudo, jeu, groupe)
            VALUES (?, ?, ?, ?)
        """
        # Using French column names (pseudo, jeu, groupe) as per schema
        cursor.execute(query, (member.id, member.name, game, group))
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