import sqlite3

def calculate_common_availability(team_name, guild_id, conn):
    """
    Calculates the common availability slots for a given team in a specific guild.
    
    Args:
        team_name: The name of the team.
        guild_id: The ID of the guild (server).
        conn: The database connection.
        
    Returns:
        dict: A dictionary where keys are days (0-6) and values are lists of compatible (start, end) tuples.
        Returns None if the team doesn't exist or is empty.
    """
    cursor = conn.cursor()
    
    # 1. Get all members of the team (case-insensitive search) IN THIS GUILD
    cursor.execute("SELECT discord_id, username FROM players WHERE LOWER(team) = ? AND guild_id = ?", (team_name.strip().lower(), guild_id))
    members = cursor.fetchall()
    
    if not members:
        return None
        
    member_ids = [m[0] for m in members]
    total_members = len(member_ids)
    
    # 2. Fetch ALL availability for these members in one query
    # Note: Availability is GLOBAL, so we query by discord_id regardless of guild
    placeholders = ','.join('?' for _ in member_ids)
    query = f"""
        SELECT discord_id, day, start_time, end_time 
        FROM availability 
        WHERE discord_id IN ({placeholders})
        ORDER BY day
    """
    cursor.execute(query, member_ids)
    all_rows = cursor.fetchall()

    # Organize data: schedule[day][member_id] = [(start, end), ...]
    # Initialize structure for all 7 days
    full_schedule = {day: {mid: [] for mid in member_ids} for day in range(7)}
    
    for row in all_rows:
        uid, day, start, end = row
        full_schedule[day][uid].append((start, end))
    
    common_schedule = {}
    
    # 3. Process each day
    for day in range(7):
        day_data = full_schedule[day]
        
        # Check if any member has NO availability for this day
        # If a member hasn't filled anything, common availability is impossible
        missing_data = False
        for mid in member_ids:
            if not day_data[mid]:
                missing_data = True
                break
        
        if missing_data:
            common_schedule[day] = [] 
            continue
            
        # 4. Calculate intersection
        # Start with the first member's slots
        first_member_slots = day_data[member_ids[0]]
        current_common = first_member_slots
        
        # Intersect with subsequent members
        for i in range(1, total_members):
            next_member_slots = day_data[member_ids[i]]
            current_common = intersect_intervals(current_common, next_member_slots)
            
            if not current_common:
                break
        
        common_schedule[day] = current_common
        
    return common_schedule

def intersect_intervals(slots_a, slots_b):
    """
    Finds the intersection between two lists of time slots.
    Slots are tuples (start, end).
    """
    intersections = []
    for start_a, end_a in slots_a:
        for start_b, end_b in slots_b:
            # Max of starts, Min of ends
            low = max(start_a, start_b)
            high = min(end_a, end_b)
            
            if low < high:
                intersections.append((low, high))
    return intersections

def get_player_availability(discord_id, conn):
    """
    Retrieves availability for a single player.
    """
    cursor = conn.cursor()
    common_schedule = {}
    
    # Optimization: Fetch all days in one query
    cursor.execute("SELECT day, start_time, end_time FROM availability WHERE discord_id = ? ORDER BY day", (discord_id,))
    rows = cursor.fetchall()
    
    # Initialize all days empty
    for d in range(7):
        common_schedule[d] = []
        
    for day, start, end in rows:
        common_schedule[day].append((start, end))
        
    return common_schedule
