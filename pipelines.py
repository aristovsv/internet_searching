# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import os
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke


class LeroymerlinparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.leroy_db = client['leroy_db']
        self._id = 0

    def process_item(self, item, spider):
        leroy = self.leroy_db
        goods = leroy.goods
        goods_dict = {}

        goods_dict['_id'] = self._id
        goods_dict['name'] = item['name']
        goods_dict['price'] = item['price'][0]
        goods_dict['currency'] = item['currency']
        goods_dict['link'] = item['link']
        goods_dict['photos'] = item['photos']
        goods_dict['characteristics'] = item['characteristics']

        try:
            db_list = []

            db_dict = goods.find({})

            if db_dict:
                for doc in db_dict:
                    db_list.append(doc['link'])

                last_id = len(db_list)

                if goods_dict['link'] in db_list:
                    for item in goods.find({'link': goods_dict['link']}):
                        goods_dict['_id'] = item['_id']
                        goods.update_one({'_id': item['_id']}, {'$set': goods_dict})
                else:
                    goods_dict['_id'] = last_id
                    goods.insert_one(goods_dict)
                    # count_of_news += 1
            else:
                goods.insert_one(goods_dict)
                # count_of_letters += 1
        except dke:
            pass

        return item


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        photos_path = f'/{item["name"]}/' + os.path.basename(urlparse(request.url).path)
        return photos_path
