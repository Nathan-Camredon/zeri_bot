import sqlite3
import datetime
import discord
from modules.planning import calculate_common_availability

async def schedule_session(interaction, team, day_input, start_hour, end_hour, conn):
    """
    Schedules a session for a team using day name and integer hours.
    day_input: "Lundi", "Mardi", etc.
    start_hour: int (0-23)
    end_hour: int (0-23)
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
        # If the requested time is already passed today, assume next week? 
        # Or let them schedule for later today? 
        # Let's say if start_hour < current_hour, it's next week.
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
            # Check overlap: max(start1, start2) < min(end1, end2)
            # Session: start_hour to end_hour
            # Slot: slot_start to slot_end
            if max(start_hour, slot_start) < min(end_hour, slot_end):
                 # Intersection found. Check if it covers the WHOLE session?
                 # User might want to play 20-23 even if common is 20-22.
                 # Let's say if there is ANY overlap, it's "okay" but warn if partial?
                 # Logic requested: "compatible" usually means fully within.
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
            # r[1] is Date (DD/MM/YYYY)
            # r[2] is Time (e.g., "20h - 22h")
            # We need to construct a datetime object for sorting and filtering.
            # Parse Date
            dt_date = datetime.datetime.strptime(r[1], "%d/%m/%Y")
            
            # Parse Start Hour from Time string
            # Expected format: "20h - 22h" or anything starting with integer
            # Let's try to extract the first integer
            import re
            match = re.search(r"(\d+)", r[2])
            start_hour = int(match.group(1)) if match else 0
            
            # Combine
            dt = dt_date.replace(hour=start_hour, minute=0)
            
            parsed_rows.append((dt, r))
        except Exception as e:
            print(f"Error parsing session row {r}: {e}")
            continue
            
    parsed_rows.sort(key=lambda x: x[0])
    
    now = datetime.datetime.now()
    
    for dt, row in parsed_rows:
        # Filter past sessions? (Allow sessions from earlier today to show?)
        # Let's hide only if date < today or (date==today and time passed)
        if dt < now:
            # Keep if it's plainly today but hour passed? Maybe just keep until midnight.
            # If session was 20h and now is 21h, it's technically "current/past".
            # Let's strict hide past sessions to be consistent with cleanup
            continue
            
        sessions_txt += f"• **{row[1]}** : {row[2]} (ID: {row[0]})\n"
        
    if not sessions_txt:
        sessions_txt = "Aucune session à venir (anciennes sessions masquées)."
        
    embed.description = sessions_txt
    await interaction.response.send_message(embed=embed)

async def delete_session(interaction, session_id, conn):
    """
    Deletes a session by ID.
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
