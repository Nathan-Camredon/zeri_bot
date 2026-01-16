import discord
from discord.ext import tasks
import datetime
import os
from modules.database import conn

def start_tasks(bot):
    """
    Starts all background tasks.
    """
    # We attach the bot instance to the task function so it can access 'bot'
    # Alternatively, we can just pass 'bot' if we refactor 'daily_cleanup' to be a class method,
    # but for a standalone function in a module, we need to inject 'bot' somehow if we want to use 'bot.get_channel'.
    # A common pattern without classes is to use a global or pass it. 
    # Since tasks.loop is a decorator, 'self' isn't there. 
    # We'll set a module-level variable or use a hidden attribute.
    daily_cleanup.bot = bot
    
    # Pass bot to other tasks
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
    yesterday = (today.weekday() - 1) % 7
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    previous_day_name = days[yesterday]
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM availability WHERE day = ?", (yesterday,))
        conn.commit()
        print(f"Database cleaned for {previous_day_name}.")
        
        # Notify in channel
        if hasattr(daily_cleanup, 'bot'):
            bot = daily_cleanup.bot
            CHANNEL_ID = os.getenv('CHANNEL_ID')
            if CHANNEL_ID:
                try:
                    channel = bot.get_channel(int(CHANNEL_ID))
                    if channel:
                        await channel.send(f"🧹 Base de données nettoyée pour la journée de **{previous_day_name}**.")
                    else:
                        print("Channel not found.")
                except Exception as e:
                    print(f"Error sending cleanup notification: {e}")
            else:
                print("No CHANNEL_ID found in .env")
        else:
            print("Warning: Bot instance not attached to daily_cleanup task.")
            
    except Exception as e:
        print(f"Error in daily_cleanup: {e}")

from modules.planning import calculate_common_availability

@tasks.loop(time=datetime.time(hour=12, minute=0))
async def weekly_schedule():
    """
    Posts the weekly schedule every Monday at 12:00.
    """
    today = datetime.datetime.now()
    # Check if it's Monday (0). tasks.loop(time=...) runs every day at that time, so we check the day.
    if today.weekday() != 0:
        return

    print("Running weekly schedule generation...")
    
    if not hasattr(weekly_schedule, 'bot'):
        print("Error: Bot not attached to weekly_schedule.")
        return
        
    bot = weekly_schedule.bot
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    if not CHANNEL_ID:
        print("No CHANNEL_ID found.")
        return
        
    channel = bot.get_channel(int(CHANNEL_ID))
    if not channel:
        print("Channel not found.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT team FROM players")
    teams = [row[0] for row in cursor.fetchall()]
    
    for team in teams:
        schedule = calculate_common_availability(team, conn)
        if not schedule:
            continue
            
        embed = discord.Embed(
            title=f"📅 Emploi du temps - Équipe {team}",
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
            print(f"Error sending schedule for {team}: {e}")

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
    # Get all players
    cursor.execute("SELECT discord_id, username FROM players")
    all_players = cursor.fetchall()
    
    for pid, username in all_players:
        # Check if they have availability for next week (which is technically "this" week in DB terms since we clean daily? 
        # Wait, if we clean daily, the DB contains future days. 
        # If today is Sunday, we want them to fill for Mon-Sun starting tomorrow.
        # But if we clean daily, 'Lundi' in DB refers to the *coming* Monday if filled recently?
        # Yes, usually people fill for the upcoming week.
        
        cursor.execute("SELECT 1 FROM availability WHERE discord_id = ?", (pid,))
        if cursor.fetchone() is None:
            # User has no availability set
            try:
                user = await bot.fetch_user(pid)
                if user:
                    await user.send(f"Salut {username} ! 👋\nCeci est un rappel : pense à remplir tes disponibilités pour la semaine à venir via la commande `/availability add` !")
                    print(f"Reminder sent to {username}.")
            except Exception as e:
                print(f"Could not send reminder to {username}: {e}")
