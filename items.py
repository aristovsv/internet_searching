# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    book_title = scrapy.Field()
    authors_name = scrapy.Field()
    name = scrapy.Field()
    rate = scrapy.Field()
    main_price = scrapy.Field()
    sale_price = scrapy.Field()
    link = scrapy.Field()
    _id = scrapy.Field()