# epsncricinfo scraper for 977Sports

This is pxy05s webscraper for https://stats.espncricinfo.com
This tool is built specifically for 977Sports https://www.977sports.com/

Testing and Usage has only been evaluated on cricket teams so far.

> **⚠️ WARNING:**  
> <span style="color:red">USING THE `--team_full` FLAG MAY LEAD TO AN IP BAN FROM ESPN.</span>

## Usage

All valid URLs must begin with "https://www.espncricinfo.com".

Choose one option from:

1. team
2. player
3. team_full
4. page

More details available below.

## custom output file name

Optionally choose the name (NOT type) of the output file using --output.

## team

The team option scrapes surface level player data from a teams page such as:

1. Player IDs
2. Links to Player images (link is half complete more info below)

The Input must be a valid team link (https://www.espncricinfo.com/cricketers/)

## player

The player option scrapes player statistics data from the espn search engine (https://stats.espncricinfo.com/ci/engine/player/...)

The input must be the playerID or link to their page.

## team_full

This combines the team option with the player.
It returns in depth data on all team members in one single file.
TODO: Extra flag to output individual files for each team member.

The Input must be a valid team link (https://www.espncricinfo.com/cricketers/)

## page

This is not an https://www.espncricinfo.com exclusive feature.
This just retrieves the initially loaded raw HTML from any link provided.

The input must begin with https://

## completing image links

There appears to be 2 types of images for cricket players although there isn't much of a difference:

1. imageUrl
2. headshotImageUrl

Not all members have images.

To complete the image link just insert this infront of the scraped link:
https://img1.hscicdn.com/image/upload/f_auto,t_h_100_2x/

e.g.

- https://img1.hscicdn.com/image/upload/f_auto,t_h_100_2x//lsci/db/PICTURES/CMS/349200/349282.png
- https://img1.hscicdn.com/image/upload/f_auto,t_h_100_2x//lsci/db/PICTURES/CMS/349200/349282.1.png
