import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import pymongo

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument()
browser = webdriver.Chrome()

wait = WebDriverWait(browser, 10)
client = pymongo.MongoClient(MONGODB_HOST, MONGODB_POST)
db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

def login():
    print("正在登录")
    # 需要用手机淘宝扫二维码登录才能搜索
    browser.get(url='https://login.taobao.com')
    # 10s用来扫码登录
    browser.implicitly_wait(10)

def search():
    print("正在查找",KEYWORD)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        )
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#mainsrp-pager > div > div > div > div.total")))
        get_goods()
        return total.text
    except TimeoutError:
        return search()

def next_page(page_number):
    print("正在换页", page_number)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,
                                                     '#mainsrp-pager > div > '\
                                                     'div > div > ul > '\
                                                     'li.item.active > '\
                                                     'span'), str(page_number)))
        get_goods()
    except Exception:
        next_page(page_number)


def get_goods():
    try:

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                   '#mainsrp-itemlist .items '
                                                   '.item')))
        html = browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            goods = {
                'img': item.find('.pic .img').attr('data-src'),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text(),
                'title': item.find('.title').text(),
                'shop': item.find('.shop').text(),
                'location': item.find('.location').text()
            }
            save_to_mongodb(goods)
    except Exception:
        print("获取商品失败")

def save_to_mongodb(result):
    try:
        if db[MONGODB_COLLECTION].insert_one(result):
            print("存储到数据成功", result)
    except Exception:
        print("存储到数据库失败", result)

def main():
    login()
    total = search()
    total = int(re.compile('(\d+)').search(total).group(0))
    for i in range(2, total + 1):
        if i % 15 == 0:
            time.sleep(20)
        next_page(i)


if __name__ == '__main__':
    main()
