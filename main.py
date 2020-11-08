import os
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbpars import settings
# from gbpars.spiders.hh import HHSpider
# from gbpars.spiders.instagram_tags import InstagramTagsSpider
from gbpars.spiders.instagram_users import InstagramUsersSpider

load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # crawl_proc.crawl(HHSpider)
    # crawl_proc.crawl(
    #     InstagramTagsSpider,
    #     login=os.getenv('USERNAME'),
    #     enc_password=os.getenv('ENC_PASSWORD')
    # )
    crawl_proc.crawl(
        InstagramUsersSpider,
        login=os.getenv('USERNAME'),
        enc_password=os.getenv('ENC_PASSWORD')
    )
    crawl_proc.start()
