# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class MusicItem(scrapy.Item):
    music_name = scrapy.Field()
    artist_name = scrapy.Field()
    play_count = scrapy.Field()
    days_on_chart = scrapy.Field()


class DoubanMusicItem(scrapy.Item):
    # song_name = scrapy.Field()       # 歌曲名称
    # performer = scrapy.Field()       # 表演者
    # release_date = scrapy.Field()    # 发行时间
    # genre = scrapy.Field()           # 类型
    pass
