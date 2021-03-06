# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from pymongo import MongoClient



class GbmPipeline:
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017')
        self.db = client['gb_parse_08']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item

class GbmImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get('image', []):
            try:
                yield Request(url)
            except Exception as e:
                print(e)


    def item_completed(self, results, item, info):
        if item.get('images'):
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item
