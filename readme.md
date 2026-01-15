# Zeri Bot

A Discord bot for managing team schedules and player lists, specifically tailored for gaming groups (e.g., League of Legends).

## Features

- **Add Players**: Register players with their game and group preference.
- **List Players**: Display all registered teams and players organized by game and group.
- **Database Storage**: Uses SQLite to persist player data.

## Prerequisites

- [Python 3.8+](https://www.python.org/)
- A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications))

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
    Create a `.env` file in the root directory and add your Discord token and Guild ID:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    GUILD_ID=your_discord_server_id
    ```

## Usage

1.  **Run the bot**:
    ```bash
    python main.py
    ```

2.  **Discord Commands**:
    - `/add [member] [game] [group]`: Add a player to the database.
        - `member`: The Discord user to add.
        - `game`: The game (e.g., 'League of Legend').
        - `group`: The group name.
    - `/list_players`: Display the list of all registered teams and players.

## Project Structure

- `main.py`: Entry point of the bot. Handles startup and command registration.
- `modules/`: Contains bot extensions and logic.
    - `add.py`: Logic for adding players.
    - `affichages.py`: Logic for displaying teams.
- `database.db`: SQLite database file (created automatically).

## Database Schema

The bot uses a `joueurs` table with the following columns:
- `discord_id` (Primary Key)
- `pseudo`
- `jeu`
- `groupe`

## Contributing

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.