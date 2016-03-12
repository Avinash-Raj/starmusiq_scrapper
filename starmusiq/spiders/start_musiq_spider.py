import re
import os
import json
import requests
from bs4 import BeautifulSoup

try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider

# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from starmusiq.items import StarmusiqItem


class MusiqSpider(CrawlSpider):
    name = "musiq"
    allowed_domains = ["starmusiq.com"]

    DOWNLOAD_LOCATION = '/home/avinash/caca'

    if not DOWNLOAD_LOCATION:
        DOWNLOAD_LOCATION = raw_input(
            '\033[91m' + 'Please choose the download location (ex. /home/download) : ' + '\033[0m')
    while True:
        is_dir = os.path.isdir(DOWNLOAD_LOCATION)
        if not is_dir:
            DOWNLOAD_LOCATION = raw_input('\033[93m' + 'Please enter a valid directory : ' + '\033[0m')
        else:
            break

    print '\033[94m' + 'Please choose a number from the below list to crawl.' + '\033[0m'
    print '\033[92m' + '1: Latest songs' + '\033[0m'
    print '\033[92m' + '2: Ilayaraja hits' + '\033[0m'
    print '\033[92m' + '3: A.R.Rahman hits' + '\033[0m'

    num = raw_input('\033[93m' + 'Enter your number : ' + '\033[0m')
    while True:
        if num not in ('1', '2', '3'):
            num = raw_input('\033[94m' + 'Please enter a valid number : ' + '\033[0m')
        else:
            break

    start_urls = [
        "http://www.starmusiq.com/Latest.asp?Movie=&RecNextPg=1"
    ]

    rules = (
        Rule(LinkExtractor(allow=(r'Movie=&RecNextPg=\d+$',)), callback='parse_page', follow=True),
    )

    if num == '2':
        start_urls = [
            "http://starmusiq.com/Composer.asp?Composer=Ilaiyaraaja&RecNextPg=1"
        ]

        rules = (
            Rule(LinkExtractor(allow=(r'Composer=Ilaiyaraaja&RecNextPg=\d+$',)), callback='parse_page', follow=True),
        )
    elif num == '3':
        start_urls = [
            "http://starmusiq.com/Composer.asp?Composer=A.R.Rahman&RecNextPg=1"
        ]

        rules = (
            Rule(LinkExtractor(allow=(r'Composer=A.R.Rahman&RecNextPg=\d+$',)), callback='parse_page', follow=True),
        )

    def parse_page(self, response):
        items = []
        soup = BeautifulSoup(response.body, 'lxml')
        sites = soup.select('.main_tb2 > tbody > tr')
        for site in sites:
            item = StarmusiqItem()
            movie = site.select('.main_tb3 > tr')
            if movie:
                # item['movie_name'] = movie[1].select('h1')[0].text()
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

                wanna_scrap = raw_input(
                    '\033[92m' + 'Do you want to scrape ' + str(name) + '?.(Y/n) ' + '\033[0m')
                print '\033[92m' + wanna_scrap + '\033[0m'
                if re.match(r'(?i)(?:y|yes)$', wanna_scrap):
                    MusiqSpider.parse_file_page(url)

                yield item

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
                    output = open(cls.DOWNLOAD_LOCATION + os.sep + song_name + '.mp3', 'wb')
                    output.write(r.content)
                    output.close()
