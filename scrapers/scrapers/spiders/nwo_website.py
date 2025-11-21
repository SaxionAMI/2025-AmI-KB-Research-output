import scrapy
import json
from datetime import datetime
from markdownify import markdownify as md
import re


class NWOwebsiteSpider(scrapy.Spider):
    name = "NWOwebsite"

    def __init__(self):
        self.max_pages = None
        self.ignore_funding = ["Stimuleringsfonds Open Access", "Open Science Open Access Boeken", "Open Access Boeken", "Reisbeurs"]
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


    async def start(self):
        url = "https://www.nwo.nl/projecten/chdep50988"
        url = "https://www.nwo.nl/projecten/tzdgg71794"
        url = "https://www.nwo.nl/projecten?page=1"
        #url = "https://www.nwo.nl/en/projects?page=1"

        #yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_project)
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_overview)

    def parse_overview(self, response):
        base_url = 'https://www.nwo.nl/projecten'
        for proj in response.xpath('//h3[@class="card__title"]/a/@href'):
            yield scrapy.Request(url='https://www.nwo.nl'+proj.get(), headers=self.headers, callback=self.parse_project)
        print("-------------------")
        item = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
        print(item)
        if item:
            yield scrapy.Request(url=base_url+item, headers=self.headers, callback=self.parse_overview)

    def parse_project(self, response):
        p = {}
        p['url'] = response.url
        p['title'] = response.xpath('//h1[@class="articleHead__title"]/text()').get()
        identifier = response.xpath('//p/strong[text()="Dossiernummer"]/following-sibling::text()').get()
        p['identifier'] = identifier.strip()

        try:
            fundingScheme = response.xpath('//p/strong[text()="Onderzoeksprogramma"]/following-sibling::text()').get()
            fundingScheme = fundingScheme.strip()
            p['fundingScheme'] = fundingScheme
        except:
            fundingScheme = None
        if fundingScheme in self.ignore_funding:
            return

        try:
            startDate = response.xpath('//p/strong[text()="Tijdsduur"]/following-sibling::time[1]/@datetime').get()
            startDate = startDate[0:10]
            p['startDate'] = startDate
        except:
            startDate = None

        try:
            endDate = response.xpath('//p/strong[text()="Tijdsduur"]/following-sibling::time[2]/@datetime').get()
            endDate = endDate[0:10]
            p['endDate'] = endDate
        except:
            endDate = None

        yield p
