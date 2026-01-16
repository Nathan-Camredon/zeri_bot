import sqlite3

# Global connection object
conn = sqlite3.connect('database.db')

def init_database():
    """
    Initializes the database by creating necessary tables.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            discord_id INTEGER PRIMARY KEY,
            username TEXT,
            game TEXT,
            team TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            discord_id INTEGER,
            day INTEGER,
            start_time INTEGER,
            end_time INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team TEXT,
            date TEXT,
            time TEXT,
            duration INTEGER DEFAULT 2
        )
    """)
    conn.commit()
    print("Database initialized.")
