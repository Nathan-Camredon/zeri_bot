# Zeri Bot

A Discord bot for managing gaming team schedules, availability, and session planning.

## Features

- **Player Management**: Register players to teams and games.
- **Availability Tracking**: Players declare their weekly availability.
- **Automated Scheduling**: 
    - Finds common availability slots for teams.
    - Weekly schedule recap (Monday 12:00).
    - Availability reminders (Sunday 18:00).
- **Session Planning**: Schedule specific game sessions with conflict detection.
- **Database Storage**: SQLite persistence.

## Prerequisites

- [Python 3.8+](https://www.python.org/)
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd zeri_bot
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    Create a `.env` file in the root directory:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    GUILD_ID=your_discord_server_id
    CHANNEL_ID=your_channel_id_for_recaps
    ```

## Usage

1.  **Run the bot**:
    ```bash
    python main.py
    ```

2.  **Discord Slash Commands**:

    **Player Management**
    - `/add [member] [game] [team]`: Register a player.
    - `/remove [member]`: Remove a player and their data.
    - `/list`: List all registered teams and players.

    **Availability**
    - `/availability add [day] [start] [end]`: Add a recurring weekly slot (e.g., Lundi 18 20).
    - `/disponibilite team:[name]`: Show common slot intersections for a team.
    - `/disponibilite member:[user]`: Show availability for a specific player.

    **Sessions**
    - `/session add [team] [date] [time]`: Plan a one-off session (e.g., 21/01/2026 21:00).
        - *Checks for conflicts with availability automatically.*
    - `/session list [team]`: View upcoming sessions.

## Project Structure

- `main.py`: Bot entry point, command registration, and event loop.
- `modules/`:
    - `database.py`: DB connection and table initialization (`players`, `availability`, `sessions`).
    - `player_management.py`: Logic for adding/removing players and availability.
    - `planning.py`: Logic for calculating schedule intersections.
    - `session_management.py`: Logic for session scheduling and conflict checks.
    - `tasks.py`: Background tasks (Daily cleanup, Weekly recap, Reminders).
    - `affichages.py`: Display formatting.
- `database.db`: SQLite database file.

## Database Schema

**`players`**: `discord_id`, `username`, `game`, `team`
**`availability`**: `discord_id`, `day` (0-6), `start_time` (0-23), `end_time` (0-23)
**`sessions`**: `id`, `team`, `date` (DD/MM/YYYY), `time` (HH:MM), `duration`