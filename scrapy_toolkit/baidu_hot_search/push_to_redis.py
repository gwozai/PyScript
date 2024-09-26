import redis

# 连接到 Redis
redis_host = '1.15.7.2'
redis_port = 6372

# 创建 Redis 连接
r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# 要推送的 URL（这个是你的爬虫的起始 URL）
start_url = "https://top.baidu.com/board?tab=realtime"

# 将 URL 推送到 Redis 列表（scrapy-redis 爬虫从这个列表中获取 URL）
redis_key = 'baidu_spider:start_urls'
r.lpush(redis_key, start_url)

print(f"Successfully pushed URL {start_url} to Redis queue '{redis_key}'")
