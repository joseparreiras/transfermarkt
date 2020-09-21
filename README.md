# transfermarkt

Scrapping of **Historical Market Values** (MV) www.transfermarkt.com using Scrapy.
The MVs are collected for each player in the First Tear competitions of a given continent.

## Spiders:
### Values: 

Extracts the historical market values for a given continent

#### Arguments:
  1. *continent*: the selected continent

#### Output:
A dictionary with a set of players info:
1. *name*:  player's name on transfermarkt
2. *id*:  transfermarkt's unique id number for each player
3. *current_team*:  team player was registered for on the scrapping date

along with a dictionary with the historical market values:
4. *value*: the players value in euros (ex. 10000000 = 10M€)
5. *team*: the team the player was registered for on the day of the valuation
6. *date*: the valuation date ('yyyy-mm-dd')
