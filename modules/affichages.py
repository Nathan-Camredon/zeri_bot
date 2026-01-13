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
        # Keeping DB columns in French as per plan: pseudo, jeu, groupe
        cursor.execute("Select pseudo, jeu, groupe FROM joueurs ORDER BY jeu, groupe")
        data = cursor.fetchall()
        schedule = {}
        
        for row in data: 
            pseudo, game, group = row
            if game not in schedule:
                schedule[game] = {}
            if group not in schedule[game]:
                schedule[game][group] = []
            schedule[game][group].append(pseudo)
            
        embed = discord.Embed(title="Our Teams", color=discord.Color.blue())
        for game in schedule:
            game_description = ""
            for group in schedule[game]:
                players = "\n".join(schedule[game][group])
                game_description += f"**{group}**\n{players}\n\n"
            embed.add_field(name=game, value=game_description, inline=False)
                
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Error in display_team: {e}")
        if interaction.response.is_done():
             await interaction.followup.send("Failed to display team. Please try again.", ephemeral=True)
        else:
             await interaction.response.send_message("Failed to display team. Please try again.", ephemeral=True)
