"""
Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
вакансии удаленной работы.

Задача: Обойти с точки входа все вакансии и собрать след данные:

название вакансии
оклад (строкой от до или просто сумма)
Описание вакансии
ключевые навыки - в виде списка названий
ссылка на автора вакансии
Перейти на страницу автора вакансии,
собрать данные:

Название
сайт ссылка (если есть)
сферы деятельности (списком)
Описание
Обойти и собрать все вакансии данного автора.

Обязательно использовать Loader Items Pipelines
"""

import scrapy

from scrapy import loader
from ..loader import HHJobLoader, HHCompanyLoader


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    xpath = {
        'job_description': '//div[@class="vacancy-serp-item__info"]/a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        'company': '//div[@class="vacancy-serp-item__meta-info"]/a[@data-qa="vacancy-serp__vacancy-employer"]/@href',
        'pagination': '//div[@data-qa="pager-block"]/a[contains(@class,"HH-Pager-Control")]/@href',
    }

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['job_description']):
            yield self.job_description_parse

        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)

    def company_parse(self, response, **kwargs):
        loader = HHCompanyLoader(response=response)
        loader.add_xpath('url', response.url)
        loader.add_xpath('url_company')
        loader.add_xpath('areas_of_activity')
        loader.add_xpath('description')
        yield loader.load_item()

    def job_description_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['company']):
            yield response.follow(url, callback=self.company_parse)

        loader = HHJobLoader(response=response)
        loader.add_xpath('url', response.url)
        loader.add_xpath('salary')
        loader.add_xpath('description')
        loader.add_xpath('skills')
        loader.add_xpath('url_company_description')
        yield loader.load_item()
