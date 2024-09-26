import scrapy
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup


class BaiduHotSearchSpider(RedisSpider):
    name = 'baidu_spider'

    # 这是 Redis 中的 key，启动爬虫时从这个键中获取起始 URL
    redis_key = 'baidu_spider:start_urls'

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        hot_searches = []
        for item in soup.find_all('div', {'class': 'c-single-text-ellipsis'}):
            hot_searches.append(item.text.strip())

        for index, search in enumerate(hot_searches, 1):
            yield {
                'rank': index,
                'search_term': search
            }
