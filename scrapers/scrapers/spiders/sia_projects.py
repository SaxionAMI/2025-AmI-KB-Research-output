import scrapy
import json
from datetime import datetime


class SiaProjectsSpider(scrapy.Spider):
    name = "siaProjects"

    async def start(self):
        url = "https://www.sia-projecten.nl/project/tpc-c-duurzaam-hergebruik-van-thermoplastische-composiet-materialen"
        url = "https://www.sia-projecten.nl/project/observe"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse_date(self, date):
        month_map = {
            'januari': 1, 'februari': 2, 'maart': 3, 'april': 4,
            'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'december': 12}
        p = date.split(" ")
        d = int(p[0])
        m = month_map[p[1]]
        y = int(p[2])
        return datetime(y,m,d).date()

    def parse(self, response):
        url = response.url
        title = response.css("h1::text").get()
        print("-----HALSJFALSJFKLASJFKLASJF---")
        projectID = response.xpath('//table/tr[th/text()="Dossier"]/td/text()').get()
        status = response.xpath('//table/tr[th/text()="Status"]/td/text()').get()
        paymentAmount = response.xpath('//table/tr[th/text()="Subsidie"]/td/text()').get()
        startDate = response.xpath('//table/tr[th/text()="Startdatum"]/td/text()').get()
        startDate = self.parse_date(startDate)
        endDate = response.xpath('//table/tr[th/text()="Einddatum"]/td/text()').get()
        endDate = self.parse_date(endDate)
        fundingScheme = response.xpath('//table/tr[th/text()="Regeling"]/td/text()').get()

        contact = {}
        contact['org'] = response.xpath('//div[@class="infoblok contactinformatie"]/div/p[@class="hogeschool"]/span/text()').get().strip()
        contact['name'] = response.xpath('//div[@class="infoblok contactinformatie"]/div/p[@class="contactpersoon"]/a/text()').get()
        contact['email'] = response.xpath('//div[@class="infoblok contactinformatie"]/div/p[@class="contactpersoon"]/a/@data-meel').get().replace('|', '@')

        participants = []
        for li in response.xpath('//div[@class="infoblok consortiumleden"]/div[@class="content"]/ul/li'):
            p = {}
            p['role'] = 'participant'
            if li.xpath('a'):
                p['name'] = li.xpath('a/text()').get()
                p['url'] = li.xpath('a/@href').get()
            else:
                p['name'] = li.xpath('text()').get().strip()
            participants.append(p)

        for li in response.xpath('//div[@class="infoblok netwerkleden"]/div[@class="content"]/ul/li'):
            p = {}
            p['role'] = 'network-member'
            if li.xpath('a'):
                p['name'] = li.xpath('a/text()').get()
                p['url'] = li.xpath('a/@href').get()
            else:
                p['name'] = li.xpath('text()').get().strip()
            participants.append(p)

        yield {
            "url": url,
            "title": title,
            "projectID": projectID,
            "status": status,
            "paymentAmount": paymentAmount,
            "startDate": startDate,
            "endDate": endDate,
            "fundingScheme": fundingScheme,
            "contact": contact,
            "participants": participants
        }
