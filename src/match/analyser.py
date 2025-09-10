import json
from typing import Dict, List, Any
import pandas as pd

class CricketMatchAnalyzer:
    def __init__(self, json_data: Dict[str, Any]):
        self.data = json_data
        self.teams = self._get_team_mapping()
    
    def _safe_float(self, value, default=0.0):
        """Safely convert value to float, handling non-numeric strings"""
        if value is None or value == '' or value == '-':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_team_mapping(self) -> Dict[str, str]:
        """Create mapping of team IDs to team names"""
        mapping = {}
        for team in self.data.get('team', []):
            mapping[team['team_id']] = team['team_name']
        return mapping
    
    def get_match_summary(self) -> Dict[str, Any]:
        """Extract comprehensive match summary"""
        match = self.data.get('match', {})
        live = self.data.get('live', {})
        
        return {
            'match_details': {
                'title': self.data.get('description', ''),
                'date': match.get('date', ''),
                'venue': match.get('ground_name', ''),
                'city': match.get('town_name', ''),
                'series': match.get('series_name', ''),
                'format': match.get('international_class_name', ''),
                'result': live.get('status', '')
            },
            'teams': {
                match.get('team1_id', ''): match.get('team1_name', ''),
                match.get('team2_id', ''): match.get('team2_name', '')
            }
        }
    
    def get_innings_summary(self) -> List[Dict[str, Any]]:
        """Extract innings data in structured format"""
        innings_data = []
        
        for innings in self.data.get('innings', []):
            team_name = self.teams.get(str(innings['batting_team_id']), 'Unknown')
            
            innings_info = {
                'innings_number': innings['innings_number'],
                'batting_team': team_name,
                'runs': innings['runs'],
                'wickets': innings['wickets'],
                'overs': innings['overs'],
                'run_rate': round(self._safe_float(innings.get('run_rate', 0)), 2),
                'extras': innings.get('extras', 0),
                'target': innings.get('target', 0),
                'status': innings.get('event_name', '')
            }
            innings_data.append(innings_info)
        
        return innings_data
    
    def get_current_batting_stats(self) -> pd.DataFrame:
        """Get current batsmen statistics as DataFrame"""
        batting_data = []
        
        for batter in self.data.get('live', {}).get('batting', []):
            # Get player name from team data
            player_name = self._get_player_name(batter['player_id'])
            
            batting_data.append({
                'Player': player_name,
                'Runs': batter['runs'],
                'Balls': batter['balls_faced'], 
                'Fours': batter['fours'],
                'Sixes': batter['sixes'],
                'Strike_Rate': self._safe_float(batter['strike_rate']),
                'Status': batter['live_current_name'],
                'Position': batter.get('batting_position', 0)
            })
        
        return pd.DataFrame(batting_data)
    
    def get_current_bowling_stats(self) -> pd.DataFrame:
        """Get current bowling statistics as DataFrame"""
        bowling_data = []
        
        for bowler in self.data.get('live', {}).get('bowling', []):
            player_name = self._get_player_name(bowler['player_id'])
            
            bowling_data.append({
                'Bowler': player_name,
                'Overs': bowler['overs'],
                'Maidens': bowler['maidens'],
                'Runs': bowler['conceded'],
                'Wickets': bowler['wickets'],
                'Economy': self._safe_float(bowler['economy_rate']),
                'Status': bowler['live_current_name']
            })
        
        return pd.DataFrame(bowling_data)
    
    def get_recent_overs_summary(self) -> List[Dict[str, Any]]:
        """Extract recent overs data"""
        recent_overs = []
        
        for over_data in self.data.get('live', {}).get('recent_overs', []):
            over_summary = {
                'over_number': over_data[0].get('over_number', 0) if over_data else 0,
                'balls': [],
                'runs_in_over': 0
            }
            
            for ball in over_data:
                ball_info = {
                    'ball_number': ball.get('ball_number', 0),
                    'runs': ball.get('ball', ''),
                    'extras': ball.get('extras', '')
                }
                over_summary['balls'].append(ball_info)
                
                # Calculate runs (simplified)
                if isinstance(ball.get('ball'), int):
                    over_summary['runs_in_over'] += ball['ball']
                elif ball.get('ball') == 'W':
                    over_summary['runs_in_over'] += 0  # Wicket
            
            recent_overs.append(over_summary)
        
        return recent_overs
    
    def get_partnerships_info(self) -> List[Dict[str, Any]]:
        """Extract partnership information"""
        partnerships = []
        
        for partnership in self.data.get('live', {}).get('fow', []):
            partnership_info = {
                'wicket_number': partnership['fow_wickets'],
                'runs_scored': partnership['fow_runs'],
                'overs_batted': partnership['fow_overs'],
                'partnership_runs': partnership['partnership_runs'],
                'partnership_overs': partnership['partnership_overs'],
                'run_rate': round(self._safe_float(partnership['partnership_rate']), 2),
                'status': partnership['live_current_name']
            }
            
            # Add dismissed player info if available
            out_player = partnership.get('out_player', {})
            if out_player:
                partnership_info['dismissed_player'] = {
                    'runs': out_player.get('runs', 0),
                    'balls': out_player.get('balls_faced', 0),
                    'dismissal': out_player.get('dismissal_string', '')
                }
            
            partnerships.append(partnership_info)
        
        return partnerships
    
    def get_ball_by_ball_data(self) -> pd.DataFrame:
        """Convert ball-by-ball data to DataFrame"""
        ball_data = []
        
        for comm in self.data.get('comms', []):
            for ball in comm.get('ball', []):
                ball_info = {
                    'Over': ball['over_number'],
                    'Ball': ball['overs_actual'],
                    'Matchup': ball['players'],
                    'Outcome': ball['event'],
                    'Dismissal': ball.get('dismissal', ''),
                    'Innings': ball['innings_number']
                }
                ball_data.append(ball_info)
        
        return pd.DataFrame(ball_data)
    
    def _get_player_name(self, player_id: str) -> str:
        """Get player name from player ID"""
        for team in self.data.get('team', []):
            for player in team.get('player', []):
                if player['player_id'] == str(player_id):
                    return player['known_as']
        return f"Player_{player_id}"
    
    def generate_human_readable_report(self) -> str:
        """Generate comprehensive human-readable match report"""
        match_info = self.get_match_summary()
        innings = self.get_innings_summary()
        current_batting = self.get_current_batting_stats()
        current_bowling = self.get_current_bowling_stats()
        partnerships = self.get_partnerships_info()
        
        report = f"""
{'='*60}
CRICKET MATCH REPORT
{'='*60}

{match_info['match_details']['title']}
Date: {match_info['match_details']['date']}
Venue: {match_info['match_details']['venue']}, {match_info['match_details']['city']}
Format: {match_info['match_details']['format']}

RESULT: {match_info['match_details']['result']}

{'='*60}
INNINGS SUMMARY
{'='*60}
"""
        
        for i, inn in enumerate(innings):
            report += f"""
Innings {inn['innings_number']}: {inn['batting_team']}
Score: {inn['runs']}/{inn['wickets']} ({inn['overs']} overs)
Run Rate: {inn['run_rate']}/over
Extras: {inn['extras']}
Status: {inn['status']}
"""
            if inn['target'] > 0:
                report += f"Target: {inn['target']}\n"
        
        # Current batting state
        if not current_batting.empty:
            report += f"""
{'='*60}
CURRENT BATTING
{'='*60}
"""
            for _, batter in current_batting.iterrows():
                if batter['Status'] in ['striker', 'non-striker']:
                    not_out = "*" if batter['Status'] in ['striker', 'non-striker'] else ""
                    report += f"""
{batter['Player']}: {batter['Runs']}{not_out} ({batter['Balls']} balls, {batter['Fours']}x4, {batter['Sixes']}x6)
Strike Rate: {batter['Strike_Rate']:.2f} | Status: {batter['Status']}
"""
        
        # Current bowling
        if not current_bowling.empty:
            report += f"""
{'='*60}
CURRENT BOWLING
{'='*60}
"""
            for _, bowler in current_bowling.iterrows():
                report += f"""
{bowler['Bowler']}: {bowler['Overs']} overs, {bowler['Runs']} runs, {bowler['Wickets']} wickets
Economy: {bowler['Economy']:.2f} | Status: {bowler['Status']}
"""
        
        # Partnership info
        current_partnership = [p for p in partnerships if p['status'] == 'current partnership']
        if current_partnership:
            cp = current_partnership[0]
            report += f"""
{'='*60}
CURRENT PARTNERSHIP
{'='*60}
Partnership for {cp['wicket_number']} wicket: {cp['partnership_runs']} runs in {cp['partnership_overs']} overs
Run Rate: {cp['run_rate']}/over
"""
        
        return report

# Example usage function
def analyze_cricket_match(json_data: Dict[str, Any]):
    """Main function to analyze cricket match data"""
    
    analyzer = CricketMatchAnalyzer(json_data)
    
    # Generate structured data
    print("=== STRUCTURED DATA EXTRACTION ===")
    
    # 1. Match summary
    match_summary = analyzer.get_match_summary()
    print("Match Summary:", json.dumps(match_summary, indent=2))
    
    # 2. Innings data
    innings_data = analyzer.get_innings_summary()
    print("\nInnings Data:", json.dumps(innings_data, indent=2))
    
    # 3. Current batting (as DataFrame)
    batting_df = analyzer.get_current_batting_stats()
    print("\nCurrent Batting Stats:")
    print(batting_df.to_string(index=False))
    
    # 4. Current bowling (as DataFrame)  
    bowling_df = analyzer.get_current_bowling_stats()
    print("\nCurrent Bowling Stats:")
    print(bowling_df.to_string(index=False))
    
    # 5. Ball-by-ball data (sample)
    ball_by_ball = analyzer.get_ball_by_ball_data()
    print(f"\nBall-by-ball data shape: {ball_by_ball.shape}")
    print("Last 5 balls:")
    print(ball_by_ball.tail().to_string(index=False))
    
    print("\n" + "="*80)
    print("=== HUMAN READABLE REPORT ===")
    print("="*80)
    
    # Generate human-readable report
    report = analyzer.generate_human_readable_report()
    print(report)
    
    return {
        'match_summary': match_summary,
        'innings_data': innings_data, 
        'batting_stats': batting_df,
        'bowling_stats': bowling_df,
        'ball_by_ball': ball_by_ball,
        'human_report': report
    }

# To use with your data:
# result = analyze_cricket_match(your_json_data)