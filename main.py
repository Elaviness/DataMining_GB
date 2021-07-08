import os
from pathlib import Path
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbm import settings
from gbm.spiders.instagram import InstagramSpider



if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())

    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_process = CrawlerProcess(settings=crawl_settings)

    crawl_process.crawl(InstagramSpider, login=os.getenv('INST_USERNAME'), password=os.getenv('ENC_PASSWORD'))

    crawl_process.start()
    