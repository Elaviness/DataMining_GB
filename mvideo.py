import os
from pathlib import Path

import pymongo
from dotenv import load_dotenv
from selenium import webdriver


mongo_server = '10.1.1.100'
mongo_port = '27017'


class Mvideo:
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Firefox()
        self.driver.get('https://www.mvideo.ru/promo/vygoda-na-smartfony-i-planshety-mark170117872')

        self.client = MongoClient('mongodb://localhost:27017')
        self.db = client['sillenium']
        self.collection = db['mvideo']

    __xpath = {
        'pagination_next': '//div[@class="o-pagination-section"]/div[@class="c-pagination notranslate"]'
                           '/a[@class="c-pagination__next font-icon icon-up "]',
        'items': '//div[@data-init="productTileList"]//div[contains(@class, "product-tiles-list-wrapper")]/div',

        'details_button': '//ul[@class="c-tabs__menu-list"]/li',
        'details_categories': '//div[@class="product-details-specification-content"]/div[2]/div/h3',
        'details': '//div[@class="product-details-specification-content"]/div[2]/div'
                   '//table[@class="table table-striped product-details-table"]'
                   '//span[@class="product-details-overview-specification"]',
        'title': '//div[@class="o-pdp-topic__title"]/h1',
        'price': '//div[@class="c-pdp-price__summary"]/div[@class="c-pdp-price__offers"]' \
                 '/div[contains(@class, "c-pdp-price__current")]'

    }

    def start(self):
        while True:
            items_len = len(self.driver.find_elements_by_xpath(self.__xpath['items']))

            for index in range(0, items_len):
                items = self.driver.find_elements_by_xpath(self.__xpath['items'])
                item = items[index]
                item.click()

                self.driver.find_elements_by_xpath(self.__xpath['details_button'])[1].click()

                result = {
                    'title': self.driver.find_element_by_xpath(self.__xpath['title']).text,
                    'price': self.driver.find_element_by_xpath(self.__xpath['price']).text,
                    'params': {},
                }

                details = self.driver.find_elements_by_xpath(self.__xpath['details'])

                for i in range(0, len(details), 2):
                    result['params'].update({details[i].text.replace('.', ''): details[i + 1].text})

                self.write_to_mongo(result)
                self.driver.execute_script('window.history.go(-2)')

            try:
                next_page = self.driver.find_elements_by_xpath(self.__xpath_mail['pagination_next'])
                next_page.click()
            except Exception as e:
                print('No more pages to scrap')
                self.driver.quit()
                break

    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)

if __name__ == '__main__':
    parse = MvideoScraper()
    parse.start()
