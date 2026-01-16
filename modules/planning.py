import sqlite3

def calculate_common_availability(team_name, conn):
    """
    Calculates the common availability slots for a given team.
    
    Args:
        team_name (str): The name of the team.
        conn (sqlite3.Connection): The database connection.
        
    Returns:
        dict: A dictionary where keys are days (0-6) and values are lists of compatible (start, end) tuples.
              Returns None if the team doesn't exist or is empty.
              Returns an empty dict entry for a day if no common slots found.
    """
    cursor = conn.cursor()
    
    # 1. Get all members of the team (case-insensitive search)
    cursor.execute("SELECT discord_id, username FROM players WHERE LOWER(team) = ?", (team_name.lower(),))
    members = cursor.fetchall()
    
    if not members:
        return None
        
    member_ids = [m[0] for m in members]
    total_members = len(member_ids)
    
    common_schedule = {}
    
    # 2. Iterate through each day (0=Monday, 6=Sunday)
    for day in range(7):
        # Get all availability slots for this day for these members
        # We use 'IN' clause with placeholders
        placeholders = ','.join('?' for _ in member_ids)
        query = f"""
            SELECT discord_id, start_time, end_time 
            FROM availability 
            WHERE day = ? AND discord_id IN ({placeholders})
        """
        # Arguments: day, followed by all member_ids
        args = [day] + member_ids
        cursor.execute(query, args)
        rows = cursor.fetchall()
        
        # Organize by member: {member_id: [(start, end), ...]}
        member_slots = {mid: [] for mid in member_ids}
        for row in rows:
            uid, start, end = row
            member_slots[uid].append((start, end))
            
        # Check if any member has NO availability for this day
        # If a member hasn't filled anything, common availability is impossible (assuming strict "all available")
        # Alternatively, we could treat missing as "not available". 
        missing_data = False
        for mid in member_ids:
            if not member_slots[mid]:
                missing_data = True
                break
        
        if missing_data:
            common_schedule[day] = [] # No common slots if someone is missing
            continue
            
        # 3. Calculate intersection
        # Start with the first member's slots
        first_member_slots = member_slots[member_ids[0]]
        current_common = first_member_slots
        
        # Intersect with subsequent members
        for i in range(1, total_members):
            next_member_slots = member_slots[member_ids[i]]
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
    return intersections

def get_player_availability(discord_id, conn):
    """
    Retrieves availability for a single player.
    """
    cursor = conn.cursor()
    common_schedule = {}
    
    for day in range(7):
        cursor.execute("SELECT start_time, end_time FROM availability WHERE discord_id = ? AND day = ?", (discord_id, day))
        rows = cursor.fetchall()
        
        member_slots = []
        for start, end in rows:
            member_slots.append((start, end))
            
        common_schedule[day] = member_slots
        
    return common_schedule
