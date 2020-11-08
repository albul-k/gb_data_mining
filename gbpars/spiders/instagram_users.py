"""
Пройти по произвольному списку имен пользователей.

собрать в единую структуру на кого подписан пользователь и кто подписан на пользователя
"""


import datetime as dt
import json
import scrapy
from ..items import InstagramUser


class InstagramUsersSpider(scrapy.Spider):
    name = 'instagram_users'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'followers': "c76146de99bb02f6415203be841dd25a",
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
    }

    def __init__(self, login, enc_password, *args, **kwargs) -> None:
        self.users = ['thehughjackman', 'vindiesel', 'leonardodicaprio']
        self.login = login
        self.enc_passwd = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_passwd,
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token'],
                }
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_parse)

    def user_parse(self, response):
        user = self.js_data_extract(
            response)['entry_data']['ProfilePage'][0]['graphql']['user']

        variables = {
            'id': user['id'],
            'include_reel': 'true',
            'fetch_mutual': 'false',
            'first': 100,
        }

        relations = (
            {
                'edge': 'edge_followed_by',
                'query_hash': self.query_hash['followers']
            },
            {
                'edge': 'edge_follow',
                'query_hash': self.query_hash['following']
            },
        )

        for relation in relations:
            url = f"{self.api_url}?query_hash={relation['query_hash']}&variables={json.dumps(variables)}"
            yield response.follow(
                url,
                callback=self.relations_parse,
                cb_kwargs={
                    'user_id': user['id'],
                    'edge': relation['edge'],
                    'query_hash': relation['query_hash'],
                },
            )

    def relations_api_parse(self, response, **kwargs):
        yield from self.relations_parse(
            response,
            user_id=kwargs['user_id'],
            edge=kwargs['edge'],
            query_hash=kwargs['query_hash'],
        )

    def relations_parse(self, response, **kwargs):
        user = response.json()['data']['user']
        if user[kwargs['edge']]['page_info']['has_next_page']:
            variables = {
                'id': kwargs['user_id'],
                'include_reel': 'true',
                'fetch_mutual': 'false',
                'first': 100,
                'after': user[kwargs['edge']]['page_info']['end_cursor'],
            }

            url = f"{self.api_url}?query_hash={kwargs['query_hash']}&variables={json.dumps(variables)}"
            yield response.follow(
                url,
                callback=self.relations_api_parse,
                cb_kwargs={
                    'user_id': kwargs['user_id'],
                    'edge': kwargs['edge'],
                    'query_hash': kwargs['query_hash'],
                },
            )

        yield from self.get_user_item(user[kwargs['edge']]['edges'])

    @staticmethod
    def get_user_item(nodes):
        for node in nodes:
            yield InstagramUser(
                date_parse=dt.datetime.utcnow(),
                data={
                    'id': node['node']['id'],
                    'username': node['node']['username'],
                    'full_name': node['node']['full_name'],
                    'profile_pic_url': node['node']['profile_pic_url'],
                }
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath(
            '//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])
