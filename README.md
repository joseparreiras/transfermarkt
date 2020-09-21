# transfermarkt

Scrapping of hitorical **Market Values** (MV) www.transfermarkt.com using Scrapy.
The MVs are collected for each player in the First Tear competitions of a given continent.

## Spiders:
1. Value: 

extracts the historical market values for a given continent

-args:
- continent: the selected continent

## Returns:
The scrapy spider returns a dictionary with a set of players info:
1. name: player's name on transfermarkt
2. id: transfermarkt's unique id number for each player
3. current_team: team player was registered for on the scrapping date

Along with a dictionary with the historical market values:
1. value: the players value in euros (ex. 10000000 = 10M€)
2. team: the team the player was registered for on the day of the valuation
3. date: the valuation date ('yyyy-mm-dd')
