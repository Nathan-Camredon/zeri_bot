import discord
from discord import app_commands
from typing import Literal
from modules.database import conn

async def config_channel(interaction: discord.Interaction, 
                         type_notif: Literal['Global', 'Planning', 'Rappels'] = 'Global'):
    """
    Sets the current channel for specific or all bot notifications.
    
    Args:
        interaction: Discord interaction.
        type_notif: Type of notification to configure.
    """
    if not interaction.guild_id:
        await interaction.response.send_message("Cette commande ne peut être utilisée que sur un serveur.", ephemeral=True)
        return
        
    # Permission check (Only Admins)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Seuls les administrateurs peuvent configurer le bot.", ephemeral=True)
        return

    channel_id = interaction.channel_id
    guild_id = interaction.guild_id
    
    cursor = conn.cursor()
    
    try:
        # Check if config exists for this guild
        cursor.execute("SELECT 1 FROM guild_configs WHERE guild_id = ?", (guild_id,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create default entry
            cursor.execute("INSERT INTO guild_configs (guild_id) VALUES (?)", (guild_id,))
            
        # Update logic based on type
        if type_notif == 'Global':
            query = """
                UPDATE guild_configs 
                SET default_channel_id = ?, planning_channel_id = ?, reminder_channel_id = ? 
                WHERE guild_id = ?
            """
            # If Global, we set ALL to this channel? Or just default? 
            # Plan said: "If Global: Sets current channel as default for ALL notifications".
            # Implication: Should we overwrite specific ones? Yes, to "reset" to a single channel.
            cursor.execute(query, (channel_id, channel_id, channel_id, guild_id))
            msg = f"✅ Canal configuré comme **Global** (Défaut + Planning + Rappels) : <#{channel_id}>"
            
        elif type_notif == 'Planning':
             cursor.execute("UPDATE guild_configs SET planning_channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
             msg = f"✅ Canal configuré pour le **Planning** : <#{channel_id}>"
             
        elif type_notif == 'Rappels':
             cursor.execute("UPDATE guild_configs SET reminder_channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
             msg = f"✅ Canal configuré pour les **Rappels** : <#{channel_id}>"
             
        conn.commit()
        await interaction.response.send_message(msg)
        
    except Exception as e:
        print(f"Error in config_channel: {e}")
        await interaction.response.send_message("Erreur lors de la configuration.", ephemeral=True)

async def config_role(interaction: discord.Interaction, role: discord.Role):
    """
    Configures the admin role for the bot in the guild.
    """
    if not interaction.guild_id:
         await interaction.response.send_message("Cette commande doit être utilisée sur un serveur.", ephemeral=True)
         return

    # Security: Only admins can use this
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return

    guild_id = interaction.guild_id
    role_id = role.id
    
    cursor = conn.cursor()
    
    try:
        # Check if config exists
        cursor.execute("SELECT 1 FROM guild_configs WHERE guild_id = ?", (guild_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO guild_configs (guild_id, admin_role_id) VALUES (?, ?)", (guild_id, role_id))
        else:
            cursor.execute("UPDATE guild_configs SET admin_role_id = ? WHERE guild_id = ?", (role_id, guild_id))
            
        conn.commit()
        await interaction.response.send_message(f"✅ Rôle **{role.name}** configuré comme gestionnaire du bot.")
    except Exception as e:
         print(f"Error in config_role: {e}")
         await interaction.response.send_message("Erreur lors de la configuration du rôle.", ephemeral=True)
