import re
import requests
import time
import json
from requests.exceptions import RequestException

def get_one_page(url):
    '''
    获取猫眼top100的一页源码
    输入网页url
    输出源码'''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0)'
                          ' Gecko/20100101 Firefox/66.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(200)
            return response.text
        return None
    except RequestException:
        return None

def parser_one_page(html):
    '''
    解析一页的10部电影信息
    输入html对象
    输出需要的信息->dict
    <dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>.*?"star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>
    '''
    # regex='<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(' \
    #      '.*?)</a>.*?"star">(.*?)</p>.*?"releasetime">(.*?)</p>.*?"integer">(' \
    #      '.*?)</li>.*?"fraction">(.*?)</i>'
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?data-src="('+
                         '.*?)".*?"name"><a.*?>(.*?)</a>.*?star">('+
                         '.*?)</p>.*?releasetime">(.*?)</p>.*?integer">('+
                         '.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for i in items:
        yield {
            'index': i[0],
            'image': i[1],
            'name': i[2],
            'actor': i[3].strip()[3:],
            'releasetime': i[4].strip()[5:],
            'score': i[5]+i[6],
        }

def write_to_file(content):
    '''将处理完成的文件放到
    输入处理好的内容
    将内容存储到文件'''
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')

def main(offset):
    '''输入每一页的偏移量'''
    url = "https://maoyan.com/board/4?offset="+str(offset)
    html = get_one_page(url)
    contents = parser_one_page(html)
    for item in contents:
        print(item)
        write_to_file(item)

if __name__ == "__main__":
    for i in range(10):
        main(i*10)
        time.sleep(1)