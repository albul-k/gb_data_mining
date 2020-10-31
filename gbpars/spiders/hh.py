"""
Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
вакансии удаленной работы.

Задача: Обойти с точки входа все вакансии и собрать след данные:
* название вакансии
* оклад (строкой от до или просто сумма)
* описание вакансии
* ключевые навыки - в виде списка названий
* ссылка на автора вакансии

Перейти на страницу автора вакансии, собрать данные:
* название
* сайт ссылка (если есть)
* сферы деятельности (списком)
* описание
Обойти и собрать все вакансии данного автора.

Обязательно использовать Loader Items Pipelines
"""

import scrapy
from ..loader import HHJobLoader, HHCompanyLoader


class HHSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru', 'spb.hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    xpath = {
        'job_description': '//div[@class="vacancy-serp-item__info"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        'employer': '//div[@class="vacancy-serp-item__meta-info"]/a[@data-qa="vacancy-serp__vacancy-employer"]/@href',
        'employer_vacancies': '//div[@class="employer-sidebar-block"]//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
        'pagination': '//div[@data-qa="pager-block"]//a[contains(@class,"HH-Pager-Control")]/@href',
    }

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['job_description']):
            yield response.follow(url, callback=self.job_description_parse)

        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)

    def company_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['employer_vacancies']):
            yield response.follow(url, callback=self.parse)

        loader = HHCompanyLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath(
            'name', '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()')
        loader.add_xpath(
            'url_employer', '//div[@class="employer-sidebar-content"]//a[@data-qa="sidebar-company-site"]/@href')
        loader.add_xpath(
            'areas_of_activity', '//div[@class="employer-sidebar-block"]/div[@class="employer-sidebar-block__header"]/following-sibling::p/text()')
        loader.add_xpath(
            'description', '//div[@class="company-description"]/div[@class="g-user-content"]//*/text()')
        yield loader.load_item()

    def job_description_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['employer']):
            yield response.follow(url, callback=self.company_parse)

        loader = HHJobLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//div[@class="vacancy-title"]/h1/text()')
        loader.add_xpath('salary', '//p[@class="vacancy-salary"]/span/text()')
        loader.add_xpath(
            'description', '//div[@data-qa="vacancy-description"]//*/text()')
        loader.add_xpath(
            'skills', '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()')
        loader.add_xpath('url_employer_description',
                         '//div[@data-qa="vacancy-company"]//a[@data-qa="vacancy-company-name"]/@href')
        yield loader.load_item()
