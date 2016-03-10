import re
import os
import json
import requests
from bs4 import BeautifulSoup
import requests
from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.http.request import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from starmusiq.items import StarmusiqItem

class MusiqSpider(CrawlSpider):
    name = "musiq"
    allowed_domains = ["starmusiq.com"]
    start_urls = [
       "http://www.starmusiq.com/Latest.asp?Movie=&RecNextPg=1"
    ]
    DOWNLOAD_LOCATION = '/home/gemini/caca'

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
                url = 'http://www.starmusiq.com' + movie[0].select('a')[0]['href'][1:]
                item['url'] = url
                # print '\033[92m' + name + '\033[0m'

                wanna_scrap = raw_input('\033[92m'+ 'Do you want to scrape '+ str(name) + '?. Say yes or no.' + '\033[0m')
                print '\033[92m' + wanna_scrap + '\033[0m'
                if re.match(r'(?i)(?:y|yes)$', wanna_scrap):
                    print '\033[92m' + 'Inside wanna scrap' + '\033[0m'
                    
                    MusiqSpider.parse_file_page(url)

                # elif re.match(r'(?i)(?:n|no)$', wanna_scrap):
                #     continue

                yield item
        #return items

    @classmethod
    def parse_file_page(cls, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        trs = soup.select(".main_tb2")[3].select('tr')
        trs = trs[1:]
        for tr in trs:
            song_row = tr.select('td')[0].select('input')
            if song_row:
                tds = tr.select('td')
                song_name = tds[1].text
                song_url = 'http://www.starmusiq.com/' + tds[2].find('a')['href']
                is_download = raw_input('\033[96m' + 'May I download ' + song_name + '?\033[0m')
                if re.match(r'(?i)(yes|y)$', is_download):
                    r = requests.get(song_url)
                    output = open(cls.DOWNLOAD_LOCATION + os.sep + song_name + '.mp3','wb')
                    output.write(r.content)
                    output.close()



    