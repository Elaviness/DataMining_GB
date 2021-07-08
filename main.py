from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbm import settings
from gbm.spiders.autoyoula import AutoyoulaSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_process = CrawlerProcess(settings=crawl_settings)

    crawl_process.crawl(AutoyoulaSpider)

    crawl_process.start()
    