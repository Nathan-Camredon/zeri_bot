import discord
from discord.ext import tasks
import datetime
import os
from modules.database import conn
from modules.planning import calculate_common_availability

def start_tasks(bot):
    """
    Starts all background tasks.

    Args:
        bot: The Discord bot instance.
    """
    # Attach bot instance to task functions to allow access within the loop
    daily_cleanup.bot = bot
    weekly_schedule.bot = bot
    availability_reminder.bot = bot

    if not daily_cleanup.is_running():
        daily_cleanup.start()
        print("Daily cleanup task started.")
        
    if not weekly_schedule.is_running():
        weekly_schedule.start()
        print("Weekly schedule task started.")
        
    if not availability_reminder.is_running():
        availability_reminder.start()
        print("Availability reminder task started.")

@tasks.loop(time=datetime.time(hour=0, minute=0))
async def daily_cleanup():
    """
    Cleans up the database every day at midnight.
    Deletes entries for the previous day.
    """
    # Calculate yesterday's index
    today = datetime.datetime.now()
    yesterday_index = (today.weekday() - 1) % 7
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    previous_day_name = days[yesterday_index]
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM availability WHERE day = ?", (yesterday_index,))
        conn.commit()
        print(f"Database cleaned for {previous_day_name}.")
        
        # Optional: Notify configured channels? 
        # For V2, we might just log it to console to avoid spamming channels daily.
        # Or notify only in guilds that have explicity set up something?
        # Decided: Console log is enough for cleanup.
            
    except Exception as e:
        print(f"Error in daily_cleanup: {e}")

@tasks.loop(time=datetime.time(hour=12, minute=0))
async def weekly_schedule():
    """
    Posts the weekly schedule every Monday at 12:00.
    """
    today = datetime.datetime.now()
    # Check if it's Monday (0).
    if today.weekday() != 0:
        return

    print("Running weekly schedule generation...")
    
    if not hasattr(weekly_schedule, 'bot'):
        print("Error: Bot not attached to weekly_schedule.")
        return
        
    bot = weekly_schedule.bot
    cursor = conn.cursor()

    # 1. Get all Guild Configurations
    cursor.execute("SELECT guild_id, planning_channel_id, default_channel_id FROM guild_configs")
    guilds = cursor.fetchall()
    
    for guild_id, planning_chan_id, default_chan_id in guilds:
        target_channel_id = planning_chan_id if planning_chan_id else default_chan_id
        
        if not target_channel_id:
            continue # No channel configured for this guild
            
        channel = bot.get_channel(target_channel_id)
        if not channel:
            print(f"Channel {target_channel_id} not found for guild {guild_id}.")
            continue
            
        # 2. Get teams for this guild
        cursor.execute("SELECT DISTINCT team FROM players WHERE guild_id = ?", (guild_id,))
        teams = [row[0] for row in cursor.fetchall()]
        
        for team in teams:
            schedule = calculate_common_availability(team, guild_id, conn)
            if not schedule:
                continue
                
            embed = discord.Embed(
                title=f"📅 Emploi du temps - Équipe {team.title()}",
                description="Voici les créneaux communs pour la semaine :",
                color=discord.Color.green()
            )
            days_str = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            has_slots = False
            for day_idx, slots in schedule.items():
                if slots:
                    has_slots = True
                    slots_str = "\n".join([f"• {s[0]}h - {s[1]}h" for s in slots])
                    embed.add_field(name=days_str[day_idx], value=slots_str, inline=False)
            
            if not has_slots:
                embed.description = "Pas de créneaux communs trouvés pour cette semaine."
                embed.color = discord.Color.orange()
                
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending schedule for {team} in guild {guild_id}: {e}")

@tasks.loop(time=datetime.time(hour=18, minute=0))
async def availability_reminder():
    """
    Sends a reminder specific Sunday at 18:00 to users who haven't filled their availability.
    """
    today = datetime.datetime.now()
    # Check if it's Sunday (6)
    if today.weekday() != 6:
        return
        
    print("Running availability reminder...")
    
    if not hasattr(availability_reminder, 'bot'):
        print("Error: Bot not attached to availability_reminder.")
        return
    
    bot = availability_reminder.bot
    
    cursor = conn.cursor()
    # Get all DISTINCT players (users might be in multiple guilds)
    cursor.execute("SELECT DISTINCT discord_id, username FROM players")
    all_players = cursor.fetchall()
    
    for pid, username in all_players:
        # Check if they have availability for next week
        cursor.execute("SELECT 1 FROM availability WHERE discord_id = ?", (pid,))
        if cursor.fetchone() is None:
            # User has no availability set
            try:
                user = await bot.fetch_user(pid)
                if user:
                    await user.send(f"Salut {username} ! 👋\nCeci est un rappel : pense à remplir tes disponibilités pour la semaine à venir via la commande `/ajout_dispo` !")
                    print(f"Reminder sent to {username}.")
            except Exception as e:
                print(f"Could not send reminder to {username}: {e}")
