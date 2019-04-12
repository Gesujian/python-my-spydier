import os
import requests
import json
from pymongo import MongoClient
from hashlib import md5
from multiprocessing import Pool
from urllib.parse import urlencode
import time
def get_page(offset):
    '''获取一页头条'''
    params = {'aid': '24',
              'app_name': 'web_search',
              'offset': offset,
              'format': 'json',
              'keyword': '街拍',
              'autoload': 'true',
              'count': '20',
              'en_qc': '1',
              'cur_tab': '1',
              'from': 'search_tab',
              'pd': 'synthesis',
              'timestamp': int(time.time()*1000//1)
              }
    headers = {
        'Accept': 'application/json, text/javascript',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.toutiao.com',
        'Referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://www.toutiao.com/api/search/content/?'
    url=base_url+urlencode(params)

    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print("error", e.args)
        return None

def parse_page(json):
    if json.get('data'):
        for item in json.get('data'):
            try:
                title = item.get('title')
                images = item.get('image_list')
            except:
                continue
            else:
                if title is None or images is None:
                    continue
                else:
                    for image in images:
                        yield {
                            'title': title,
                            'image': image.get('url')
                        }

def save_img(item):
    title = item.get('title')
    image = item.get('image')
    if not os.path.exists(title):
        os.makedirs(title)
    try:
        response = requests.get(image)
        if response.status_code == 200:
            file_path = "{0}/{1}.{2}".format(title,
                                             md5(response.content).hexdigest(),
                                             'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print("图片已存在", file_path)
    except requests.ConnectionError:
        print("保存图片失败")

def insert_into_mongodb(item, collection):
    result = collection.insert_one(item)
    print(result)

def main(offset):
    print("main",offset)
    client = MongoClient('mongodb://localhost:27017')
    db = client.toutiao
    collection = db.jiepai
    json = get_page(offset)
    for item in parse_page(json):
        print(item)
        save_img(item)
        insert_into_mongodb(item,collection)



GROUP_START = 0
GROUP_STOP = 20
if __name__ == '__main__':
    pool = Pool()
    group = ([x*20 for x in range(GROUP_START, GROUP_STOP+1)])
    print(group)
    pool.map(main, group)
    pool.close()
    pool.join()
    input()