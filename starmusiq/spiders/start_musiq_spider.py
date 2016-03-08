import re
import json
from bs4 import BeautifulSoup

from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from starmusiq.items import StarmusiqItem

class MusiqSpider(CrawlSpider):
    name = "musiq"
    allowed_domains = ["starmusiq.com"]
    start_urls = [
       "http://starmusiq.com/Latest.asp"
    ]

    #Rule(SgmlLinkExtractor(allow=(r'category1/description/\d+/story\.html',)), callback='parse_item', follow=True)

    # def parse(self, response):
    #     filename = response.url.split("/")[-2] + '.html'
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'Movie=&RecNextPg=\d$',)), callback='parse_page', follow=True),
    )

    def parse_page(self, response):
        items = []
        soup = BeautifulSoup(response.body, 'lxml')
        sites = soup.select('.main_tb2 > tbody > tr')
        for site in sites:
            item = StarmusiqItem()
            movie = site.select('.main_tb3 > tr')
            if movie:
                #item['movie_name'] = movie[1].select('h1')[0].text()
                name = movie[1].select('h1')[0].text
                author = ''
                if '-' in name:
                    foo = name.split('-')
                    name = foo[0]
                    author = foo[1]
                item['movie_name'] = name.strip()
                item['music_director'] = author.strip()
                item['url'] = movie[0].select('a')[0]['href']
                print '\033[92m' + name + '\033[0m'
                items.append(item)
        return items
