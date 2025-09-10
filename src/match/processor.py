# WORKING EXAMPLE: Process your cricket JSON data

# Replace 'your_json_data' with your actual JSON dictionary
def process_cricket_data(json_data):
    """
    Complete example showing how to extract both usable data and human-readable formats
    from your cricket JSON
    """
    
    print("CRICKET MATCH DATA PROCESSOR")
    print("=" * 60)
    
    # 1. EXTRACT USABLE DATA STRUCTURES
    print("\nEXTRACTING STRUCTURED DATA...")
    
    # Basic match info
    match_info = {
        'description': json_data.get('description', ''),
        'venue': json_data['match']['ground_name'],
        'date': json_data['match']['date'],
        'result': json_data['live']['status']
    }
    
    # Innings data
    innings_data = []
    for innings in json_data['innings']:
        team_name = "Nepal" if innings['batting_team_id'] == 32 else "Namibia"
        innings_data.append({
            'team': team_name,
            'runs': innings['runs'],
            'wickets': innings['wickets'],
            'overs': innings['overs'],
            'run_rate': innings.get('run_rate', 0)
        })
    
    # Current batting stats
    current_batting = []
    for batter in json_data['live']['batting']:
        player_name = get_player_name_from_data(json_data, batter['player_id'])
        current_batting.append({
            'name': player_name,
            'runs': batter['runs'],
            'balls': batter['balls_faced'],
            'strike_rate': batter['strike_rate'],
            'status': batter['live_current_name']
        })
    
    # Current bowling stats
    current_bowling = []
    for bowler in json_data['live']['bowling']:
        player_name = get_player_name_from_data(json_data, bowler['player_id'])
        current_bowling.append({
            'name': player_name,
            'overs': bowler['overs'],
            'runs': bowler['conceded'],
            'wickets': bowler['wickets'],
            'economy': bowler['economy_rate']
        })
    
    # 2. CREATE HUMAN-READABLE OUTPUT
    print("\nGENERATING HUMAN-READABLE REPORT...")
    
    readable_report = f"""
CRICKET MATCH SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{match_info['description']}
Date: {match_info['date']}
Venue: {match_info['venue']}
Result: {match_info['result']}

INNINGS SUMMARY
────────────────────────────────────────────────────────────
"""
    
    for i, innings in enumerate(innings_data):
        readable_report += f"""
Innings {i+1}: {innings['team']}
Score: {innings['runs']}/{innings['wickets']} ({innings['overs']} overs)
Run Rate: {innings['run_rate']:.2f} per over
"""
    
    # Current match state
    current_innings = json_data['live']['innings']
    batting_team = "Namibia" if current_innings['batting_team_id'] == 28 else "Nepal"
    
    readable_report += f"""
CURRENT MATCH STATE
────────────────────────────────────────────────────────────
{batting_team} batting: {current_innings['runs']}/{current_innings['wickets']} ({current_innings['overs']} overs)
Target: {current_innings.get('target', 'N/A')}
Run Rate: {current_innings.get('run_rate', 0):.2f}

Current Batsmen:
"""
    
    for bat in current_batting:
        if bat['status'] in ['striker', 'non-striker']:
            readable_report += f"  {bat['name']} ({bat['status']}): {bat['runs']}* ({bat['balls']}b) SR: {bat['strike_rate']}\n"
    
    readable_report += "\nCurrent Bowlers:\n"
    for bowl in current_bowling:
        readable_report += f"  {bowl['name']}: {bowl['overs']}-0-{bowl['runs']}-{bowl['wickets']} (Econ: {bowl['economy']})\n"
    
    # 3. RETURN BOTH FORMATS
    return {
        'structured_data': {
            'match_info': match_info,
            'innings': innings_data,
            'current_batting': current_batting,
            'current_bowling': current_bowling
        },
        'human_readable': readable_report
    }

def get_player_name_from_data(json_data, player_id):
    """Helper function to get player name"""
    for team in json_data.get('team', []):
        for player in team.get('player', []):
            if player['player_id'] == str(player_id):
                return player['known_as']
    return f"Player_{player_id}"

# EXAMPLE USAGE:
def demonstrate_usage():
    """Shows how to use the processor with your actual data"""
    
    print("""
🚀 HOW TO USE THIS WITH YOUR DATA:
═══════════════════════════════════

1. Import your JSON data:
   import json
   with open('your_cricket_data.json', 'r') as f:
       cricket_data = json.load(f)

2. Process the data:
   result = process_cricket_data(cricket_data)

3. Access structured data:
   match_info = result['structured_data']['match_info']
   batting_stats = result['structured_data']['current_batting']

4. Print human-readable report:
   print(result['human_readable'])

5. Export to different formats:
   # Save as JSON
   with open('match_analysis.json', 'w') as f:
       json.dump(result['structured_data'], f, indent=2)
   
   # Save human report as text
   with open('match_report.txt', 'w') as f:
       f.write(result['human_readable'])
""")

# ADVANCED DATA EXTRACTION FUNCTIONS
def extract_ball_by_ball_summary(json_data):
    """Extract recent ball-by-ball action"""
    ball_summary = []
    
    for comm in json_data.get('comms', [])[:3]:  # Last 3 overs
        over_data = {
            'over': comm['over_number'],
            'balls': []
        }
        
        for ball in comm.get('ball', []):
            over_data['balls'].append({
                'matchup': ball['players'],
                'outcome': ball['event'],
                'dismissal': ball.get('dismissal', '')
            })
        
        ball_summary.append(over_data)
    
    return ball_summary

def extract_team_squads(json_data):
    """Extract complete team information"""
    teams = {}
    
    for team in json_data.get('team', []):
        teams[team['team_name']] = {
            'players': [],
            'captain': None,
            'wicket_keeper': None
        }
        
        for player in team.get('player', []):
            player_info = {
                'name': player['known_as'],
                'role': player.get('player_primary_role', ''),
                'batting_style': player.get('batting_style_long', ''),
                'bowling_style': player.get('bowling_style_long', '')
            }
            
            if player.get('captain'):
                teams[team['team_name']]['captain'] = player['known_as']
            
            if player.get('keeper'):
                teams[team['team_name']]['wicket_keeper'] = player['known_as']
            
            teams[team['team_name']]['players'].append(player_info)
    
    return teams

def create_match_summary_table(json_data):
    """Create a tabular summary"""
    innings = json_data.get('innings', [])
    
    table_data = []
    for inn in innings:
        team = "Nepal" if inn['batting_team_id'] == 32 else "Namibia"
        table_data.append([
            f"Innings {inn['innings_number']}",
            team,
            f"{inn['runs']}/{inn['wickets']}",
            inn['overs'],
            f"{inn.get('run_rate', 0):.2f}",
            str(inn.get('extras', 0))
        ])
    
    # Simple table formatting
    headers = ["Innings", "Team", "Score", "Overs", "RR", "Extras"]
    
    table = f"{'':=<60}\n"
    table += f"{'Innings':<10}{'Team':<10}{'Score':<12}{'Overs':<8}{'RR':<6}{'Extras':<6}\n"
    table += f"{'':=<60}\n"
    
    for row in table_data:
        table += f"{row[0]:<10}{row[1]:<10}{row[2]:<12}{row[3]:<8}{row[4]:<6}{row[5]:<6}\n"
    
    return table

# RUN THE DEMONSTRATION
if __name__ == "__main__":
    demonstrate_usage()
    
    # If you have the actual data, uncomment and run:
    # result = process_cricket_data(your_json_data_here)
    # print(result['human_readable'])