import datetime as dt
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from pymongo import MongoClient

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class ParserMagnit:

    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    }

    def __init__(self, url: str):

        self.url = url
        self.url_parsed = urlparse(url)
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['magnit']

    def _get_soup(self, url: str):
        response = requests.get(url, headers=self.__headers)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.url)
        catalog = soup.find('div', attrs={'class': "сatalogue__main"})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})
        for product in products:
            if product.attrs.get('href').split('/')[1] != 'promo':
                continue
            product_url = f'{self.url_parsed.scheme}://{self.url_parsed.hostname}{product.attrs.get("href")}'
            product_soup = self._get_soup(product_url)
            product_data = self.get_product_structure(
                product_soup, product_url)
            self.save_to(product_data)

    def get_product_structure(self, product_soup, product_url):
        url_parsed = urlparse(url)

        product_template = {

            'promo_name': self.get_promo_name,

            'product_name': self.get_product_name,

            'old_price': self.get_old_price,

            'new_price': self.get_new_price,

            'image_url': self.get_image_url,

            'date_from': self.get_date_from,

            'date_to': self.get_date_to,
        }

        product = {
            'url': url,
        }

        for key, value in product_template.items():
            try:
                product[key] = value(product_soup, url_parsed)
            except Exception:
                product[key] = None

        return product

    @staticmethod
    def get_promo_name(product_soup, *args) -> str:
        val = product_soup.find('p', attrs={'class': 'action__name-text'}).text
        return str(val)

    @staticmethod
    def get_product_name(product_soup, *args) -> str:
        val = product_soup.find('div', attrs={'class': 'action__title'}).text
        return str(val)

    @staticmethod
    def get_old_price(product_soup, *args) -> float:
        val = product_soup.find(
            'div', attrs={'class': 'label__price_old'}).text
        return float(val.strip('\n').replace('\n', '.'))

    @staticmethod
    def get_new_price(product_soup, *args) -> float:
        val = product_soup.find(
            'div', attrs={'class': 'label__price_new'}).text
        return float(val.strip('\n').replace('\n', '.'))

    @staticmethod
    def get_image_url(product_soup, url_parsed) -> str:
        val = product_soup.find(
            'img', attrs={'class': 'action__image'}).attrs['data-src']
        return f"{url_parsed.scheme}://{url_parsed.netloc}{val}"

    @staticmethod
    def get_date_from(product_soup, *args) -> datetime:
        val = product_soup.find(
            'div', attrs={'class': 'action__date-label'}).text
        _d = val.split()[1:3]
        return dt.datetime(day=int(_d[0]), month=MONTHS[_d[1][:3]], year=dt.datetime.now().year)

    @staticmethod
    def get_date_to(product_soup, *args) -> datetime:
        val = product_soup.find(
            'div', attrs={'class': 'action__date-label'}).text
        _d = val.split()[4:6]
        return dt.datetime(day=int(_d[0]), month=MONTHS[_d[1][:3]], year=dt.datetime.now().year)

    def save_to(self, product_data: dict):
        collection = self.db['promo']
        collection.insert_one(product_data)


if __name__ == "__main__":
    url = 'https://magnit.ru/promo/?geo=sankt-peterbur'
    parser = ParserMagnit(url)
    parser.parse()
