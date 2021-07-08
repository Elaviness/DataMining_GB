import os
from pathlib import Path

import pymongo
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Mail:
    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        self.driver = webdriver.Chrome()
        self.driver.get('https://mail.yandex.ru/')

        self.client = MongoClient('mongodb://localhost:27017')
        self.db = client['sillenium']
        self.collection = db['mail']

    __xpath_login = {
        'login': '//div[contains(@class, "Field_view_floating-label")]//input[@id="passp-field-login"]',
        'login_btn': '//div[contains(@class, "passp-button passp-sign-in-button")]',
        'password': '//span[contains(@class, "extinput_view_floating-label")]/input[@id="passp-field-passwd"]'

    }
    __xpath_mail = {
        'pagination_next': '//div[@class="b-pager"]/span[@class="b-pager__links"]/span[@class="b-pager__active"]',
        'messages': '//div[@class="b-messages"]/div[contains(@class, "b-messages__message")]',
        'subject': '//div[@class="b-message-head__subject"]/span[@class="b-message-head__subject-text"]',
        'date': '//div[@class="b-message-head__top"]/span[contains(@class, "b-message-head__field_date")]/span',
        'from': '//div[@class="b-message-head"]/div[@class="b-message-head__field"][2]'
                '/span[@class="b-message-head__field-value"]/a',
    }

    def start(self):
        self.driver.find_element_by_xpath(self.__xpath_login['login']).send_keys(self.__login + Keys.ENTER)
        self.driver.find_element_by_xpath(self.__xpath_login['password']).send_keys(self.__password + Keys.ENTER)

        while True:
            messages_lenght = len(self.driver.find_element_by_xpath(self.__xpath_mail['messages'])

            for index in range(0, messages_lenght):
                messages = self.driver.find_element_by_xpath(self.__xpath_mail['messages'], multiple=True)
                message = messages[index]
                message.click()
                result = {
                    'subject': self.driver.find_element_by_xpath(self.__xpath_mail['subject']).text,
                    'date': self.driver.find_element_by_xpath(self.__xpath_mail['date']).text,
                    'from': self.driver.find_element_by_xpath(self.__xpath_mail['from']).text,
                }
                # todo добавить парсинг контента самого письма
                self.write_to_mongo(result)
                self.driver.execute_script('window.history.go(-1)')

            try:
                next_page = self.driver.find_element_by_xpath(self.__xpath_mail['pagination_next'])
                next_page.click()
            except Exception as e:
                print('No more pages to scrap')
                self.driver.quit()
                break

    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)


if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    mail_crawler = Mail(
        login=os.getenv('MAIL'),
        password=os.getenv('PASSWORD')
    )
    mail_crawler.start()
