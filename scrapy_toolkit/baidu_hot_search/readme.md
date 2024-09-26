要将你提供的代码改造成一个基于 `scrapy-redis` 的分布式爬虫项目，可以按照以下步骤来操作。我将从创建项目开始，然后展示如何将代码转化为 Scrapy 爬虫，并使用 Redis 来进行调度。

### 步骤 1：安装依赖

首先，安装必要的依赖项，包括 `scrapy` 和 `scrapy-redis`。

```bash
pip install scrapy scrapy-redis
pip install beautifulsoup4 lxml

```

### 步骤 2：创建 Scrapy 项目

使用 Scrapy 的命令行工具创建一个新项目：

```bash
scrapy startproject baidu_hot_search
```

这将创建一个名为 `baidu_hot_search` 的 Scrapy 项目。

### 步骤 3：创建 Scrapy-Redis 爬虫

在 `spiders` 目录下，创建一个新的爬虫文件 `baidu_spider.py`，并将爬虫继承自 `RedisSpider`。

```bash
cd baidu_hot_search/baidu_hot_search/spiders
touch baidu_spider.py
```

在 `baidu_spider.py` 中编写爬虫代码：

```python
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
```

### 步骤 4：配置 Scrapy-Redis

接下来，我们需要配置 Scrapy 以使用 Redis 作为调度器和去重机制。

在项目的 `settings.py` 中，添加以下配置：

```python
# Redis 配置
REDIS_HOST = 'localhost'  # Redis 的主机地址
REDIS_PORT = 6379         # Redis 的端口

# 使用 scrapy-redis 提供的调度器和去重类
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 请求队列持久化
SCHEDULER_PERSIST = True

# 使用 scrapy-redis 的请求优先级队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# 存储数据的管道 (可选，存储到 Redis)
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
}

# 日志级别
LOG_LEVEL = 'DEBUG'
```

### 步骤 5：向 Redis 中添加起始 URL

启动 Redis 后，通过 Redis CLI 添加起始 URL，这会将 URL 推送到 Redis 中，以供爬虫使用。

```bash
redis-cli lpush baidu_spider:start_urls "https://top.baidu.com/board?tab=realtime"
```

这将把百度热搜页面的 URL 添加到 Redis 队列中，爬虫将从该 URL 开始抓取数据。

### 步骤 6：运行爬虫

最后，运行爬虫：

```bash
scrapy crawl baidu_spider
```

### 分布式运行

你可以在不同的终端或服务器上启动多个 Scrapy 实例来实现分布式抓取，所有实例都会共享同一个 Redis 队列：

```bash
scrapy crawl baidu_spider
```

每个爬虫实例都会从 Redis 队列中读取 URL 并进行抓取，同时避免重复抓取相同的内容。

### 总结

通过使用 `scrapy-redis`，你已经构建了一个基于 Redis 的分布式爬虫系统，该系统可以抓取百度热搜数据，并可以通过多个爬虫实例来并行抓取数据。

Redis 在这个系统中充当了请求队列、去重机制和数据存储的角色，使得系统具备了高效分布式爬虫的能力。