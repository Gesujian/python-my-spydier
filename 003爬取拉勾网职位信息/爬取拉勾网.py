import requests
import json
from pymongo import MongoClient
from multiprocessing import Pool
from urllib.parse import urlencode
import time

def get_one_page(pagenum):
    '''
    pagemun为页数，获取一页的信息
    :param pagenum:
    :return json:
    '''
    params = {
        'xl': '本科',
        'px': 'default',
        'gx': '全职',
        'needAddtionalResult': 'false',
        'isSchoolJob': '1'
    }
    data = {
    	'first': 'false' if pagenum != 1 else 'true',
    	'kd': 'python',
    	'pn': pagenum

    }
    headers = {
        'Host': 'www.lagou.com',
        'Connection': 'keep-alive',
        'Content-Length': '26',
        'Origin': 'https://www.lagou.com',
        'X-Anit-Forge-Code': '0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Anit-Forge-Token': 'None',
        'Referer': 'https://www.lagou.com/jobs/list_python?px=default&gx=%E5%85%A8%E8%81%8C&gj=&xl=%E6%9C%AC%E7%A7%91&isSchoolJob=1&city=%E5%85%A8%E5%9B%BD',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'WEBTJ-ID=20190328100105-169c2078019103-03287e499e7cc-7a1437-1327104-169c207801a0; _ga=GA1.2.1664461408.1553738469; _gid=GA1.2.1954202981.1553738469; user_trace_token=20190328100111-5bf04f0f-50fd-11e9-b40b-525400f775ce; LGUID=20190328100111-5bf053d7-50fd-11e9-b40b-525400f775ce; JSESSIONID=ABAAABAAADEAAFI9211681F55FF42AB9EE85C8EC6C94593; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_search; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22169c40de3e43ad-0357531209afde-7a1437-1327104-169c40de3e524d%22%2C%22%24device_id%22%3A%22169c40de3e43ad-0357531209afde-7a1437-1327104-169c40de3e524d%22%7D; sajssdk_2015_cross_new_user=1; _gat=1; LGSID=20190328201212-b7f050c6-5152-11e9-b9c8-525400f775ce; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DKbms6xfMqIUv7AMjnRPDL-xkTFJ6snHQGL9DF5fQumm%26wd%3D%26eqid%3De29fa16f0000d8bc000000035c9ca96a; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; SEARCH_ID=2798721a148d4f538908ca0bd396d4ac; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1553771063,1553775087,1553775136,1553775450; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1553775450; LGRID=20190328201727-7371eef8-5153-11e9-b831-5254005c3644'
    }
    base_url = "https://www.lagou.com/jobs/positionAjax.json?"
    url = base_url+urlencode(params)
    try:
        response = requests.post(url, headers=headers, data=data)
        print('页面获取成功')
        if response.status_code == 200:
            # print(response.json())
            return response.json()
    except requests.ConnectionError as e:
        print("error", e.args)
        return None

def parse_page(json):
    '''
    解析收到的信息
    :param json:
    :return dict:
    '''
    items = json.get('content').get('positionResult').get('result')
    if items:
        for item in items:
            try:
                # job
                positionName = item.get('positionName')
                positionLables = item.get('positionLables')
                salary = item.get('salary')
                jobNature = item.get('jobNature')
                education = item.get('education')
                # company
                city = item.get('city')
                district = item.get('district')
                companyShortName = item.get('companyShortName')
                industryField = item.get('industryField')
                financeStage = item.get('financ eStage')
                companyId = item.get('companyId')
                companyLabelList = item.get('companyLabelList')
                companySize = item.get('companySize')
            except:
                pass
            else:
                yield {
                    # job
                    'positionName': positionName,
                    'positionLables': positionLables,
                    'salary': salary,
                    'jobNature': jobNature,
                    'education': education,
                    # company
                    'city': city,
                    'district': district,
                    'companyShortName': companyShortName,
                    'industryField': industryField,
                    'financeStage': financeStage,
                    'companyId': companyId,
                    'companyLabelList': companyLabelList,
                    'companySize': companySize,
                }
def save_to_db(item, collection):
    '''
    保存数据导数据库
    :param item:
    :param collection:
    :return:
    '''
    result = collection.insert_one(item)
    print(result)

def main(pagenum):
    '''
    主函数，输入页码
    :param pagenum:
    :return:
    '''
    # 链接数据库并选择集合
    print('开始第{0}'.format(pagenum))
    client = MongoClient('mongodb://localhost:27017')
    db = client.lagou
    collection = db.pythonjob
    # 请求ajax数据，返回json
    json = get_one_page(pagenum)
    # 处理返回json数据并保存到的数据库
    for item in parse_page(json):
        print(item['positionName'])
       # 保存到数据库
        save_to_db(item, collection)


GROUP_START = 1
GROUP_STOP = 29
if __name__ == '__main__':
    # get_one_page(1)
    pool = Pool()
    group = ([x for x in range(GROUP_START, GROUP_STOP+1)])
    print(group)
    pool.map(main, group)
    pool.close()
    pool.join()

