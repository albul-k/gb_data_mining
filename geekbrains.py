import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from time import sleep
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class ParserGeekBrains:
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    }

    __delay_between_try = 5

    __delay_between_request = 0.1

    def __init__(self, url_posts: str, url_comments: str):
        self.url_posts = url_posts
        self.url_comments = url_comments

        self.domain = self.get_domain(self.url_posts)

        self.engine = create_engine('sqlite:///gb_blog.db')
        models.Base.metadata.create_all(bind=self.engine)
        self.SessionMaker = sessionmaker(bind=self.engine)

    def get_domain(self, url: str) -> str:
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.hostname}"

    def get_response(self, url: str, headers: dict = None, params: dict = None) -> requests.Response:
        if not headers:
            headers = self.__headers

        while True:
            response = self.do_request(url, headers, params)
            if response:
                break
            else:
                sleep(self.__delay_between_try)
        return response

    def do_request(self, url: str, headers: dict = None, params: dict = None) -> requests.Response:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error: {http_err}')
        except Exception as err:
            print(f'{err}')
        else:
            return response

    def get_soup(self, response: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        pages_number = self.get_pages_number(self.url_posts)
        url_list = (
            f"{self.domain}/posts?page={i}" for i in range(1, pages_number + 1))
        for page_link in url_list:
            soup = self.get_soup(self.get_response(page_link))
            posts = soup.find(
                'div', attrs={'class': 'post-items-wrapper'}).contents
            post_links = [
                f"{self.domain}{post.a.attrs.get('href')}" for post in posts]
            for post_link in post_links:
                post_data = self.get_post_data(post_link)
                self.save_to(post_data)
                sleep(self.__delay_between_request)

    def get_comments(self, soup: BeautifulSoup) -> list:

        def get_comment_data(comments_json: list, comments_data: list = []) -> list:
            for comment in comments_json:
                comments_data.append({
                    'writer_url': comment.get('comment').get('user').get('url'),
                    'writer_name': comment.get('comment').get('user').get('full_name'),
                    'body': comment.get('comment').get('body'),
                })
                comment_children = comment.get('comment').get('children')
                if len(comment_children) != 0:
                    get_comment_data(comment_children, comments_data)
            return comments_data

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Range': f"0-{int(soup.find('comments').attrs.get('total-comments-count'))}",
        }
        params = {
            'commentable_type': soup.find('comments').attrs.get('commentable-type'),
            'commentable_id': int(soup.find('comments').attrs.get('commentable-id')),
            'order': 'desc',
        }

        response = self.get_response(
            self.url_comments, headers=headers, params=params)
        comments_json = json.loads(response.text)
        return get_comment_data(comments_json)

    def get_pages_number(self, url: str) -> int:
        soup = self.get_soup(self.get_response(url))
        return int(soup.find('ul', attrs={'class': 'gb__pagination'}).contents[-2].text)

    def get_post_data(self, url: str) -> dict:
        template = {
            'title': lambda soup: soup.find('h1', attrs={'itemprop': 'headline'}).text,

            'date': lambda soup: datetime.datetime.fromisoformat(soup.find('time', {'itemprop': 'datePublished'}).attrs.get('datetime')),

            'img_url': self.get_img_url,

            'tags': lambda soup: [tag.text for tag in soup.find_all('a', attrs={'class': 'small'})],

            'writer_url': lambda soup: f"{self.domain}{soup.find('div', attrs={'itemprop': 'author'}).parent.attrs.get('href')}",

            'writer_name': lambda soup: soup.find('div', attrs={'itemprop': 'author'}).text,

            'comments': self.get_comments,
        }

        post_data = {'url': url}
        post_soup = self.get_soup(self.get_response(url))
        for key, value in template.items():
            try:
                post_data[key] = value(post_soup)
            except Exception as e:
                print(e)
        return post_data

    def get_img_url(self, soup: BeautifulSoup) -> str:
        img_list = soup.find(
            'div', attrs={'itemprop': 'articleBody'}).select('p > img')
        if len(img_list) == 0:
            return None
        else:
            return img_list[0].attrs.get('src')

    def save_to(self, post_data: dict):
        db = self.SessionMaker()

        tags = post_data.get('tags')
        for tag_name in tags:
            tag = models.Tag(name=tag_name)
            if db.query(models.Tag).filter(models.Tag.name == tag.name).first() is None:
                db.add(tag)
                db.commit()

        writer = models.Writer(
            url=post_data.get('writer_url'),
            name=post_data.get('writer_name'),
        )
        writer_db = db.query(models.Writer).filter(
            models.Writer.url == writer.url).first()
        if writer_db is None:
            db.add(writer)
            db.commit()
        else:
            writer = writer_db

        post = models.Post(
            url=post_data.get('url'),
            title=post_data.get('title'),
            date=post_data.get('date'),
            img_url=post_data.get('img_url'),
            writer_id=writer.id,
            writer=db.query(models.Writer).filter(
                models.Writer.id == writer.id).first(),
            tags=[db.query(models.Tag).filter(models.Tag.name ==
                                              tag_name).first() for tag_name in tags],
        )
        if db.query(models.Post).filter(models.Post.url == post.url).first() is None:
            db.add(post)
            db.commit()

        comments_list = post_data.get('comments')
        for comment_dict in comments_list:
            writer = models.Writer(url=comment_dict.get(
                'writer_url'), name=comment_dict.get('writer_name'))
            if db.query(models.Writer).filter(models.Writer.url == writer.url).first() is None:
                db.add(writer)
                db.commit()
            writer = db.query(models.Writer).filter(
                models.Writer.url == writer.url).first()
            post = db.query(models.Post).filter(
                models.Post.url == post.url).first()
            comment = models.Comment(
                writer_id=writer.id,
                post_id=post.id,
                content=comment_dict.get('body'),
                writer=writer,
                post=post,
            )
            db.add(comment)
            db.commit()

        db.close()


if __name__ == '__main__':
    parser = ParserGeekBrains(
        url_posts='https://geekbrains.ru/posts',
        url_comments='https://geekbrains.ru/api/v2/comments',
    )
    parser.parse()
