import re
import scrapy
from scrapy.http import HtmlResponse
from HomeWork_7.LeroyMerlinParser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader



class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super(LeroymerlinSpider, self).__init__(**kwargs)
        self.start_urls =[f'https://leroymerlin.ru/search/?q={kwargs.get("search")}/']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item = "right"]')
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_data)

    def parse_data(self, response: HtmlResponse):

        headers_list = response.xpath('//dt//text()').getall()
        char_list = response.xpath('//dd//text()').getall()
        char_dict = dict(zip(headers_list, char_list))

        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('currency', "//span[@slot='currency']/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[contains(@media, "1024px")]/@srcset')
        loader.add_value('characteristics', char_dict)
        yield loader.load_item()