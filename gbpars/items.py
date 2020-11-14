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
    name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    url_employer_description = scrapy.Field()


class HHCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    url_employer = scrapy.Field()
    areas_of_activity = scrapy.Field()
    description = scrapy.Field()


class Instagram(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstagramTag(Instagram):
    pass


class InstagramPost(Instagram):
    pass


class InstagramUser(Instagram):
    pass


class InstagramRelations(InstagramUser):
    id_from = scrapy.Field()
    is_found = scrapy.Field()
