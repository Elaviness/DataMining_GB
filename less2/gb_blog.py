from typing import Dict

import re
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class GBBlogParse:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
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
        ul = soap.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text=re.compile('›'))
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap: BeautifulSoup):
        wrapper = soap.find('div', attrs={'class': "post-items-wrapper"})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)

    # todo Зайти на страницу материала
    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            self.posts_data.append(self.get_post_data(soap))

    # todo Извлечение данных из страницы материала
    def get_post_data(self, soap: BeautifulSoup) -> Dict[str, str]:
        result = {}
        result['url'] = soap.find('link', attrs={'rel': 'canonical'}).get('href')
        result['title'] = soap.find('h1', attrs={'class': 'blogpost-title'}).text
        content = soap.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        result['writer_name'] = soap.find('div', attrs={'itemprop': 'author'}).text
        result['writer_url'] = self.domain + soap.find('a', attrs={'style': 'text-decoration:none;'}).get('href')
        pub_date = soap.find('time', attrs={'itemprop': 'datePublished'}).get('datetime')
        result['pub_date'] = pub_date.split('T')[0]
        return result


    def save_to_mongo(self):
        self.collection.insert_many(self.posts_data)


if __name__ == '__main__':
    parser = GBBlogParse()
    parser.parse_rows()
    parser.post_page_parse()
    parser.save_to_mongo()

    print(1)