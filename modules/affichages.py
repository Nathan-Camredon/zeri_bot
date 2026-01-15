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
    Fetches and displays the list of players grouped by game and team/group.
    """
    cursor = conn.cursor()
    try:
        # Using English columns: username, game, team
        cursor.execute("SELECT username, game, team FROM players ORDER BY game, team")
        data = cursor.fetchall()
        schedule = {}
        
        for row in data: 
            username, game, team = row
            if game not in schedule:
                schedule[game] = {}
            if team not in schedule[game]:
                schedule[game][team] = []
            schedule[game][team].append(username)
            
        embed = discord.Embed(title="Our Teams", color=discord.Color.blue())
        for game in schedule:
            game_description = ""
            for team in schedule[game]:
                players = "\n".join(schedule[game][team])
                game_description += f"**{team}**\n{players}\n\n"
            embed.add_field(name=game, value=game_description, inline=False)
                
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Error in display_team: {e}")
        if interaction.response.is_done():
             await interaction.followup.send("Failed to display team. Please try again.", ephemeral=True)
        else:
             await interaction.response.send_message("Failed to display team. Please try again.", ephemeral=True)
