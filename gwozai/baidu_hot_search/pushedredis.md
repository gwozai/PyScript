你可以使用 Python 和 Redis 进行交互，通过 `redis` 库连接 Redis 并将数据推送到 Redis 队列中。

以下是一个简单的 Python 脚本，用于将起始 URL 推送到 Redis 中的指定键。你可以使用这个脚本来为 `scrapy-redis` 爬虫提供起始 URL。

### 安装 Redis Python 客户端

首先，你需要确保 `redis` 库已安装。如果还没有安装，请运行以下命令：

```bash
pip install redis
```

### 提交 Redis 链接的 Python 代码

```python
import redis

# 连接到 Redis
redis_host = 'localhost'
redis_port = 6379

# 创建 Redis 连接
r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# 要推送的 URL（这个是你的爬虫的起始 URL）
start_url = "https://top.baidu.com/board?tab=realtime"

# 将 URL 推送到 Redis 列表（scrapy-redis 爬虫从这个列表中获取 URL）
redis_key = 'baidu_spider:start_urls'
r.lpush(redis_key, start_url)

print(f"Successfully pushed URL {start_url} to Redis queue '{redis_key}'")
```

### 解释代码

- **连接 Redis**：`redis.StrictRedis` 是连接 Redis 服务器的客户端，我们通过 `host` 和 `port` 参数指定 Redis 服务器的地址和端口。
- **推送数据到 Redis**：`r.lpush(redis_key, start_url)` 将起始 URL 推送到 Redis 中名为 `baidu_spider:start_urls` 的列表。这个列表将作为 `scrapy-redis` 爬虫的任务队列。
- **反馈信息**：代码会打印成功将 URL 推送到 Redis 队列中的信息。

### 运行 Python 脚本

1. 将此代码保存为 `push_to_redis.py` 文件。
2. 确保你的 Redis 服务器正在运行。
3. 运行此 Python 脚本：

```bash
python push_to_redis.py
```

成功执行后，起始 URL 就会被推送到 Redis 中，`scrapy-redis` 爬虫就会从这个队列中读取 URL 并开始爬取数据。