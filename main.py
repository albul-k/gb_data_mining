
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbpars import settings
from gbpars.spiders.hh import HHSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(HHSpider)
    crawl_proc.start()
