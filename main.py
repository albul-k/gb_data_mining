import os
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbpars import settings
from gbpars.spiders.instagram_relations import InstagramRelationsSpider

load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(
        InstagramRelationsSpider,
        login=os.getenv('USERNAME'),
        enc_password=os.getenv('ENC_PASSWORD')
    )
    crawl_proc.start()
