出现这种情况是因为 Scrapy-Redis 的设计允许多个爬虫共享同一个 Redis 队列。当有多个爬虫实例时，如果队列中没有新的任务可供处理，其中一个爬虫会一直等待。

以下是可能的原因和解决方案：

### 原因 1: Redis 队列中没有足够的 URL

当队列中只有一个 URL 时，可能只有一个爬虫实例会处理该 URL，处理完成后，其他爬虫实例会一直等待新的任务。如果你只推送了一个 URL，其他实例可能会处于“空闲”状态，直到新的 URL 被推送到队列中。

#### 解决方案
你可以在 Redis 中推送多个 URL，这样每个爬虫实例都有任务可以处理。

```bash
redis-cli lpush baidu_spider:start_urls "https://top.baidu.com/board?tab=realtime"
redis-cli lpush baidu_spider:start_urls "https://top.baidu.com/board?tab=film"
redis-cli lpush baidu_spider:start_urls "https://top.baidu.com/board?tab=novel"
```

每次 `lpush` 命令会将新的 URL 添加到 Redis 队列，爬虫实例会从队列中依次获取任务。

### 原因 2: 爬虫已经处理完所有的任务

Scrapy-Redis 的爬虫会一直监听 Redis 队列，如果队列中没有新的请求，它们会处于等待状态。只要队列中有新的任务，爬虫会继续工作。

#### 解决方案
如果你需要爬虫在任务完成后自动关闭，可以设置 `CLOSESPIDER_TIMEOUT` 参数，这样在等待一段时间后，爬虫会自动关闭。

在 `settings.py` 中添加以下配置：

```python
CLOSESPIDER_TIMEOUT = 30  # 如果 30 秒内没有新的请求，爬虫会关闭
```

这将设置 Scrapy 在等待 30 秒后没有新的请求时自动关闭。

### 原因 3: Redis 中的调度问题

如果你希望每个爬虫实例都能并行处理任务，确保你使用的是基于优先级的队列调度器（即 `SpiderPriorityQueue`）。这是 Scrapy-Redis 默认使用的队列调度器，它可以有效地管理并行爬取。

在 `settings.py` 中检查调度器配置：

```python
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
```

这个配置确保多个爬虫实例可以并行从队列中获取任务。

### 总结

如果你同时运行了多个爬虫实例，但只有一个实例在工作，而另一个实例在等待，这通常是因为 Redis 队列中缺少足够的任务。当爬虫从 Redis 队列中获取到 URL 并处理完成后，其他爬虫实例会等待新的任务。

你可以通过以下几种方式解决：
1. 推送更多的 URL 到 Redis 队列。
2. 设置 `CLOSESPIDER_TIMEOUT`，让爬虫在任务完成后自动关闭。
3. 确保 `SCHEDULER_QUEUE_CLASS` 的配置是 `SpiderPriorityQueue`。

如果这些解决方案没有解决问题，请提供更多的日志信息，我可以帮助进一步排查。