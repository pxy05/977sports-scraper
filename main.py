import argparse

help_desc = (
'''CLI Scraper tool for www.espncricinfo.com by pxy05.
Visit https://github.com/pxy05/sport-scraper for more information.

This is a CLI tool for:
Scraping basic player data (name, image, URL) from ESPN Cricinfo via their teams pages https://www.espncricinfo.com/cricketers/team/...
Scraping player data from ESPN Cricinfo via their player pages https://www.espncricinfo.com/cricketers/player/...
Or scraping team full player data (all players in a team with detailed stats)



It is necessary to run this tool with a head to bypass bot detection.'''
)


def main():
    only_by_itself = ["team", "player", "team_full", "page"]
    only_by_itself_counter = 0

    parser = argparse.ArgumentParser(description=help_desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--team', type=str, help='To use, insert the link to the team page and it will create a JSON file with team member info (name, image, URL to their profile).')
    parser.add_argument('--player', type=str, help='To use, insert the link to the player page and it will create a JSON file with player info (Batting & Fielding stats, and Bowling stats).')
    parser.add_argument('--team_full', type=str, help='To use, insert the link to the team page and it will create a JSON file with full player data (all players in a team with detailed stats).')
    parser.add_argument('--page', type=str, help='To use, insert the link to any page and it will scrape the raw HTML data.')
    parser.add_argument('--output', type=str, default='data/output.json', help='Specify the output file path (default: ./output.json)')

    args = parser.parse_args()

    for option in only_by_itself:
        while only_by_itself_counter < 1 and getattr(args, option) == True:
            only_by_itself_counter += 1
        
        if only_by_itself_counter > 1:
            print("\033[91mError: You cannot specify multiple options (--team, --player, --team_full, --page) at once.\033[0m")
            print("--help for more advice.")
            return

    if only_by_itself_counter == 0 and args.output:
        print("\033[91mError: You must specify either --team, --player, --team_full, or --page before specifying an output file.\033[0m")
        print("--help for more advice.")
        return
    
    # Here you would call your scraping logic, e.g.:
    # from src.utils import extract_team_players
    # extract_team_players(args.team, args.output, headless=args.headless)

    

    if args.team:
        from src.utils import extract_team_players
        extract_team_players(args.team, args.output)


    print(f"Scraping team: {args.team}")
    print(f"Output file: {args.output}")

if __name__ == "__main__":
    main()
