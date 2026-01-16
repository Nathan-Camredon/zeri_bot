import sqlite3
import datetime
import discord
from modules.planning import calculate_common_availability

async def schedule_session(interaction, team, date_str, time_str, conn):
    """
    Schedules a session for a team.
    Date format: DD/MM/YYYY
    Time format: HH:MM
    """
    cursor = conn.cursor()
    team = team.lower()

    # 1. Parse Date and Time
    try:
        session_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        session_time = datetime.datetime.strptime(time_str, "%H:%M")
        
        # Get day of week (0=Monday, ... 6=Sunday)
        day_of_week = session_date.weekday()
        start_hour = session_time.hour
        end_hour = start_hour + 2 # Default 2 hours duration
        
    except ValueError:
        await interaction.response.send_message("❌ Format invalide. Date: JJ/MM/AAAA, Heure: HH:MM", ephemeral=True)
        return

    # 2. Check if team exists
    cursor.execute("SELECT 1 FROM players WHERE LOWER(team) = ?", (team,))
    if cursor.fetchone() is None:
        await interaction.response.send_message(f"⚠️ L'équipe **{team.title()}** n'existe pas.", ephemeral=True)
        return

    # 3. Availability Check (Warning only)
    warning_message = ""
    common_slots = calculate_common_availability(team, conn)
    
    # Check if the proposed slot falls within any common slot for that day
    is_compatible = False
    if common_slots and day_of_week in common_slots:
        for slot_start, slot_end in common_slots[day_of_week]:
            # Simple check: Does the session fit entirely?
            # Session: start_hour to start_hour + 2
            # Slot: slot_start to slot_end
            if start_hour >= slot_start and end_hour <= slot_end:
                is_compatible = True
                break
    
    if not is_compatible:
        days_str = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        day_name = days_str[day_of_week]
        warning_message = f"\n⚠️ **Attention** : Créneau ({day_name} {time_str}) hors des disponibilités communes déclarées."

    # 4. Insert into DB
    try:
        cursor.execute("INSERT INTO sessions (team, date, time) VALUES (?, ?, ?)", (team, date_str, time_str))
        conn.commit()
        
        embed = discord.Embed(
            title=f"✅ Session planifiée - {team.title()}",
            description=f"📅 **Date** : {date_str}\n🕒 **Heure** : {time_str}{warning_message}",
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
    team = team.lower()
    
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
    # Sort by date? (Basic string sort works for YYYY-MM-DD but we have DD/MM/YYYY)
    # Let's convert to datetime for sorting
    parsed_rows = []
    for r in rows:
        try:
            dt = datetime.datetime.strptime(f"{r[1]} {r[2]}", "%d/%m/%Y %H:%M")
            parsed_rows.append((dt, r))
        except:
            continue
            
    parsed_rows.sort(key=lambda x: x[0])
    
    for dt, row in parsed_rows:
        # Filter past sessions?
        if dt < datetime.datetime.now():
            continue
            
        sessions_txt += f"• **{row[1]}** à **{row[2]}** (ID: {row[0]})\n"
        
    if not sessions_txt:
        sessions_txt = "Aucune session à venir (anciennes sessions masquées)."
        
    embed.description = sessions_txt
    await interaction.response.send_message(embed=embed)
