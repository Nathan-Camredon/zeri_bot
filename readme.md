# Zeri Bot

🇬🇧 A Discord bot for managing gaming team schedules, availability, and session planning.  
🇫🇷 Un bot Discord pour gérer les plannings d'équipes, les disponibilités et l'organisation de sessions de jeu.

---

## 🇬🇧 Features / 🇫🇷 Fonctionnalités

🇬🇧
- **Multi-Server Support**: Teams and sessions are isolated per Discord server (Guild).
- **Player Management**: Register players to teams and games.
- **Availability Tracking**: Players declare their weekly availability (Global across servers).
- **Automated Scheduling**: 
    - Finds common availability slots for teams.
    - Weekly schedule recap.
- **Session Planning**: Schedule specific game sessions with conflict detection.
- **Permission System**: Secure sensitive commands to Admins or a configured Manager role.
- **Onboarding**: Auto-welcome message and setup guide.
- **Feedback**: Built-in `/report` system.

🇫🇷
- **Multi-Serveur** : Les équipes et sessions sont isolées par serveur Discord.
- **Gestion des Joueurs** : Inscription des joueurs dans des équipes.
- **Suivi des Disponibilités** : Les joueurs déclarent leurs créneaux (Global).
- **Planification Automatique** :
    - Trouve les créneaux communs pour chaque équipe.
    - Récapitulatif hebdomadaire.
- **Organisation de Sessions** : Planification de séances avec détection de conflits.
- **Système de Permissions** : Sécurisation des commandes (Admin ou Rôle Manager).
- **Acceuil** : Message de bienvenue automatique et guide de configuration.
- **Feedback** : Système de `/report` intégré.

---

## 🇬🇧 Prerequisites / 🇫🇷 Prérequis

- [Python 3.8+](https://www.python.org/)
- 🇬🇧 A Discord Bot Token
- 🇫🇷 Un Token de Bot Discord

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
    # Optional for Dev / Optionnel pour le Dev
    GUILD_ID=your_dev_server_id
    ```

---

## 🇬🇧 Usage / 🇫🇷 Utilisation

1.  **Run the bot / Lancer le bot** :
    ```bash
    python main.py
    ```

2.  **Discord Slash Commands / Commandes Discord** :

    ### 🇬🇧 General / 🇫🇷 Général
    - `/aide`: 🇬🇧 Show commands / 🇫🇷 Voir les commandes.
    - `/info`: 🇬🇧 Bot info & stats / 🇫🇷 Infos & statistiques.
    - `/report [message]`: 🇬🇧 Send feedback / 🇫🇷 Envoyer un signalement.

    ### 🇬🇧 Management (Admin/Manager) / 🇫🇷 Gestion
    - `/config_canal [type]`: 
        - 🇬🇧 Configure notification channels.
        - 🇫🇷 Configurer les canaux d'annonces.
    - `/config_role [role]`:
        - 🇬🇧 Set a Manager role.
        - 🇫🇷 Définir un rôle Manager.
    - `/ajouter [member] [game] [team]`: 
        - 🇬🇧 Register a player.
        - 🇫🇷 Inscrire un joueur.
    - `/retirer [member]`: 
        - 🇬🇧 Remove a player.
        - 🇫🇷 Supprimer un joueur.

    ### 🇬🇧 Availability / 🇫🇷 Disponibilités
    - `/ajout_dispo [day] [start] [end]`: 
        - 🇬🇧 Add a recurring slot (e.g., Lundi 18 20).
        - 🇫🇷 Ajouter un créneau (ex: Lundi 18 20).
    - `/voir_dispo [team/member]`: 
        - 🇬🇧 Show availability.
        - 🇫🇷 Afficher les disponibilités.

    ### 🇬🇧 Sessions / 🇫🇷 Sessions
    - `/planifier_session [team] [day] [start] [end]`: 
        - 🇬🇧 Plan a session.
        - 🇫🇷 Planifier une session.
    - `/liste_sessions [team]`: 
        - 🇬🇧 List upcoming sessions.
        - 🇫🇷 Voir les sessions à venir.
    - `/supprimer_session [id]`: 
        - 🇬🇧 Delete a session.
        - 🇫🇷 Supprimer une session.

---

## 🇬🇧 Database Schema / 🇫🇷 Schéma BDD

**`guild_configs`**: `guild_id`, `default_channel_id`, `planning_channel_id`, `reminder_channel_id`, `admin_role_id`
**`players`**: `discord_id`, `guild_id`, `username`, `game`, `team`  
**`availability`**: `discord_id`, `day`, `start_time`, `end_time` (Global)
**`sessions`**: `id`, `guild_id`, `team`, `date`, `time`