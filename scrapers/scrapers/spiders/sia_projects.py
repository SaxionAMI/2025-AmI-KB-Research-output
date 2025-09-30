import scrapy
import json
from datetime import datetime


class SiaProjectsSpider(scrapy.Spider):
    name = "siaProjects"

    async def start(self):
        url = "https://www.sia-projecten.nl/project/tpc-c-duurzaam-hergebruik-van-thermoplastische-composiet-materialen"
        url = "https://www.sia-projecten.nl/project/observe"
        url = "https://www.sia-projecten.nl/zoek?page=0"
        # TODO: edge cases: https://www.sia-projecten.nl/project/backseat-buddy https://www.sia-projecten.nl/project/waterlab
        yield scrapy.Request(url=url, callback=self.parse_overview)

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

    def parse_overview(self, response):
        curpage = int(response.url.split("=")[-1])
        for a in response.xpath('//div[@class="view-project dm-teaser"]/div[@class="cardheader"]/h2/a/@href'):
            yield scrapy.Request(url=response.urljoin(a.get()), callback=self.parse_project)
        maxpage = response.xpath('//li[@class="pager__item summary"]/text()').get()
        maxpage = int(maxpage.split("/")[-1].strip())-1 # Pages start at 0
        if curpage != maxpage:
            url = response.urljoin(f'zoek?page={curpage+1}')
            yield scrapy.Request(url=url, callback=self.parse_overview)

    def parse_project(self, response):
        url = response.url
        title = response.css("h1::text").get()
        projectID = response.xpath('//table/tr[th/text()="Dossier"]/td/text()').get()
        status = response.xpath('//table/tr[th/text()="Status"]/td/text()').get()
        paymentAmount = response.xpath('//table/tr[th/text()="Subsidie"]/td/text()').get()
        try:
            startDate = response.xpath('//table/tr[th/text()="Startdatum"]/td/text()').get()
            startDate = self.parse_date(startDate)
        except:
            startDate = None

        try:
            endDate = response.xpath('//table/tr[th/text()="Einddatum"]/td/text()').get()
            endDate = self.parse_date(endDate)
        except:
            endDate = None
        fundingScheme = response.xpath('//table/tr[th/text()="Regeling"]/td/text()').get()

        contact = {}
        el = response.xpath('//div[@class="infoblok contactinformatie"]/div/p[@class="hogeschool"]/span')
        if el.xpath('a'):
            contact['org'] = el.xpath('a/text()').get().strip()
            contact['org_url'] = el.xpath('a/@href').get()
        else:
            contact['org'] = el.xpath('text()').get().strip()

        el = response.xpath('//div[@class="infoblok contactinformatie"]/div/p[@class="contactpersoon"]')
        if el:
            contact['name'] = el.xpath('a/text()').get()
            contact['email'] = el.xpath('a/@data-meel').get().replace('|', '@')

        participants = []
        el = response.xpath('//div[@class="infoblok consortiumleden"]/div[@class="content"]')
        if el:
            for li in el.xpath('ul/li'):
                p = {}
                p['role'] = 'participant'
                if li.xpath('a'):
                    p['name'] = li.xpath('a/text()').get()
                    p['url'] = li.xpath('a/@href').get()
                else:
                    p['name'] = li.xpath('text()').get().strip()
                participants.append(p)

        el = response.xpath('//div[@class="infoblok netwerkleden"]/div[@class="content"]')
        if el:
            for li in el.xpath('ul/li'):
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
