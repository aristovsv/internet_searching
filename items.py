# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose,TakeFirst

def int_price(price):
    try:
        result = price[0].replace(' ', '')
        return int(result)
    except:
        return price

def fix_val_char(characteristics):
    char_dict = characteristics[0]
    for key, val in char_dict.items():
        result = val.replace('\n                ', '')
        res = result.replace('\n            ', '')
        try:
            char_dict[key] = float(res)
        except:
            char_dict[key] = res
    return char_dict


class LeroymerlinparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(int_price))
    currency = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field()
    photos = scrapy.Field()
    _id = scrapy.Field()
    characteristics = scrapy.Field(input_processor=Compose(fix_val_char))