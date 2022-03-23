import scrapy
from scrapy.http import HtmlResponse
from HomeWork_6.BookScraper.items import BookscraperItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    base_url = 'https://www.labirint.ru'
    start_urls = [
        'https://www.labirint.ru/search/%D1%84%D0%B0%D0%BD%D1%82%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%B0/?stype=0&page=1&russianonly=1&available=1&paperbooks=1']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//div[@class='pagination-next']/a/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='product-title-link']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        book_title = response.xpath("//h1//text()").get()
        authors_name = response.xpath("//div[@class='authors']/a/text()").getall()
        rate = response.xpath("//div[@id='rate']/text()").get()
        main_price = response.xpath(
            "//div[@class='buying-priceold-val']/span/text() | //div[@class='buying-price']//span[@class='buying-price-val-number']/text()").get()
        sale_price = response.xpath("//div[@class='buying-pricenew-val']/span/text()").get()
        link = response.url
        yield BookscraperItem(book_title=book_title, authors_name=authors_name, rate=rate, main_price=main_price,
                              sale_price=sale_price, link=link)