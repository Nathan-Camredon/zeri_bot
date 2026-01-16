# Zeri Bot

🇬🇧 A Discord bot for managing gaming team schedules, availability, and session planning.  
🇫🇷 Un bot Discord pour gérer les plannings d'équipes, les disponibilités et l'organisation de sessions de jeu.

---

## 🇬🇧 Features / 🇫🇷 Fonctionnalités

🇬🇧
- **Player Management**: Register players to teams and games.
- **Availability Tracking**: Players declare their weekly availability.
- **Automated Scheduling**: 
    - Finds common availability slots for teams.
    - Weekly schedule recap (Monday 12:00).
    - Availability reminders (Sunday 18:00).
- **Session Planning**: Schedule specific game sessions with conflict detection.
- **Database Storage**: SQLite persistence.

🇫🇷
- **Gestion des Joueurs** : Inscription des joueurs dans des équipes et sur des jeux.
- **Suivi des Disponibilités** : Les joueurs déclarent leurs créneaux hebdomadaires.
- **Planification Automatique** :
    - Trouve les créneaux communs pour chaque équipe.
    - Récapitulatif hebdomadaire (Lundi 12h00).
    - Rappels de disponibilité (Dimanche 18h00).
- **Organisation de Sessions** : Planification de séances précises avec détection de conflits.
- **Base de Données** : Persistance via SQLite.

---

## 🇬🇧 Prerequisites / 🇫🇷 Prérequis

- [Python 3.8+](https://www.python.org/)
- 🇬🇧 A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- 🇫🇷 Un Token de Bot Discord (via le [Portail Développeur Discord](https://discord.com/developers/applications))

---

## 🇬🇧 Installation / 🇫🇷 Installation

1.  **Clone the repository / Cloner le dépôt** :
    ```bash
    git clone <repository_url>
    cd zeri_bot
    ```

2.  **Install dependencies / Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    🇬🇧 Create a `.env` file in the root directory:
    🇫🇷 Créez un fichier `.env` à la racine :
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    GUILD_ID=your_discord_server_id
    CHANNEL_ID=your_channel_id_for_recaps
    ```

---

## 🇬🇧 Usage / 🇫🇷 Utilisation

1.  **Run the bot / Lancer le bot** :
    ```bash
    python main.py
    ```

2.  **Discord Slash Commands / Commandes Discord** :

    ### 🇬🇧 Player Management / 🇫🇷 Gestion des Joueurs
    - `/add [member] [game] [team]`: 
        - 🇬🇧 Register a player.
        - 🇫🇷 Inscrire un joueur.
    - `/remove [member]`: 
        - 🇬🇧 Remove a player and their data.
        - 🇫🇷 Supprimer un joueur et ses données.
    - `/list`: 
        - 🇬🇧 List all registered teams and players.
        - 🇫🇷 Lister toutes les équipes et joueurs inscrits.

    ### 🇬🇧 Availability / 🇫🇷 Disponibilités
    - `/availability add [day] [start] [end]`: 
        - 🇬🇧 Add a recurring weekly slot (e.g., Lundi 18 20).
        - 🇫🇷 Ajouter un créneau hebdo récurrent (ex: Lundi 18 20).
    - `/disponibilite team:[name]`: 
        - 🇬🇧 Show common slot intersections for a team.
        - 🇫🇷 Afficher les créneaux communs d'une équipe.
    - `/disponibilite member:[user]`: 
        - 🇬🇧 Show availability for a specific player.
        - 🇫🇷 Afficher les disponibilités d'un joueur spécifique.

    ### 🇬🇧 Sessions (V1.1) / 🇫🇷 Sessions (V1.1)
    - `/session add [team] [day] [start] [end]`: 
        - 🇬🇧 Plan a specific session (auto-calculates date). Checks for conflicts.
        - 🇫🇷 Planifier une session (calcul auto de la date). Vérifie les conflits.
        - *Ex: `/session add team:Alpha day:Lundi start:21 end:23`*
    - `/session list [team]`: 
        - 🇬🇧 View upcoming sessions.
        - 🇫🇷 Voir les sessions à venir.
    - `/session delete [id]`: 
        - 🇬🇧 Delete a session by its ID.
        - 🇫🇷 Supprimer une session via son ID.

---

## 🇬🇧 Project Structure / 🇫🇷 Structure du Projet

- `main.py`: 
    - 🇬🇧 Bot entry point, command registration, and event loop.
    - 🇫🇷 Point d'entrée, enregistrement des commandes et boucle d'événements.
- `modules/`:
    - `database.py`: DB connection/tables (`players`, `availability`, `sessions`).
    - `player_management.py`: Logic for adding/removing players.
    - `planning.py`: Logic for schedule intersections.
    - `session_management.py`: Logic for sessions (add/list/delete).
    - `tasks.py`: Background tasks (Cleanup, Recap, Reminders).
    - `affichages.py`: Display formatting.
- `database.db`: SQLite database file.

---

## 🇬🇧 Database Schema / 🇫🇷 Schéma BDD

**`players`**: `discord_id`, `username`, `game`, `team`  
**`availability`**: `discord_id`, `day` (0-6), `start_time` (0-23), `end_time` (0-23)  
**`sessions`**: `id`, `team`, `date` (DD/MM/YYYY), `time` (Text)