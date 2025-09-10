from anyio import sleep
from src.utils import fetch_page, write_to_file, verify_link
from src.extract_team_data import extract_team_data, get_team_id, get_team_country, get_team_uuid
from src.extract_player_data import extract_player_data
from src.extract_match_data import extract_match_data
from src.progress_bar import print_progress_bar
import json
from src.match.processor import process_cricket_data
from src.match.analyser import CricketMatchAnalyzer, analyze_cricket_match
from src.match.extractor import CricketDataExtractor

'''
Using sleep between each player info retrieval.

Sleep times between players tested:
10 seconds - Successful
'''



async def team_data(URL: str, output: str = "output") -> None:
    if not verify_link(URL, "team"):
        print("\033[91mError: Invalid team URL. It should start with 'https://www.espncricinfo.com/team/' or 'https://www.espncricinfo.com/cricketers/team/' and be followed by the team name only (no extra slashes).\033[0m")
        return

    team_id = get_team_id(URL).replace("-", "_")
    team_country = get_team_country(URL)


    if output == "output":
        output = team_id

    print(f"Output will be saved to: {output}")
    print(f"Scraping team: {team_id}")

    all_players = await extract_team_data(URL, output)

    print(f"Output saved to: {output}.json")

    print(f"Task Completed: Collected all {len(all_players)} players from {team_country}.")
    

    write_to_file(all_players, "json", output)


async def player_data(URL: str, individual_player: bool = False, output: str = "output") -> None:

    if individual_player:
        player_data = await extract_player_data(URL, True)
        if output == "output":
            output = player_data.get("player_id")
        write_to_file(player_data, "json", output)


async def team_full_data(URL: str, output: str = "output", existing_team_data: str = None, existing_player_data: str = None) -> None:
    # existing_team_data is just the path to the JSON file containing team data (literally just a list of team members links and ids)
    # existing_player_data is just the path to the JSON file containing player data (already scraped data)
    dissected_url = URL.strip().split('/')
    if not verify_link(URL, "team"):
        print("\033[91mError: Invalid team URL. It should start with 'https://www.espncricinfo.com/team/' or 'https://www.espncricinfo.com/cricketers/team/' and be followed by the team name only (no extra slashes).\033[0m")
        return
    #dissected_url has array structure like ['https:', '', 'www.espncricinfo.com', 'team', 'united-arab-emirates-27']
    print(f"Scraping players from: {dissected_url[-1]}")
    print(f"Data will be saved into: {output}")

    if dissected_url[3] != "cricketers":
        URL = f"https://www.espncricinfo.com/cricketers/team/{dissected_url[-1]}"
    
    


    if existing_team_data: #if existing team members list then use it
        with open(existing_team_data, "r", encoding="utf-8") as f:
            team_json = json.load(f)

    if existing_player_data and not existing_team_data: # if existing player data was already scraped then finish off the job
        with open(existing_player_data, "r", encoding="utf-8") as f:
            team_json = json.load(f)

    if not existing_player_data and not existing_team_data:
        team_json = await extract_team_data(URL, output)

    index = 0

    for player in team_json:
        index+=1
        player_id = str(player.get("objectId"))
        player_data = await extract_player_data(player_id, False)
        player["full_data"] = player_data
        print_progress_bar(index / len(team_json), True)
        write_to_file(team_json, "json", output) # save the updated team JSON after each player is processed so save if anything interrupts v annoying
        await sleep(5)

async def page(url: str, output: str = "output") -> None:
    page_html = await fetch_page(url)
    write_to_file(page_html, "html", output)

async def match_data(match_url: str = None, output: str = "output", analysis_type: str = "comprehensive", filename: str = None) -> None:
    """
    Extract and analyze cricket match data from ESPN Cricinfo
    
    Args:
        match_url: ESPN Cricinfo match JSON URL (optional if filename is provided)
        output: Output filename (without extension)
        analysis_type: Type of analysis to perform
            - "comprehensive": Full analysis with all data extraction methods
            - "summary": Basic match summary only
            - "live": Current match state only
            - "structured": Structured data extraction only
            - "timeline": Event-by-event timeline of the match
        filename: Path to existing JSON file containing match data (optional)
    """
    try:
        # Load match data from file or URL
        if filename:
            print(f"Loading match data from file: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    match_data = json.load(f)
                print(f"Successfully loaded match data from file")
            except FileNotFoundError:
                print(f"\033[91mError: File '{filename}' not found.\033[0m")
                return
            except json.JSONDecodeError as e:
                print(f"\033[91mError: Invalid JSON in file '{filename}': {str(e)}\033[0m")
                return
            except Exception as e:
                print(f"\033[91mError reading file '{filename}': {str(e)}\033[0m")
                return
        elif match_url:
            print(f"Fetching match data from URL: {match_url}")
            match_data = await extract_match_data(match_url)
            if not match_data:
                print("\033[91mError: Failed to fetch match data. Please check the URL.\033[0m")
                return
            print(f"Successfully fetched match data")
        else:
            print("\033[91mError: Either match_url or filename must be provided.\033[0m")
            return
        
        # Validate that this is match data, not player data
        if not _is_match_data(match_data):
            print("\033[91mError: The provided data does not appear to be cricket match data.\033[0m")
            print("Please ensure you're using a match JSON file, not player data.")
            return
        
        # Initialize analyzers
        analyzer = CricketMatchAnalyzer(match_data)
        extractor = CricketDataExtractor(match_data)
        
        # Process based on analysis type
        if analysis_type == "comprehensive":
            print("\nPerforming comprehensive analysis...")
            
            # Get comprehensive analysis
            analysis_result = analyze_cricket_match(match_data)
            
            # Process with the processor function
            processed_data = process_cricket_data(match_data)
            
            # Convert DataFrames to dictionaries for JSON serialization
            analysis_result_serializable = {
                'match_summary': analysis_result['match_summary'],
                'innings_data': analysis_result['innings_data'],
                'batting_stats': analysis_result['batting_stats'].to_dict('records') if not analysis_result['batting_stats'].empty else [],
                'bowling_stats': analysis_result['bowling_stats'].to_dict('records') if not analysis_result['bowling_stats'].empty else [],
                'ball_by_ball': analysis_result['ball_by_ball'].to_dict('records') if not analysis_result['ball_by_ball'].empty else [],
                'human_report': analysis_result['human_report']
            }
            
            # Combine all results
            comprehensive_data = {
                "raw_data": match_data,
                "analysis": analysis_result_serializable,
                "processed": processed_data,
                "extracted": {
                    "match_info": extractor.extract_match_info(),
                    "team_info": extractor.extract_team_info(),
                    "innings_data": extractor.extract_innings_data(),
                    "live_batting": extractor.extract_live_batting(),
                    "live_bowling": extractor.extract_live_bowling(),
                    "ball_by_ball": extractor.extract_ball_by_ball(),
                    "partnerships": extractor.extract_partnerships()
                }
            }
            
            # Save comprehensive data
            write_to_file(comprehensive_data, "json", f"{output}_comprehensive")
            
            # Print human-readable report
            print("\n" + "="*80)
            print("CRICKET MATCH ANALYSIS REPORT")
            print("="*80)
            print(analysis_result['human_report'])
            
            print(f"\nComprehensive analysis saved to: {output}_comprehensive.json")
            
        elif analysis_type == "summary":
            print("\nGenerating match summary...")
            
            # Get basic summary
            match_info = extractor.extract_match_info()
            team_info = extractor.extract_team_info()
            innings_data = extractor.extract_innings_data()
            
            summary_data = {
                "match_info": match_info,
                "team_info": team_info,
                "innings_summary": innings_data,
                "human_readable": extractor.get_human_readable_summary()
            }
            
            write_to_file(summary_data, "json", f"{output}_summary")
            
            print(extractor.get_human_readable_summary())
            print(f"\nMatch summary saved to: {output}_summary.json")
            
        elif analysis_type == "live":
            print("\nExtracting live match state...")
            
            # Get current match state
            live_batting = extractor.extract_live_batting()
            live_bowling = extractor.extract_live_bowling()
            partnerships = extractor.extract_partnerships()
            
            live_data = {
                "current_batting": live_batting,
                "current_bowling": live_bowling,
                "partnerships": partnerships,
                "timestamp": match_data.get('live', {}).get('timestamp', '')
            }
            
            write_to_file(live_data, "json", f"{output}_live")
            
            print("Current Batting:")
            for batter in live_batting:
                if batter['position'] in ['striker', 'non-striker']:
                    print(f"  {batter['position']}: {batter['runs']}* ({batter['balls_faced']}b) SR: {batter['strike_rate']}")
            
            print("\nCurrent Bowling:")
            for bowler in live_bowling:
                print(f"  {bowler['overs']}-{bowler['maidens']}-{bowler['runs_conceded']}-{bowler['wickets']} Econ: {bowler['economy_rate']}")
            
            print(f"\nLive match data saved to: {output}_live.json")
            
        elif analysis_type == "structured":
            print("\nExtracting structured data...")
            
            # Get structured data using analyzer
            match_summary = analyzer.get_match_summary()
            innings_summary = analyzer.get_innings_summary()
            batting_stats = analyzer.get_current_batting_stats()
            bowling_stats = analyzer.get_current_bowling_stats()
            ball_by_ball = analyzer.get_ball_by_ball_data()
            
            structured_data = {
                "match_summary": match_summary,
                "innings_summary": innings_summary,
                "batting_stats": batting_stats.to_dict('records') if not batting_stats.empty else [],
                "bowling_stats": bowling_stats.to_dict('records') if not bowling_stats.empty else [],
                "ball_by_ball": ball_by_ball.to_dict('records') if not ball_by_ball.empty else []
            }
            
            write_to_file(structured_data, "json", f"{output}_structured")
            
            print("Match Summary:")
            print(json.dumps(match_summary, indent=2))
            
            print(f"\nStructured data saved to: {output}_structured.json")
            
        elif analysis_type == "timeline":
            print("\nGenerating event-by-event timeline...")
            
            # Get timeline data
            timeline_events = extractor.extract_match_timeline()
            timeline_report = extractor.generate_timeline_report()
            
            timeline_data = {
                "timeline_events": timeline_events,
                "timeline_report": timeline_report,
                "total_events": len(timeline_events)
            }
            
            write_to_file(timeline_data, "json", output)
            
            # Also save the human-readable report as a text file
            with open(f"{output}.txt", 'w', encoding='utf-8') as f:
                f.write(timeline_report)
            
            print(timeline_report)
            print(f"\nTimeline data saved to: {output}.json")
            print(f"Timeline report saved to: {output}.txt")
            
        else:
            print(f"\033[91mError: Invalid analysis_type '{analysis_type}'. Valid options: comprehensive, summary, live, structured, timeline\033[0m")
            return

        
        print(f"\nMatch data processing completed successfully!")
        
    except Exception as e:
        print(f"\033[91mError processing match data: {str(e)}\033[0m")
        print("Please check the match URL and try again.")

def _is_match_data(data):
    """
    Validate that the provided data is cricket match data, not player data
    """
    if not isinstance(data, dict):
        return False
    
    # Check for key match data fields
    match_indicators = ['match', 'live', 'innings', 'team', 'comms']
    has_match_fields = any(key in data for key in match_indicators)
    
    # Check for player data indicators (to exclude)
    player_indicators = ['player_name', 'player_id', 'Span', 'Mat', 'Runs', 'HS', 'Ave', 'SR']
    has_player_fields = any(key in data for key in player_indicators)
    
    # If it has match fields and doesn't look like player data, it's likely match data
    return has_match_fields and not has_player_fields
