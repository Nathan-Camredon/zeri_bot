#------------------------------------------------------
#           Import
#------------------------------------------------------
import sqlite3
import discord
#------------------------------------------------------
#           Functions
#------------------------------------------------------
async def display_team(interaction, conn):
    """
    Fetches and displays the list of players grouped by game and team.
    
    Args:
        interaction: The Discord interaction object.
        conn: The database connection.
    """
    cursor = conn.cursor()
    try:
        # Select all players ordered by game and team for grouping
        cursor.execute("SELECT username, game, team FROM players ORDER BY game, team")
        data = cursor.fetchall()
        schedule = {}
        
        # Organize data into a nested dictionary: schedule[game][team] = [list of usernames]
        for row in data: 
            username, game, team = row
            team_display = team.title()
            
            if game not in schedule:
                schedule[game] = {}
            if team_display not in schedule[game]:
                schedule[game][team_display] = []
            schedule[game][team_display].append(username)
            
        embed = discord.Embed(title="Nos Équipes", color=discord.Color.blue())
        for game in schedule:
            game_description = ""
            for team in schedule[game]:
                # Format player list with newlines
                players = "\n".join(schedule[game][team])
                game_description += f"**{team}**\n{players}\n\n"
            embed.add_field(name=game, value=game_description, inline=False)
                
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Error in display_team: {e}")
        if interaction.response.is_done():
             await interaction.followup.send("Impossible d'afficher les équipes. Veuillez réessayer.", ephemeral=True)
        else:
             await interaction.response.send_message("Impossible d'afficher les équipes. Veuillez réessayer.", ephemeral=True)
