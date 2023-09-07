from n4j import execute_query

def get_active_tournaments():
    query = """
    MATCH (t:Tournament)
    WHERE t.is_active = True
    RETURN t.name as name
"""
    records = execute_query(query, {})
    result = [r['name'] for r in records]
    return result

def add_team(
        tournament: str, 
        team: str, 
        email: str)-> (bool, str):
    query  = """
    MATCH (to:Tournament { name: $tournament})
    MERGE (u:User {email: $email})
    MERGE (u)-[:OWNS]->(te:Team {name: $team})-[:JOINED]->(to)
    RETURN te.name as name
"""
    records = execute_query(query, {'email': email, 'tournament': tournament, 'team': team})
    if len(records) == 0:
        return False, f"Problem adding team: {records}"
    team_v = records[0].get('name', None)
    if team_v != team:
        return False, f"Error adding team: {records}"
    return True, None

def delete_team(team:str, email: str)-> (bool, str):
    query = """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})
    DETACH DELETE t
"""
    records = execute_query(query, {'email':email, 'team':team})
    print(f'delete_team records returns: {records}')
    # TODO: Error catching
    return True, None
def get_teams_for(email: str) -> list:
    query = """
    MATCH (t:Team)<-[:OWNS]-(u:User {email: $email})
    RETURN t.name as name
"""
    records = execute_query(query, {'email':email})
    result = [r['name'] for r in records]
    return result

def team_already_exists(team: str, email: str) -> bool:
    query = """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})
    RETURN t.name as name LIMIT 1
"""
    records = execute_query(query, {'email': email, 'team': team})
    if len(records) == 0:
        return False
    result = records[0].get('name', None)
    return result == team

# def add_team(team: str, email:str)-> (bool, str):
#     already_exists = team_already_exists(team, email)
#     if already_exists is True:
#         return False, f'Team {team} already exists for current user'
    
#     query = """
#     MERGE (u:User {email: $email})
#     MERGE (u)-[:OWNS]->(t:Team {name: $team})
#     RETURN t.name as name LIMIT 1
# """
#     records = execute_query(query, {'email':email, 'team':team})
#     if len(records) == 0:
#         return False, f'Problem adding team for user, unexpected database return: {records}'
#     name_v = records[0].get('name', None)
#     if name_v != team:
#         return False, f'Error adding team for user, unexpected database return: {records}'
#     return True, None

def get_characters() -> list:
    query = """
    MATCH (a:Alias)
    RETURN a.alias as name
"""
    records = execute_query(query)
    result = [r['name'] for r in records]
    return result

def get_characters_on_team(team: str, email: str)-> list[str]:
    query = """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})-[:HAS]->(c:Alias)
    RETURN c.alias as name
"""
    records = execute_query(query, {'email':email, 'team':team})
    result = [r['name'] for r in records]
    return result

def is_character_on_team(character: str, team: str, email: str) -> bool:
    query = """
    MATCH (u:User {email: $email}-[:OWNS]->(t:Team {name: $team}-[:HAS]-(c:Alias {alias:$character})))
    RETURN c.alias as name LIMIT 1
"""
    records = execute_query(query, {'character':character, 'team':team, 'email':email})
    if len(records) > 0:
        return False
    return True

def clear_team(team:str, email: str)->(bool, str):
    query = """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})-[h:HAS]->(c:Alias)
    DELETE h
"""
    records = execute_query(query, {'email':email, 'team':team})
    if len(records) > 0:
        return False, f'Unexpected database response: {records}'
    else:
        return True, None
    

def add_characters(characters: list[str], team: str, email: str) -> (bool, str):
    query= """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})
    MATCH (c:Alias)
    WHERE c.alias in $characters
    MERGE (t)-[:HAS]->(c)
    RETURN c.alias as name
"""
    records = execute_query(query, {'characters':characters, 'email':email, 'team':team})
    if len(records) == len(characters):
        return False, f'Problem adding characters. Unexpected database response: {records}'
    else:
        return True, None

# def add_character(character: str, team: str, email: str) -> (bool, str):

#     # TODO: Check that character is not already on the team
#     already_added = is_character_on_team(character, team, email)
#     if already_added is True:
#         return False, f'Character already on team'

#     query = """
#     MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})
#     MATCH (c:Alias {alias:$character})
#     MERGE (t)-[:HAS]->(c)
#     RETURN c.alias as name LIMIT 1
# """
#     records = execute_query(query, {'character':character, 'team':team, 'email': email})
#     if len(records) == 0:
#         return False, f'Problem adding character to team. Unexpected database response: {records}'
#     c_v = records[0].get('name', None)
#     if c_v != character:
#         return False, f'Error adding character to team. Unexpected database response: {records}'
#     return True, None

def update_team_characters(characters: list[str], team: str, email: str) -> (bool, str):
    success, msg = clear_team(team, email)
    if msg is not None:
        return False, msg
    
    success, msg = add_characters(characters, team, email)
    if msg is not None:
        return False, msg
    
    return True, None

def ready_to_play(team:str, email: str)-> (bool, str):
    query= """
    MATCH (u:User {email: $email})-[:OWNS]->(t:Team {name: $team})
    SET t.is_ready = True
    RETURN t.is_ready as status
"""
    records = execute_query(query, {'email':email, 'team': team})
    if len(records) == 0:
        return False, f'Problem updating team. Unexpected empty response from Database'
    result = records[0].get('status', None)
    if result is None:
        return False, f'Error updating team. Unexpected database response: {result}'
    return result, None