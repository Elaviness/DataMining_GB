import scrapy

from scrapy.loader import ItemLoader
from gbm.items import AutoyoulaItem

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/moskva/cars/used/toyota/']

    __xpaths = {
        "pagination" : '//div[contains(@class,"Paginator_block__2XAPy")]'
                       '/div[@class="Paginator_total__oFW1n"]',
        "ads": '//article[contains(@class,"SerpSnippet_snippet__3O1t2")]'
                '//div[@class="SerpSnippet_titleWrapper__38bZM"]'
                '/a[contains(@class, "SerpSnippet_name__3F7Yu")]/@href',
        "title": '//div[@data-target="advert"]'
                 '//div[@class="AdvertCard_topAdvertHeaderInfo__OiPAZ"]'
                 '//div[@data-target="advert-title"]/text()',
        "image": '//div[@class="PhotoGallery_photoWrapper__3m7yM"]'
                 '//img[@class="PhotoGallery_photoImage__2mHGn"]/@src',
        "params": '//div[@class="AdvertCard_specs__2FEHc"]//div'
                  '//div[@class="AdvertSpecs_row__ljPcX"]',
        "description": '//div[@data-target="advert-info-descriptionLess"]'
                       '/div[@data-target="advert-info-descriptionFull"]/text()',
        "price": '//div[@class="AdvertCardStickyContacts_toolbar__pMpq1"]/'
                 'div[contains(@class, "rouble")]/text()'
        # "seller_url": ' ' не получилось извлечь
    }

    def parse(self, response, start=True):
        if start:
            pages_count = int(response.xpath(self.__xpaths['pagination']).extract()[-1].split('>')[2].split('<')[0])
        
        for num in range(2, pages_count+1):
            yield response.follow(
                f'?page={num}#serp',
                callback = self.parse,
                cb_kwargs={'start': False}
            )

        for link in response.xpath(self.__xpaths['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )
    
    def ads_parse(self, response):
        item_loader = ItemLoader(AutoyoulaItem(), response)

        item_loader.add_value('url', response.url)
        for key, value in self.__xpaths.items():
            if key in {'pagination', 'ads'}:
                continue
            item_loader.add_xpath(key, value)

        yield item_loader.load_item()
        
