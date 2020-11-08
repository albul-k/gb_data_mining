"""
Источник https://auto.youla.ru/

Обойти все марки авто и зайти на странички объявлений
Собрать след стуркутру и сохранить в БД Монго

Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить телефона
"""

import re
import scrapy
import base64
from pymongo import MongoClient


class YoulaSpider(scrapy.Spider):
    name = 'auto.youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'ads_name': '//div[contains(@class, "AdvertCard_advertTitle")]/text()',
        'ads_images': '//div[contains(@class, "PhotoGallery_block")]//img/@src',
        'ads_author': '//script[contains(text(), "window.transitState =")]/text()',
        'ads_specifications': '//div[contains(@class, "AdvertCard_specs")]//div[contains(@class, "AdvertSpecs")]',
    }
    db_client = MongoClient()

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):
        template = {
            'specifications': self.get_specificstions,
            'name': lambda response: response.xpath(self.xpath['ads_name']).extract_first(),
            'images': lambda response: response.xpath(self.xpath['ads_images']).extract(),
            'url_author': self.get_url_author,
            'phone_number': self.get_phone_number,
        }

        data = {}
        for key, value in template.items():
            try:
                data[key] = value(response)
            except Exception as e:
                print(e)

        collection = self.db_client['youla'][self.name]
        collection.insert_one(data)

    def get_url_author(self, response) -> str:
        script = response.xpath(self.xpath['ads_author']).get()
        regex = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(regex, script)
        if len(result) > 0:
            return f'https://youla.ru/user/{result[0]}'
        else:
            return None

    def get_specificstions(self, response) -> dict:
        xpath_specs = response.xpath(self.xpath['ads_specifications'])
        specs = {
            itm.xpath('div[1]/text()').get(): itm.xpath('div[2]/text()').get() or itm.xpath('div[2]/a/text()').get()
            for itm in xpath_specs
            if itm.xpath('div[1]/text()').get()
        }
        return specs

    def get_phone_number(self, response) -> str:
        regex = re.compile(
            r'phone\%22\%2C\%22([0-9|a-zA-Z]+)\%3D\%3D\%22\%2C\%22time')
        result = re.findall(regex, response.text)
        if len(result) > 0:
            return base64.b64decode(base64.b64decode(result[0] + '==')).decode("utf-8")
        else:
            return None
