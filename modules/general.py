import discord
from discord import app_commands

async def aide_command(interaction: discord.Interaction):
    """
    Displays a help embed listing all commands.
    """
    embed = discord.Embed(
        title="📘 Zeri Bot - Aide",
        description="Voici la liste des commandes disponibles pour gérer vos équipes et plannings.",
        color=discord.Color.gold()
    )
    
    # 1. Gestion des Joueurs
    embed.add_field(
        name="👥 Gestion des Joueurs",
        value=(
            "`/ajouter [membre] [jeu] [équipe]` : Ajouter un joueur à une équipe.\n"
            "`/retirer [membre]` : Supprimer un joueur de la base.\n"
            "`/liste_joueurs` : Afficher tous les joueurs par équipe."
        ),
        inline=False
    )
    
    # 2. Disponibilités
    embed.add_field(
        name="📅 Disponibilités",
        value=(
            "`/ajout_dispo [jour] [début] [fin]` : Ajouter vos dispos (ex: Lundi 20h-22h).\n"
            "`/voir_dispo [équipe|membre]` : Voir les créneaux communs ou d'un joueur."
        ),
        inline=False
    )
    
    # 3. Planning & Sessions
    embed.add_field(
        name="🎮 Planning & Sessions",
        value=(
            "`/planifier_session [équipe] [jour] [debut] [fin]` : Créer une session.\n"
            "`/liste_sessions [équipe]` : Voir les prochaines sessions.\n"
            "`/supprimer_session [ID]` : Annuler une session."
        ),
        inline=False
    )
    
    # 4. Configuration (Admin)
    embed.add_field(
        name="⚙️ Configuration (Admin)",
        value=(
            "`/config_canal [type]` : Définir le canal pour les annonces du bot.\n"
            "*Types* : Global, Planning, Rappels."
        ),
        inline=False
    )
    
    embed.set_footer(text="Zeri Bot V1.3 - Développé pour la Ffaille")
    await interaction.response.send_message(embed=embed)

async def info_command(interaction: discord.Interaction):
    """
    Displays bot information and invite link.
    """
    embed = discord.Embed(
        title="⚡ Zeri Bot V1.3",
        description=(
            "Zeri Bot est un outil de gestion d'équipe et de planning pour Discord.\n"
            "Il permet de gérer facilement les disponibilités de vos joueurs et de planifier vos sessions de jeu."
        ),
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Version", value="1.2 (Public)", inline=True)
    embed.add_field(name="Développeur", value="5omega", inline=True)
    
    # Stats
    server_count = len(interaction.client.guilds)
    user_count = sum(g.member_count for g in interaction.client.guilds)
    stats_text = f"**{server_count}** serveurs nous font confiance ({user_count} utilisateurs)"
    embed.add_field(name="Statistiques", value=stats_text, inline=False)
    
    # Invite Button
    client_id = interaction.client.user.id
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands"
    
    button = discord.ui.Button(label="Inviter le Bot", url=invite_url, style=discord.ButtonStyle.link)
    view = discord.ui.View()
    view.add_item(button)
    
    await interaction.response.send_message(embed=embed, view=view)

async def report_command(interaction: discord.Interaction, message: str):
    """
    Sends a report to the developer (Bot Owner) via DM.
    """
    # 1. Log to console
    print(f"[REPORT] From {interaction.user} in {interaction.guild}: {message}")
    
    # 2. visual feedback for the user
    embed_user = discord.Embed(
        title="📨 Signalement envoyé",
        description="Merci pour votre retour ! Votre signalement a été transmis directement au développeur.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed_user, ephemeral=True)
    
    # 3. Send DM to Bot Owner
    try:
        app_info = await interaction.client.application_info()
        owner = app_info.owner
        
        # Format the report
        embed_report = discord.Embed(
            title="🚨 Nouveau Signalement",
            description=message,
            color=discord.Color.orange(),
            timestamp=interaction.created_at
        )
        embed_report.add_field(name="Auteur", value=f"{interaction.user} ({interaction.user.id})", inline=True)
        embed_report.add_field(name="Serveur", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=True)
        
        # Handle Team owners (iterating team members if necessary, but usually owner is enough or it's a Team object)
        # If owner is a User (standard bot), send directly.
        if hasattr(owner, 'send'):
             await owner.send(embed=embed_report)
        else:
             # Team handling (optional, but good practice)
             pass
             
    except Exception as e:
        print(f"Failed to DM report to owner: {e}")
