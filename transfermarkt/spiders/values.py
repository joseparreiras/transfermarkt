import scrapy
import pandas as pd
from scrapy.http import Request
import json
import numpy as np
from scrapy.utils.response import open_in_browser


class ValuesSpider(scrapy.Spider):
    name = 'values'
    allowed_domains = ['transfermarkt.com']
    start_urls = [
        'https://www.transfermarkt.com/']

    def start_requests(self):
        with open("headers.json", "r") as read_headers:
            headers = json.load(read_headers)
        team = 'Liverpool'
        href = 'fc-liverpool/startseite/verein/31'
        team_url = 'https://www.transfermarkt.com/'+href
        yield Request(team_url, callback=self.parse_team, meta={'team': team})

    def parse_league(self, response):
        table = response.xpath(
            '//table[@class="items"]')[0].xpath('.//tbody/tr')
        for team in table:
            name += [team.xpath(
                './/a[@class="vereinprofil_tooltip"]/text()').extract_first()]
            href += [team.xpath(
                './/a[@class="vereinprofil_tooltip"]/@href').extract_first()]
            team_url = response.urljoin(href)
            yield Request(
                team_url,
                callback=self.parse_team,
                meta={'team': name}
            )

    def parse_team(self, response):
        team = response.meta.get('team')
        squad_table = response.xpath('//table[@class="items"]')
        players = squad_table.xpath('.//span[@class="show-for-small"]/a')
        for player in players:
            name = player.xpath('.//text()').extract_first()
            ids = player.xpath('.//@id').extract_first()
            href = player.xpath('.//@href').extract_first().replace(
                'profil', 'marktwertverlauf')
            url = response.urljoin(href)
            yield Request(
                url,
                callback=self.parse_player,
                meta=player.to_dict()
            )

    def parse_player(self, response):
        name = response.meta.get('name')
        id_number = response.meta.get('id')
        team = response.meta.get('team')

        script = response.xpath(
            '//script[@type = "text/javascript"]/text()')
        idx = np.where(['/*<![CDATA[*/' in x[:20]
                        for x in script.extract()])[0][-1]
        script = script[idx].extract()
        table = '['+script.split(
            "'series':[{'type':'line','name':'Market\\x20value','data':[")[1].split(']')[0]+']'
        table = table.replace("'", '"')
        table = pd.DataFrame(json.loads(table.encode('unicode-escape')))
        yield {'player': {'name': name, 'id': id_number, 'current_team': team}, 'market_value': table.to_dict(orient='list')}
