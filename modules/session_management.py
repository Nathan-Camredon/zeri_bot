import sqlite3
import datetime
import discord
import re
from modules.planning import calculate_common_availability

async def schedule_session(interaction, team, day_input, start_hour, end_hour, conn):
    """
    Schedules a session for a team.
    
    Args:
        interaction: Discord interaction.
        team (str): Team name.
        day_input (str): Day name (e.g., "Lundi").
        start_hour (int): Start hour (0-23).
        end_hour (int): End hour (0-23).
        conn: Database connection.
    """
    cursor = conn.cursor()
    team = team.strip().lower()

    # 1. Resolve Day Input to Date
    days_map = {
        "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, 
        "vendredi": 4, "samedi": 5, "dimanche": 6
    }
    target_day_index = days_map.get(day_input.lower())
    
    if target_day_index is None:
        await interaction.response.send_message(f"❌ Jour invalide : **{day_input}**. Utilisez Lundi, Mardi...", ephemeral=True)
        return
        
    # Calculate next occurrence
    today = datetime.datetime.now()
    current_day_index = today.weekday()
    
    days_ahead = target_day_index - current_day_index
    if days_ahead < 0: # Target day already passed this week
        days_ahead += 7
    elif days_ahead == 0: # Same day
        # If the requested time is already passed today, assume next week.
        if start_hour <= today.hour:
             days_ahead += 7
             
    target_date = today + datetime.timedelta(days=days_ahead)
    date_str = target_date.strftime("%d/%m/%Y")
    
    # 2. Check if team exists
    cursor.execute("SELECT 1 FROM players WHERE LOWER(team) = ?", (team,))
    if cursor.fetchone() is None:
        await interaction.response.send_message(f"⚠️ L'équipe **{team.title()}** n'existe pas.", ephemeral=True)
        return

    # 3. Availability Check (Warning only)
    warning_message = ""
    common_slots = calculate_common_availability(team, conn)
    
    # Check compatibility
    is_compatible = False
    if common_slots and target_day_index in common_slots:
        for slot_start, slot_end in common_slots[target_day_index]:
            # Simple check: if session time is fully within a common slot
            if start_hour >= slot_start and end_hour <= slot_end:
                is_compatible = True
                break
    
    if not is_compatible:
        warning_message = f"\n⚠️ **Attention** : Créneau ({day_input.title()} {start_hour}h-{end_hour}h) hors des disponibilités communes déclarées."

    # 4. Insert into DB
    try:
        # We store nice formatted strings for display
        time_display = f"{start_hour}h - {end_hour}h"
        cursor.execute("INSERT INTO sessions (team, date, time) VALUES (?, ?, ?)", (team, date_str, time_display))
        conn.commit()
        
        embed = discord.Embed(
            title=f"✅ Session planifiée - {team.title()}",
            description=f"📅 **Date** : {date_str} ({day_input.title()})\n🕒 **Heure** : {start_hour}h00 - {end_hour}h00{warning_message}",
            color=discord.Color.green() if not warning_message else discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Error scheduling session: {e}")
        await interaction.response.send_message("Erreur lors de la planification.", ephemeral=True)


async def list_sessions(interaction, team, conn):
    """
    Lists upcoming sessions for a team.
    
    Args:
        interaction: Discord interaction.
        team (str): Team name.
        conn: Database connection.
    """
    cursor = conn.cursor()
    team = team.strip().lower()
    
    cursor.execute("SELECT id, date, time FROM sessions WHERE LOWER(team) = ?", (team,))
    rows = cursor.fetchall()
    
    if not rows:
        await interaction.response.send_message(f"Aucune session prévue pour l'équipe **{team.title()}**.", ephemeral=True)
        return
        
    embed = discord.Embed(
        title=f"📅 Sessions prévues - {team.title()}",
        color=discord.Color.blue()
    )
    
    sessions_txt = ""
    parsed_rows = []
    
    for r in rows:
        try:
            # r[1] is Date (DD/MM/YYYY), r[2] is Time string
            dt_date = datetime.datetime.strptime(r[1], "%d/%m/%Y")
            
            # Extract start hour
            match = re.search(r"(\d+)", r[2])
            start_hour = int(match.group(1)) if match else 0
            
            # Combine to full datetime
            dt = dt_date.replace(hour=start_hour, minute=0)
            
            parsed_rows.append((dt, r))
        except Exception as e:
            print(f"Error parsing session row {r}: {e}")
            continue
            
    parsed_rows.sort(key=lambda x: x[0])
    
    now = datetime.datetime.now()
    
    for dt, row in parsed_rows:
        # Hide past sessions
        if dt < now:
            continue
            
        sessions_txt += f"• **{row[1]}** : {row[2]} (ID: {row[0]})\n"
        
    if not sessions_txt:
        sessions_txt = "Aucune session à venir (anciennes sessions masquées)."
        
    embed.description = sessions_txt
    await interaction.response.send_message(embed=embed)

async def delete_session(interaction, session_id, conn):
    """
    Deletes a session by ID.
    
    Args:
        interaction: Discord interaction.
        session_id (int): ID of the session to delete.
        conn: Database connection.
    """
    cursor = conn.cursor()
    
    # Check if session exists
    cursor.execute("SELECT team, date, time FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    
    if not row:
        await interaction.response.send_message(f"❌ Aucune session trouvée avec l'ID **{session_id}**.", ephemeral=True)
        return
        
    team, date, time = row
    
    try:
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        
        embed = discord.Embed(
            title="🗑️ Session supprimée",
            description=f"La session de l'équipe **{team.title()}** du **{date}** ({time}) a été supprimée.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Error deleting session: {e}")
        await interaction.response.send_message("Erreur lors de la suppression.", ephemeral=True)
