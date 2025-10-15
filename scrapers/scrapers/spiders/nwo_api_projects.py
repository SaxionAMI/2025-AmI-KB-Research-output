import scrapy
import json
from datetime import datetime
from markdownify import markdownify as md
import re


class NWOapiProjectsSpider(scrapy.Spider):
    name = "NWOapiProjects"

    def __init__(self):
        self.max_pages = None
        self.ignore_funding = ["Stimuleringsfonds Open Access", "Open Science Open Access Boeken", "Reisbeurs"]

    async def start(self):
        url='https://nwopen-api.nwo.nl/NWOpen-API/api/Projects?project_id=NWA.1160.18.238'
        url='https://nwopen-api.nwo.nl/NWOpen-API/api/Projects?'
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        data = response.json()
        if not self.max_pages:
            self.max_pages = data['meta']['pages']
        curpage = data['meta']['page']

        if curpage != self.max_pages:
            url = response.urljoin(f'?page={curpage+1}')
            yield scrapy.Request(url=url, callback=self.parse)
        for p in data['projects']:
            fundingScheme = p['funding_scheme']
            # Ignore some funding schemes
            if any(fIgnore in fundingScheme for fIgnore in self.ignore_funding):
                continue
            try:
                startDate = datetime.fromisoformat(p['start_date'])
            except:
                startDate = None
            title = p['title']
            projectID = p['project_id']
            try:
                paymentAmount = p['award_amount']
            except:
                paymentAmount = None

            try:
                doi = p['grant_id']
            except:
                doi = None

            # Summaries
            try:
                summary_nl =  p['summary_nl']
            except:
                summary_nl = None
            try:
                summary_en =  p['summary_en']
            except:
                summary_en = None

            participants = []
            for m in p['project_members']:
                part = {}
                try:
                    part['givenName'] = m['first_name']
                except:
                    part['givenName'] = None
                part['baseSurname'] = m['last_name']
                try:
                    part['surnamePrefix'] = m['prefix']
                except:
                    part['surnamePrefix'] = None
                part['initials'] = m['initials']
                part['role'] = m['role']
                part['organisation'] = m['organisation']

                if m['orcid'] == 'https://orcid.org/-':
                    part['orcid'] = None
                else:
                    part['orcid'] = m['orcid']

                try:
                    part['prefix'] = m['degree_pre_nominal']
                except:
                    part['prefix'] = None
                try:
                    part['honorificSuffix'] = m['degree_post_nominal']
                except:
                    part['honorificSuffix'] = None
                part['NWOid'] = m['member_id']
                participants.append(part)


            yield {
                "title": title,
                "projectID": projectID,
                "doi": doi,
                "startDate": startDate,
                "endDate": startDate,
                "fundingScheme": fundingScheme,
                "paymentAmount": paymentAmount,
                "summaryNL": summary_nl,
                "summaryEN": summary_en,
                "participants": participants,
            }


