import scrapy
import pandas as pd
from scrapy.http import Request
import json
import numpy as np
from scrapy.utils.response import open_in_browser
from tempfile import TemporaryFile
from ast import literal_eval


class ValuesSpider(scrapy.Spider):
    name = 'values'
    allowed_domains = ['transfermarkt.com']
    start_urls = [
        'https://www.transfermarkt.com/']

    def parse(self, response):
        href = {
            'asia': '/wettbewerbe/asien',
            'oceania': '/wettbewerbe/asien',
            'africa': '/wettbewerbe/afrika',
            'america': '/wettbewerbe/amerika',
            'europe': '/wettbewerbe/europa'
        }
        continent_url = response.urljoin(href[self.continent])
        yield Request(
            continent_url,
            callback=self.parse_continent
        )

    def parse_continent(self, response):
        table = response.xpath(
            '//table[@class="items"]/tbody/tr')
        tier = 'First Tier'
        i = 0
        while i < len(table):
            x = table[i]
            if x.xpath('.//@class').extract_first() == 'extrarow bg_blau_20 hauptlink':
                tier = x.xpath('.//text()').extract_first()
                table.pop(i)
            else:
                if not tier == 'First Tier':
                    table.pop(i)
                else:
                    i += 1
        table = [x for x in table.xpath(
            './/a/@href').extract() if 'startseite' in x][1::2]
        for link in table:
            league_link = response.urljoin(link)
            yield Request(
                league_link,
                callback=self.parse_league
            )

    def parse_league(self, response):
        table = response.xpath('//table[@class="items"]')[0].xpath('.//tr')[2:]
        for team in table:
            name = team.xpath(
                './/a[@class="vereinprofil_tooltip"]/text()').extract_first()
            href = team.xpath(
                './/a[@class="vereinprofil_tooltip"]/@href').extract_first()
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
            id_number = player.xpath('.//@id').extract_first()
            href = player.xpath('.//@href').extract_first().replace(
                'profil', 'marktwertverlauf')
            url = response.urljoin(href)
            yield Request(
                url,
                callback=self.parse_player,
                meta={'name': name, 'id': id_number, 'team': team}
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
        table = script.split(
            "'series':[{'type':'line','name':'Market\\x20value','data':[")[1].split(']')[0]
        table = pd.DataFrame(literal_eval(table))
        table['datum_mw'] = pd.to_datetime(
            table['datum_mw'], format='%b %d, %Y')
        table = table.rename(
            columns={'y': 'value', 'verein': 'team', 'datum_mw': 'date'})
        table = table[['value', 'team', 'date']]
        yield {
            'player': {
                'name': name,
                'id': id_number,
                'current_team': team
            },
            'market_value': table.to_dict(orient='list')
        }
