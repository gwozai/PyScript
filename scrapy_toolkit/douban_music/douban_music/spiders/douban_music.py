import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
import urllib.request
import random
import cv2
from lxml import html
import pymongo  # 引入 pymongo 库


class DoubanMusicSpider(scrapy.Spider):
    name = "douban_music"
    allowed_domains = ["douban.com", "accounts.douban.com"]
    start_urls = ['https://accounts.douban.com/passport/login']

    def __init__(self, *args, **kwargs):
        super(DoubanMusicSpider, self).__init__(*args, **kwargs)
        # MongoDB 连接设置
        self.client = pymongo.MongoClient("mongodb://1.15.7.2:27017/")
        self.db = self.client["douban"]
        self.collection = self.db["musics"]

    def parse(self, response):
        driver = self.driver
        self.login(driver)
        genres = ["民谣", "流行"]
        for genre in genres:
            self.fetch_music_data(genre, driver)

    def login(self, driver):
        passClick = driver.find_element(By.XPATH, '//*[@id="account"]/div[2]/div[2]/div/div[1]/ul[1]/li[2]')
        passClick.click()
        driver.implicitly_wait(3)

        userInput = driver.find_element(By.ID, "username")
        userInput.send_keys("19834858827")
        passInput = driver.find_element(By.ID, "password")
        passInput.send_keys("Qq123456")
        time.sleep(3)
        loginButton = driver.find_element(By.XPATH, '//*[@id="account"]/div[2]/div[2]/div/div[2]/div[1]/div[4]/a')
        loginButton.click()
        driver.implicitly_wait(5)

        driver.switch_to.frame("tcaptcha_iframe_dy")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'slideBg')))

        bigImage = driver.find_element(By.ID, "slideBg")
        s = bigImage.get_attribute("style")
        p = 'background-image: url\(\"(.*?)\"\);'
        bigImageSrc = re.findall(p, s, re.S)[0]
        print("滑块验证图片下载路径:", bigImageSrc)

        urllib.request.urlretrieve(bigImageSrc, 'bigImage.png')

        dis = self.get_pos('bigImage.png')

        smallImage = driver.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]')
        newDis = int(dis * 340 / 672 - smallImage.location['x'])
        driver.implicitly_wait(5)

        ActionChains(driver).click_and_hold(smallImage).perform()

        i = 0
        moved = 0
        while moved < newDis:
            x = random.randint(3, 10)
            moved += x
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
            print(f"第{i + 1}次移动后，位置为{smallImage.location['x']}")
            i += 1

        ActionChains(driver).release().perform()
        time.sleep(5)

    def fetch_music_data(self, genre, driver):
        base_url = 'https://music.douban.com/tag/{}?start=0&type=T'.format(genre)
        driver.get(base_url)

        for page_num in range(6):
            print(f"正在抓取 {genre} 第 {page_num + 1} 页")
            time.sleep(2)  # 等待页面加载

            page_source = driver.page_source
            tree = html.fromstring(page_source)

            data = self.parse_page(tree)
            # 保存数据到 MongoDB
            if data:
                self.collection.insert_many(data)

            try:
                next_page = driver.find_element(By.XPATH, '//*[@id="subject_list"]/div[22]/span[4]/a')
                next_page.click()
            except:
                print("没有更多页面了")
                break
        print("数据已保存到Mongodb中")

    def parse_page(self, tree):
        tables = tree.xpath('//*[@id="subject_list"]/table')
        data = []
        for table in tables:
            song_name = table.xpath('.//td[2]/div/a/text()')[0].strip()
            details = table.xpath('.//td[2]/div/p[1]/text()')[0].strip()
            parts = [part.strip() for part in details.split('/')]

            if len(parts) == 3:
                performer, release_date, genre = parts
            elif len(parts) > 3:
                performer, release_date, genre = parts[:3]
            else:
                performer = parts[0] if len(parts) > 0 else "未知表演者"
                release_date = parts[1] if len(parts) > 1 else "未知发行时间"
                genre = "未知类型"

            data.append({
                '歌曲名称': song_name,
                '表演者': performer,
                '发行时间': release_date,
                '类型': genre
            })
        print(data)
        return data

    def get_pos(self, imageSrc):
        image = cv2.imread(imageSrc)
        blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
        canny = cv2.Canny(blurred, 0, 100)
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            length = cv2.arcLength(contour, True)
            if 5025 < area < 7225 and 300 < length < 380:
                x, y, w, h = cv2.boundingRect(contour)
                print("计算出目标区域的坐标及宽高：", x, y, w, h)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.imwrite("111.jpg", image)
                return x
        return 0
