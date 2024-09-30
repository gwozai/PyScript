import scrapy
import pymysql
from lxml import etree
import re
from scrapy.http import Request


class DoubanMusicChartSpider(scrapy.Spider):
    name = "douban_music_chart"
    allowed_domains = ["douban.com"]
    start_urls = ['https://music.douban.com/chart']

    # MySQL 配置
    mysql_config = {
        'host': '1.15.7.2',
        'port': 3306,
        'user': 'douban',
        'password': 'SaXPNzGdXR53XrnY',
        'db': 'douban',
        'charset': 'utf8mb4'
    }

    def __init__(self, *args, **kwargs):
        super(DoubanMusicChartSpider, self).__init__(*args, **kwargs)
        # 连接到MySQL
        self.connection = pymysql.connect(
            host=self.mysql_config['host'],
            port=self.mysql_config['port'],
            user=self.mysql_config['user'],
            password=self.mysql_config['password'],
            database=self.mysql_config['db'],
            charset=self.mysql_config['charset']
        )

    def parse(self, response):
        """
        解析排行榜页面，获取前10名音乐数据
        """
        html = etree.HTML(response.text)
        music_list = []

        for i in range(1, 11):
            try:
                # 获取音乐名称
                music_name = html.xpath(f'//*[@id="content"]/div/div[1]/div/ul/li[{i}]/div/h3/a/text()')[0].strip()

                # 获取艺术家和播放次数字符串
                artist_play = html.xpath(f'//*[@id="content"]/div/div[1]/div/ul/li[{i}]/div/p/text()')[0].strip()

                # 替换掉不可见空格符号
                artist_play = re.sub(r'\u00a0', ' ', artist_play)

                # 解析艺术家和播放次数
                match = re.search(r'(.+?)\s*/\s*([\d,]+)\s*次播放', artist_play)
                if match:
                    artist = match.group(1).strip()  # 提取艺术家名字
                    play_count = int(match.group(2).replace(',', ''))  # 提取播放次数，并去掉逗号
                else:
                    # 如果未能匹配到，默认艺术家名称为整体文本，播放次数为0
                    artist = artist_play
                    play_count = 0

                # 提取上榜天数
                days_on_chart = html.xpath(f'//*[@id="content"]/div/div[1]/div/ul/li[{i}]/span[@class="days"]/text()')
                if days_on_chart:
                    days = re.sub(r'\D+', '', days_on_chart[0])  # 提取纯数字的天数
                else:
                    days = '0'  # 如果上榜天数缺失，设置为0

                music_list.append((music_name, artist, play_count, int(days)))
                self.log(f"成功解析第 {i} 条数据：{music_name}, {artist}, {play_count}, {days}天")

            except IndexError:
                self.log(f"第 {i} 条数据不完整，跳过。")
            except Exception as e:
                self.log(f"解析第 {i} 条数据时出错: {e}")
                continue

        print(music_list)

        self.save_to_db(music_list)

    def save_to_db(self, music_list):
        """
        将抓取到的音乐数据保存到MySQL数据库
        """
        try:
            with self.connection.cursor() as cursor:
                # 创建表
                create_table_query = """
                CREATE TABLE IF NOT EXISTS musics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    music_name VARCHAR(255),
                    artist_name VARCHAR(255),
                    play_count INT,
                    days_on_chart INT
                );
                """
                cursor.execute(create_table_query)

                # 插入数据
                insert_query = """
                INSERT INTO musics (music_name, artist_name, play_count, days_on_chart)
                VALUES (%s, %s, %s, %s);
                """
                cursor.executemany(insert_query, music_list)

            self.connection.commit()
            self.log("数据已成功保存到数据库")
        except pymysql.MySQLError as e:
            self.log(f"保存数据到 MySQL 时出错: {e}")

    def close(self, reason):
        """
        爬虫结束时关闭数据库连接
        """
        self.connection.close()
        self.log("MySQL 连接已关闭")
