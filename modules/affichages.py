#------------------------------------------------------
#           Import
#------------------------------------------------------
import sqlite3
import discord


#------------------------------------------------------
#           Fonction
#------------------------------------------------------
async def affichage_team(interaction, conn):
    cursor = conn.cursor()
    cursor.execute("Select pseudo, jeu, groupe FROM joueurs ORDER BY jeu, groupe")
    data = cursor.fetchall()
    planning = {}
    
    for row in data: 
        pseudo, jeu, groupe = row
        if jeu not in planning:
            planning[jeu] = {}
        if groupe not in planning[jeu]:
            planning[jeu][groupe] = []
        planning[jeu][groupe].append(pseudo)
        
    embed = discord.Embed(title="Nos équipes", color=discord.Color.blue())
    for jeu in planning:
        description_jeu = ""
        for groupe in planning[jeu]:
            joueurs = "\n".join(planning[jeu][groupe])
            description_jeu += f"**{groupe}**\n{joueurs}\n\n"
        embed.add_field(name=jeu, value=description_jeu, inline=False)
            
    await interaction.response.send_message(embed=embed)
