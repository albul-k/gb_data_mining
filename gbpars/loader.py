from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

from .items import HHJobItem, HHCompanyItem


def get_as_list(itms):
    return itms


def get_description(itms):
    text = ''
    for itm in itms:
        text += itm + '\n'
    return text


def get_as_joined_list(itms):
    result = (' ').join(itms)
    return result.strip()


def get_url_employer_description(itm):
    result = 'https://spb.hh.ru' + itm
    return result


class HHJobLoader(ItemLoader):
    default_item_class = HHJobItem
    name_out = get_as_joined_list
    url_out = TakeFirst()
    salary_out = get_as_joined_list
    description_out = get_description
    skills_out = get_as_list
    url_employer_description_in = MapCompose(get_url_employer_description)
    url_employer_description_out = TakeFirst()


class HHCompanyLoader(ItemLoader):
    default_item_class = HHCompanyItem
    name_out = get_as_joined_list
    url_out = TakeFirst()
    url_employer_out = TakeFirst()
    areas_of_activity_out = get_as_list
    description_out = get_description
