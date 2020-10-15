import requests
import json
import os
from time import sleep


class Parser5ka:

    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Accept': 'application/json',
    }

    __records_per_page = 50

    __max_request_numbers = 20

    def __init__(self, url_offers: str, url_categories: str, pathdir: str):

        self.url_offers = url_offers
        self.url_categories = url_categories
        self.pathdir = pathdir

    def parse(self):

        # создаем каталог, куда будем сохранять json файлы
        try:
            if os.path.isdir(self.pathdir) is False:
                os.mkdir(self.pathdir)
        except OSError as os_err:
            print(os_err)
            return
        except Exception as err:
            print(f'Cannot create the specified directory: {err}')
            return

        # получаем список категорий
        response = self.try_request(self.url_categories, None)
        if not response:
            return

        # получаем содержимое response в json
        try:
            categories: dict = response.json()
        except ValueError as val_err:
            print(val_err)
            return

        # обходим полученные категории
        for category in categories:

            url = self.url_offers
            params = {
                'records_per_page': self.__records_per_page,
                'categories': category['parent_group_code'],
            }
            while url:

                # запрос списка товаров по категории
                response = self.try_request(url, params)
                if not response:
                    break

                if params:
                    params = {}

                try:
                    products: dict = response.json()
                except ValueError as val_err:
                    print(val_err)
                    break

                url = products['next']
                data = {
                    "name": category['parent_group_name'],
                    "code": category['parent_group_code'],
                    "products": [product for product in products['results']]
                }

                # сохраняем в файл
                self.save_to_json_file(category, data)

    def try_request(self, url: str, params: dict)-> dict:
        """Делаем заданное количество попыток запросов к ресурсу"""

        count = 0
        response = None
        while not response:
            response = self.do_request(url, self.__headers, params)
            count += 1
            if count > self.__max_request_numbers:
                print('Reached the maximum number of attempts')
                break
            if not response:
                sleep(0.5)
                print(
                    f'Try #{count} (from {self.__max_request_numbers}), status code is: {response.status_code}')
        return response

    def do_request(self, url: str, headers: dict, params: dict):
        """Обращение к ресурсу"""

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error: {http_err}')
        except Exception as err:
            print(f'{err}')
        else:
            return response

    def save_to_json_file(self, category: dict, data: dict):
        """Сохранение результата в файл"""

        with open(f'{self.pathdir + category["parent_group_code"]}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka(
        url_offers='https://5ka.ru/api/v2/special_offers/',
        url_categories='https://5ka.ru/api/v2/categories/',
        pathdir='./products/',
    )
    parser.parse()
