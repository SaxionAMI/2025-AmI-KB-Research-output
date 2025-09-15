import scrapy
import json


class SaxResearchersSpider(scrapy.Spider):
    name = "saxResearchers"

    def cleanName(self, name):
        strip_list = ['dr. ',
                      'Dr. ',
                      'dr. ir. ',
                      'ir. ',
                      'ing. ',
                      'drs. ',
                      'mr. ',
                      ', BSc',
                      ', MSc',
                      ', MSc, MA',
                      ', MBA',
                      ', MA',
                      ', BA',
                      ', PD',
                      ', PhD'
                     ]
        strip_list.sort(key=len, reverse=True)
        for s in strip_list:
            name = name.replace(s, '')
        return name

    async def start(self):
        url = "https://www.saxion.nl/services/researcher-facetednavigation?page=1&searchQuery=&facetTreeId=researcher-nl&language=en"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        cur_page = data['page']
        tot_pages = data['amount']['pages']

        for person in data['results']:
            id = person['identifier']
            url = "https://www.saxion.nl/ajax/personlightbox?person="+id
            yield scrapy.Request(url=url, callback=self.parse_lb)

        if cur_page != tot_pages:
            cur_page += 1
            url = f"https://www.saxion.nl/services/researcher-facetednavigation?page={cur_page}&searchQuery=&facetTreeId=researcher-nl&language=en"
            yield scrapy.Request(url=url, callback=self.parse)

    # Parse light box
    def parse_lb(self, response):
        name = response.css("h2.researcher__body__title::text").get(),
        if name:
            name = self.cleanName(name[0])
        lectoraat = response.css("h4.theme__body__title::text").get()
        email = response.css('a.researcher__info__link--email::attr(href)').get()
        if email:
            email = email[7:]
        # TODO: format LinkedIn URL to get identifier part only
        linkedin = response.css('a.researcher__info__link--linkedin::attr(href)').get()
        yield {
            "name": name,
            "lectoraat": lectoraat,
            "email": email,
            "linkedin": linkedin
        }
