# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Request
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import os


class GbparsPipeline:

    def __init__(self) -> None:
        db_client = MongoClient()
        self.db = db_client['insta']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item


class GbparsImagesPipeline(ImagesPipeline):

    path_checksums = './image/'

    filename_checksums = 'list.txt'

    def __init__(self, *args, **kwargs) -> None:

        self.checksums = set()
        self.path_to_checksums = os.path.join(
            self.path_checksums, self.filename_checksums)

        if not os.path.exists(self.path_checksums):
            os.makedirs(self.path_checksums)
        else:
            try:
                with open(self.path_to_checksums, 'r', encoding='UTF-8') as f:
                    for str in f:
                        self.checksums.add(str[:-1])
            except IOError:
                pass
        super().__init__(*args, **kwargs)

    def get_media_requests(self, item, info):
        images = item.get('img',
                          item['data'].get('profile_pic_url',
                                           item['data'].get('display_url', [])
                                           )
                          )

        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]

            checksum = item['img'][0]['checksum']
            if not checksum in self.checksums:
                self.checksums.add(checksum)
                try:
                    with open(self.path_to_checksums, 'a', encoding='UTF-8') as f:
                        f.write(checksum + '\n')
                except IOError as e:
                    print(e)
        except KeyError:
            pass
        return item
