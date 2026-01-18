import sqlite3

# Global connection object
conn = sqlite3.connect('database.db')

def init_database():
    """
    Initializes the database by creating necessary tables.
    """
    cursor = conn.cursor()
    
    # 1. Guild Configs (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild_configs (
            guild_id INTEGER PRIMARY KEY,
            default_channel_id INTEGER,
            planning_channel_id INTEGER,
            reminder_channel_id INTEGER,
            admin_role_id INTEGER,
            report_channel_id INTEGER
        )
    """)

    # 2. Players (Updated with guild_id)
    # Composite PK to allow same user in different teams across guilds
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            discord_id INTEGER,
            guild_id INTEGER,
            username TEXT,
            game TEXT,
            team TEXT,
            PRIMARY KEY (discord_id, guild_id)
        )
    """)

    # 3. Availability (Global - Unchanged)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            discord_id INTEGER,
            day INTEGER,
            start_time INTEGER,
            end_time INTEGER
        )
    """)

    # 4. Sessions (Updated with guild_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            team TEXT,
            date TEXT,
            time TEXT,
            duration INTEGER DEFAULT 2
        )
    """)
    conn.commit()
    print("Database initialized (V2.0 Schema).")
