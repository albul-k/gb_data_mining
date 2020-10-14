import requests
import json
import os
from time import sleep


class Parser5ka:

    __params = {
        'records_per_page': 50,
    }

    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Accept': 'application/json',
    }

    def __init__(self, url: str, pathdir: str):

        self.url = url
        self.pathdir = pathdir

    def parse(self):

        error = self.create_directory(self.pathdir)
        if error is not None:
            raise Exception(error)

        url = self.url
        params = self.__params
        while url:

            try:
                sleep(0.1)
                response = requests.get(
                    url, params=params, headers=self.__headers, timeout=60)
            except:
                pass

            if params:
                params = {}

            data: dict = response.json()
            url = data['next']

            for product in data['results']:
                self.save_to_json_file(product)

    @staticmethod
    def save_to_json_file(product: dict):

        with open(f'products/{product["id"]}.json', 'w', encoding='UTF-8') as file:
            json.dump(product, file, ensure_ascii=False)

    @staticmethod
    def create_directory(pathdir: str) -> str:
        try:
            if os.path.isdir(pathdir):
                return None
        except:
            return 'Cannot get access to specified directory'

        try:
            os.mkdir(pathdir)
            return None
        except:
            return 'Cannot create the specified directory'


if __name__ == '__main__':
    parser = Parser5ka(
        url='https://5ka.ru/api/v2/special_offers/', pathdir='./products')
    parser.parse()
