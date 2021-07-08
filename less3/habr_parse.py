from typing import Dict

import re
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from habr_db import HabrDB
from habr_tables import Writer, Tag, Post



class HabrParse:
    domain = "https://habr.com"
    start_url = "https://habr.com/ru/"
    
    def __init__(self, db):
        self.db: HabrDB = db
        self.visited_urls = set()
        self.post_links = set()
        self.posts_data = []

    def parse_rows(self, url=start_url):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.search_post_links(soap)


    def get_next_page(self, soap: BeautifulSoup) -> str:
        a = soap.find('a', attrs={'class': 'toggle-menu__item-link_pagination'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap: BeautifulSoup):
        posts_list = soap.find('div', attrs={'class': 'posts_list'})
        posts_a = posts_list.find_all('a', attrs={'class': 'post__title_link'})
        self.post_links.update({f'{itm.get("href")}' for itm in posts_a})

    # todo Зайти на страницу материала
    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            self.posts_data.append(self.get_post_data(soap))

    def get_tags(self, soap:BeautifulSoup):
        tag_list = soap.find('dl', attrs={'class': 'post__tags'}).find('ul').find_all('a', attrs={'class': 'post__tag'})
        return [Tag(name=itm.text, url=itm.get('href')) for itm in tag_list]


    # todo Извлечение данных из страницы материала
    def get_post_data(self, soap: BeautifulSoup) -> Dict[str, str]:
        result = {}
        writer = {}
        result['url'] = soap.find('link', attrs={'rel': 'canonical'}).get('href')
        result['title'] = soap.find('span', attrs={'class': 'post__title-text'}).text

        writer['name'] = soap.find('a', attrs={'class':'user-info__fullname'}).text
        writer['url'] = soap.find('a', attrs={'class':'user-info__fullname'}).get('href')
        a = soap.find('a', attrs={'class': 'user-info__nickname'}).get('href').split('/')
        writer['username'] = a[2]
        w_result = Writer(**writer)
        
        result['writer'] = w_result
        result['tags'] = self.get_tags(soap)
        #result['habs'] = self.get_habs(soap) на habr'e хабы и теги находятся в общем контейнере
        self.db.add_post(Post(**result))





if __name__ == '__main__':
    db = HabrDB('sqlite:///habr_blog.db')
    parser = HabrParse(db)
    parser.parse_rows()
    parser.post_page_parse()
   # parser.save_to_mongo()

    print(1)