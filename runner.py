from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

import settings
from LeroyMerlin.spiders.leroymerlin import LeroymerlinSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    search = 'ковры'
    process.crawl(LeroymerlinSpider, search=search)

    process.start()