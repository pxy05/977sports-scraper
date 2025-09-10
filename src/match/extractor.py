import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class PlayerStats:
    name: str
    runs: int
    balls_faced: int
    fours: int
    sixes: int
    strike_rate: float
    dismissal: Optional[str] = None

@dataclass
class BowlerStats:
    name: str
    overs: str
    maidens: int
    runs_conceded: int
    wickets: int
    economy_rate: float

@dataclass
class InningsData:
    team_name: str
    total_runs: int
    wickets: int
    overs: str
    run_rate: float
    extras: int
    batting_stats: List[PlayerStats]
    bowling_stats: List[BowlerStats]

@dataclass
class MatchSummary:
    description: str
    date: str
    venue: str
    result: str
    team1: str
    team2: str
    innings: List[InningsData]

class CricketDataExtractor:
    def __init__(self, json_data: Dict[str, Any]):
        self.data = json_data
    
    def extract_match_info(self) -> Dict[str, Any]:
        """Extract basic match information"""
        match_info = self.data.get('match', {})
        return {
            'match_title': match_info.get('cms_match_title', ''),
            'date': match_info.get('date', ''),
            'venue': match_info.get('ground_name', ''),
            'city': match_info.get('town_name', ''),
            'country': match_info.get('country_name', ''),
            'series': match_info.get('series_name', ''),
            'match_type': match_info.get('international_class_name', ''),
            'result': self.data.get('live', {}).get('status', ''),
            'toss_winner': match_info.get('toss_winner_team_id', ''),
            'winner': match_info.get('winner_team_id', '')
        }
    
    def extract_team_info(self) -> Dict[str, Any]:
        """Extract team information and players"""
        teams = {}
        for team in self.data.get('team', []):
            team_id = team['team_id']
            teams[team_id] = {
                'name': team['team_name'],
                'abbreviation': team['team_abbreviation'],
                'players': []
            }
            
            for player in team.get('player', []):
                teams[team_id]['players'].append({
                    'name': player['known_as'],
                    'role': player.get('player_primary_role', ''),
                    'batting_style': player.get('batting_style_long', ''),
                    'bowling_style': player.get('bowling_style_long', ''),
                    'captain': bool(player.get('captain', 0)),
                    'keeper': bool(player.get('keeper', 0))
                })
        
        return teams
    
    def extract_innings_data(self) -> List[Dict[str, Any]]:
        """Extract innings information"""
        innings_list = []
        
        for innings in self.data.get('innings', []):
            innings_data = {
                'innings_number': innings['innings_number'],
                'batting_team_id': innings['batting_team_id'],
                'bowling_team_id': innings['bowling_team_id'],
                'runs': innings['runs'],
                'wickets': innings['wickets'],
                'overs': innings['overs'],
                'run_rate': innings.get('run_rate', 0),
                'extras': innings.get('extras', 0),
                'target': innings.get('target', 0),
                'result': innings.get('event_name', '')
            }
            innings_list.append(innings_data)
        
        return innings_list
    
    def extract_live_batting(self) -> List[Dict[str, Any]]:
        """Extract current batting information"""
        batting_stats = []
        
        for batter in self.data.get('live', {}).get('batting', []):
            batting_stats.append({
                'player_id': batter['player_id'],
                'runs': batter['runs'],
                'balls_faced': batter['balls_faced'],
                'fours': batter['fours'],
                'sixes': batter['sixes'],
                'strike_rate': batter['strike_rate'],
                'position': batter['live_current_name'],
                'batting_position': batter.get('batting_position', 0)
            })
        
        return batting_stats
    
    def extract_live_bowling(self) -> List[Dict[str, Any]]:
        """Extract current bowling information"""
        bowling_stats = []
        
        for bowler in self.data.get('live', {}).get('bowling', []):
            bowling_stats.append({
                'player_id': bowler['player_id'],
                'overs': bowler['overs'],
                'maidens': bowler['maidens'],
                'runs_conceded': bowler['conceded'],
                'wickets': bowler['wickets'],
                'economy_rate': bowler['economy_rate'],
                'position': bowler['live_current_name']
            })
        
        return bowling_stats
    
    def extract_ball_by_ball(self) -> List[Dict[str, Any]]:
        """Extract ball-by-ball commentary"""
        ball_data = []
        
        for comm in self.data.get('comms', []):
            over_info = {
                'over_number': comm['over_number'],
                'innings_number': comm['innings_number'],
                'runs_after_over': comm.get('runs', 0),
                'wickets_after_over': comm.get('wickets', 0),
                'balls': []
            }
            
            for ball in comm.get('ball', []):
                over_info['balls'].append({
                    'over': ball['overs_actual'],
                    'bowler_to_batter': ball['players'],
                    'event': ball['event'],
                    'dismissal': ball.get('dismissal', ''),
                    'text': ball.get('text', '')
                })
            
            ball_data.append(over_info)
        
        return ball_data
    
    def extract_partnerships(self) -> List[Dict[str, Any]]:
        """Extract partnership information"""
        partnerships = []
        
        for fow in self.data.get('live', {}).get('fow', []):
            partnerships.append({
                'wicket_number': fow['fow_wickets'],
                'runs_when_fell': fow['fow_runs'],
                'overs_when_fell': fow['fow_overs'],
                'partnership_runs': fow['partnership_runs'],
                'partnership_balls': fow['partnership_overs'],
                'run_rate': fow['partnership_rate'],
                'out_player': fow.get('out_player', {}),
                'current': fow['live_current_name'] == 'current partnership'
            })
        
        return partnerships
    
    def get_human_readable_summary(self) -> str:
        """Generate human-readable match summary"""
        match_info = self.extract_match_info()
        teams = self.extract_team_info()
        innings = self.extract_innings_data()
        
        summary = f"""
=== CRICKET MATCH SUMMARY ===

Match: {match_info['match_title']}
Date: {match_info['date']}
Venue: {match_info['venue']}, {match_info['city']}
Series: {match_info['series']}
Format: {match_info['match_type']}

RESULT: {match_info['result']}

=== INNINGS SUMMARY ===
"""
        
        team_names = {team_data['name']: tid for tid, team_data in teams.items()}
        
        for i, inn in enumerate(innings, 1):
            batting_team = next((team_data['name'] for tid, team_data in teams.items() 
                               if tid == str(inn['batting_team_id'])), 'Unknown')
            
            summary += f"""
Innings {i}: {batting_team}
Score: {inn['runs']}/{inn['wickets']} ({inn['overs']} overs)
Run Rate: {inn['run_rate']:.2f}
Extras: {inn['extras']}
"""
        
        # Add current match state if live
        live_innings = self.data.get('live', {}).get('innings', {})
        if live_innings.get('live_current') == 1:
            current_batters = self.extract_live_batting()
            current_bowlers = self.extract_live_bowling()
            
            summary += f"""
=== CURRENT STATE ===
Score: {live_innings['runs']}/{live_innings['wickets']} ({live_innings['overs']} overs)
Target: {live_innings.get('target', 'N/A')}
Required: {live_innings.get('required_run_rate', 'N/A')} per over

Current Batsmen:"""
            
            for batter in current_batters:
                if batter['position'] in ['striker', 'non-striker']:
                    summary += f"""
  {batter['position']}: {batter['runs']}* ({batter['balls_faced']}b, {batter['fours']}x4, {batter['sixes']}x6) SR: {batter['strike_rate']}"""
        
        return summary
    
    def extract_match_timeline(self) -> List[Dict[str, Any]]:
        """Extract chronological event-by-event timeline of the match"""
        timeline_events = []
        
        for comm in self.data.get('comms', []):
            over_number = comm.get('over_number', 0)
            innings_number = comm.get('innings_number', 0)
            
            for ball in comm.get('ball', []):
                event = {
                    'over': ball.get('overs_actual', ''),
                    'over_number': over_number,
                    'innings': innings_number,
                    'players': ball.get('players', ''),
                    'event': ball.get('event', ''),
                    'dismissal': ball.get('dismissal', ''),
                    'text': ball.get('text', ''),
                    'speed_kph': ball.get('speed_kph', ''),
                    'speed_mph': ball.get('speed_mph', '')
                }
                timeline_events.append(event)
        
        # Sort by innings and then by over for proper chronological order
        timeline_events.sort(key=lambda x: (int(x['innings']), float(x['over']) if x['over'] else 0))
        
        return timeline_events
    
    def generate_timeline_report(self) -> str:
        """Generate human-readable timeline report"""
        timeline = self.extract_match_timeline()
        match_info = self.extract_match_info()
        
        report = f"""
CRICKET MATCH TIMELINE
{'='*60}

Match: {match_info['match_title']}
Date: {match_info['date']}
Venue: {match_info['venue']}, {match_info['city']}
Result: {match_info['result']}

{'='*60}
EVENT-BY-EVENT TIMELINE
{'='*60}
"""
        
        current_innings = None
        current_over = None
        
        for event in timeline:
            # Add innings header when it changes
            if current_innings != event['innings']:
                current_innings = event['innings']
                report += f"\nINNINGS {current_innings}\n"
                report += "-" * 40 + "\n"
                current_over = None
            
            # Add over header when it changes
            if current_over != event['over_number']:
                current_over = event['over_number']
                report += f"\nOver {current_over}:\n"
            
            # Format the event
            event_text = f"  {event['over']}: {event['players']} - {event['event']}"
            
            # Add dismissal details if it's a wicket
            if event['dismissal']:
                event_text += f" ({event['dismissal']})"
            
            # Add speed if available
            if event['speed_kph']:
                event_text += f" [Speed: {event['speed_kph']} km/h]"
            
            report += event_text + "\n"
        
        return report

def main():
    # Example usage - replace with your JSON data
    sample_json = '''paste your JSON data here'''
    
    try:
        # Load the JSON data (in your case, you already have it)
        # data = json.loads(sample_json)
        
        # For demonstration, using the provided data structure
        # Replace this with: extractor = CricketDataExtractor(data)
        print("Cricket Data Extractor Ready!")
        print("\nAvailable extraction methods:")
        print("1. extract_match_info() - Basic match details")
        print("2. extract_team_info() - Team and player information") 
        print("3. extract_innings_data() - Innings summaries")
        print("4. extract_live_batting() - Current batting stats")
        print("5. extract_live_bowling() - Current bowling stats")
        print("6. extract_ball_by_ball() - Detailed ball-by-ball data")
        print("7. extract_partnerships() - Partnership information")
        print("8. get_human_readable_summary() - Formatted summary")
        print("9. extract_match_timeline() - Event-by-event timeline")
        print("10. generate_timeline_report() - Formatted timeline report")
        
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()