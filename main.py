import argparse
import asyncio
from src.end_point_functions import *

help_desc = (
'''CLI Scraper tool for www.espncricinfo.com by pxy05.
Visit https://github.com/pxy05/sport-scraper for more information.

This tool is still in Beta if there are any issues please start on at: https://github.com/pxy05/sport-scraper/issues

This is a CLI tool for:
Scraping basic player data (name, image, URL) from ESPN Cricinfo via their teams pages https://www.espncricinfo.com/cricketers/team/...
Scraping player data from ESPN Cricinfo via their player pages https://www.espncricinfo.com/cricketers/player/...
Or scraping team full player data (all players in a team with detailed stats)



It is necessary to run this tool with a head to bypass bot detection.'''
)

# def validate_url(URL: str, option: bool) -> bool:
#     if not URL.startswith("https://www.espncricinfo.com"):
#         if ["team_full"].count(option) > 0:
#             print("\033[91mError: Invalid URL. It should start with 'https://www.espncricinfo.com/'.\033[0m")
#         return False
#     return True

async def main():
    only_by_itself = ["team", "player", "team_full", "page"]
    only_by_itself_counter = 0
    selected_option = ""

    parser = argparse.ArgumentParser(description=help_desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--team', type=str, help='To use, insert the link to the team page and it will create a JSON file with team member info (name, image, URL to their profile).')
    parser.add_argument('--player', type=str, help='To use, insert the link to the player page and it will create a JSON file with player info (Batting & Fielding stats, and Bowling stats).')
    parser.add_argument('--team_full', type=str, help='To use, insert the link to the team page and it will create a JSON file with full player data (all players in a team with detailed stats).')
    parser.add_argument('--page', type=str, help='To use, insert the link to any page and it will scrape the raw HTML data.')
    parser.add_argument('--output', type=str, default='output', help='Specify the output file path (default: ./output) The type of file depends on the scraping option used.')

    args = parser.parse_args()

    for option in only_by_itself:

        if getattr(args, option) is not None:
            selected_option = option
            only_by_itself_counter += 1
            
        
        if only_by_itself_counter > 1:
            print("\033[91mError: You cannot specify multiple options (--team, --player, --team_full, --page) at once.\033[0m")
            print("--help for more advice.")
            return

    if only_by_itself_counter == 0:
        print("\033[91mError: You must specify either --team, --player, --team_full, or --page before specifying an output file.\033[0m")
        print("--help for more advice.")
        return
    
    # if  (not args.page) and (not validate_url(getattr(args, selected_option))):
    #     return

    if selected_option == "team":
        await team_data(args.team, args.output)
    elif selected_option == "player":
        # await player_data(args.player, True)
        await player_data(args.player, True)
    elif selected_option == "team_full":
        await team_full_data(args.team_full, args.output)
    elif selected_option == "page":
        await page(args.page, args.output)

if __name__ == "__main__":
    asyncio.run(main())
