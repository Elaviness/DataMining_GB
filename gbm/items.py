# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy import Selector

def validate_photo(value):
    if value[:2] == '//':
        return f'https:{value}'
    return value

def get_params(value):
    value_path = '//div[@class="AdvertSpecs_data__xK2Qx"]'
    tag = Selector(text=value)
    key = tag.xpath('//div[@class="AdvertSpecs_label__2JHnS"]/text()').extract_first()
    if tag.xpath('//a/text()'):
        value = tag.xpath('//a/text()').extract()[-1]
    else:
        value = tag.xpath('//div/text()').extract()[-1]

    return key, value

def get_price(value):
    tag = Selector(text=value)

    return ''.join(tag.xpath('//p/text()').extract()[-1].split('\u2009'))


class AutoyoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    image = scrapy.Field(input_procesor=MapCompose(validate_photo))
    params = scrapy.Field(output_processor=lambda x: dict(get_params(itm) for itm in x))
    description = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(get_price))
    # seller_url = scrapy.Field() 

