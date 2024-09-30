# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class DoubanMusicPipeline:
    def process_item(self, item, spider):
        print("======================================================================")
        print(item)
        logging.WARNING('==========================')
        return item
