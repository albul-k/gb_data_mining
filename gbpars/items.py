# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbparsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HHJobItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    url_company_description = scrapy.Field()


class HHCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    url_company = scrapy.Field()
    areas_of_activity = scrapy.Field()
    description = scrapy.Field()
