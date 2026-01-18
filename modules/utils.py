from modules.database import conn

async def has_permission(interaction):
    """
    Checks if the user has permission to perform management actions.
    Returns True if:
    - User is Administrator
    - User has the configured 'Admin Role'
    """
    # 1. Check Administrator permission
    if interaction.user.guild_permissions.administrator:
        return True
        
    # 2. Check Configured Role
    if not interaction.guild_id:
        return False # DM or no guild
        
    cursor = conn.cursor()
    cursor.execute("SELECT admin_role_id FROM guild_configs WHERE guild_id = ?", (interaction.guild_id,))
    result = cursor.fetchone()
    
    if result and result[0]:
        role_id = result[0]
        user_roles = [r.id for r in interaction.user.roles]
        if role_id in user_roles:
            return True
            
    return False

async def check_permission_and_respond(interaction):
    """
    Checks permission and sends an ephemeral message if denied.
    Returns True if permitted, False otherwise.
    """
    if await has_permission(interaction):
        return True
        
    await interaction.response.send_message("⛔ Vous n'avez pas la permission d'effectuer cette action.", ephemeral=True)
    return False
