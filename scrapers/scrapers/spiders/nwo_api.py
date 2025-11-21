import scrapy
import json
from datetime import datetime
from markdownify import markdownify as md
import re


class NWOapiSpider(scrapy.Spider):
    name = "NWOapi"

    def __init__(self):
        self.max_pages = None
        self.ignore_funding = ["Stimuleringsfonds Open Access", "Open Science Open Access Boeken", "Open Access Boeken", "Reisbeurs"]

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
            proj = {}
            proj['title'] = p['title']
            proj['identifier'] = p['project_id']

            # Funding scheme
            if 'funding_scheme' in p:
                fundingScheme = p['funding_scheme']
                # Ignore some funding schemes
                if any(fIgnore in fundingScheme for fIgnore in self.ignore_funding):
                    continue
                proj['fundingScheme'] = fundingScheme

            # Start date
            if 'start_date' in p:
                startDate = datetime.fromisoformat(p['start_date'])
                startDate = startDate.strftime("%Y-%m-%d")
                proj['startDate'] = startDate

            # End date
            if 'end_date' in p:
                endDate = datetime.fromisoformat(p['end_date'])
                endDate = endDate.strftime("%Y-%m-%d")
                proj['endDate'] = endDate

            # Funding amount
            if 'award_amount' in p:
                proj['fundingAmount'] = p['award_amount']

            # DOI, newer NWO projects have a DOI
            if 'grant_id' in p:
                proj['doi'] = p['grant_id']

            # Abstracts
            if 'summary_nl' in p:
                proj['abstractNL'] =  p['summary_nl']
            if 'summary_en' in p:
                proj['abstractEN'] =  p['summary_en']

            participants = []
            for m in p['project_members']:
                part = {}
                if 'degree_pre_nominal' in m:
                    part['prefix'] = m['degree_pre_nominal']

                if 'first_name' in m:
                    part['givenName'] = m['first_name']

                if 'last_name' in m:
                    part['baseSurname'] = m['last_name']

                if 'prefix' in m:
                    part['surnamePrefix'] = m['prefix']

                if 'degree_post_nominal' in m:
                    part['honorificSuffix'] = m['degree_post_nominal']

                if 'initials' in m:
                    part['initials'] = m['initials']

                if 'role' in m:
                    part['role'] = m['role']

                if 'organisation' in m:
                    part['organisation'] = m['organisation']

                if 'orcid' in m:
                    if m['orcid'] != 'https://orcid.org/-':
                        part['orcid'] = m['orcid']

                if 'member_id' in m:
                    part['NWOid'] = m['member_id']

                participants.append(part)


            if len(participants) > 0:
                proj['participants'] = participants

            yield proj
