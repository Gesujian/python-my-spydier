>清明时节雪纷纷，路上行人欲断魂。借问寝室和处在，室友遥指积雪痕。

为什么要用IP代理，我就不多说了。直接进入正题。

我们在使用爬虫时需要换代理时，总是希望能找到稳定快速的代理，但是网上大多数免费代理的很多都是不可用的，每次换都要先判断这个代理是否可用。为了省去这一麻烦的步骤，IP代理池就出现了。

我的目的是自己维护一个的代理池，他定时获取新的代理，定时的去检测代理的可用性，并赋予权值、分数，提供api接口，我们需要的时候直接请求api就行了。

分为四大模块：
- 存储模块
- 获取模块
- 检测模块
- 接口模块

其中存储模块是中枢，连接着其他三个模块。
```
获取模块----------->存储模块<--------------->检测模块
                      |
                      |
                      |
                      |
                      V
                   接口模块
```
大概是这么个结构。

今天先说存储模块 ：
这里我用的Redis数据库的有序集合来存储代理，因为集合具有唯一性等特点，可以去重，而且集合有序，可以方便查找。

直接上代码：**中间遇到了不少坑，下面说**：
```
import redis
from random import choice

MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies'


class PoolEmptyError(Exception):
    def __init__(self, error_info='IP代理池为空，无法提供有效代理'):
        # super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class RedisClient:
    """定义一个Redis服务器

    连接本地Redis数据库，并提供相关方法"""
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT,
                 password=REDIS_PASSWORD):
        """连接接数据库

        :param host: Redis地址
        :param port: Redis地址
        :param password: Redis密码"""
        self.db = redis.StrictRedis(host=host, port=port, password=password,
                                    decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """添加新的IP代理

        :param proxy: 代理
        :param score: 分数
        :return : 添加结果"""
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, {proxy: score})

    def random(self):
        """随机返回一个代理

        如果有100分的代理，随机返回一个；
        如果没有100分的，则按照分数排名获取分数最高的
        如果都没有则返回异常

        :return: 随机代理"""
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def decrease(self, proxy):
        """将检测出不可用的代理的分数减一分，如果分数小于最小值，则从代理池中删除

        :param proxy: 代理地址及端口
        :return: 修改后的代理分数"""
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            print('代理', proxy, '当前分数', score, '删除')
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """判断IP代理是否存在

        :param proxy: 代理ip
        :return： 是否存在->bool"""
        return self.db.zscore(REDIS_KEY, proxy) is not None

    def max(self, proxy):
        """将代理的分数设置为MAX_SCORE

        :param proxy: 代理ip
        :return: 设置结果"""
        print('代理', proxy, '可用，设置为',MAX_SCORE)
        return self.db.zadd(REDIS_KEY, {proxy: MAX_SCORE})

    def count(self):
        """返回数据库中的代理数量

        :return: 数量->int"""
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """返回数据库中的所有代理

        :return: 全部代理"""
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)


# p=RedisClient()
# proxy = '11.1.1.1:8080'
# p.add(proxy, 10)
# p.decrease(proxy)
# print(p.exists(proxy))
# p.max(proxy)
# print(p.count())
# print(p.all())
"""
获取模块----------->存储模块<--------------->检测模块
                      |
                      |
                      |
                      |
                      V
                   接口模块
"""
```

#####遇到的坑：
- 对自定义异常类不熟悉，定义了一个PoolEmptyError，而且也不清楚什么时候应该报异常，而不是过滤错误。
- redis库在操作数据库时有序结合的一个方法：zadd()，这个函数，书上和网上给的例子都是：zadd(redis_key, 'bob', 10)或者zadd(redis_key, 10, 'bob')，等类似这样的调用方法，但是这样会报错。自己试一下就知道了，我忘记怎么说的了。正确的用法：**zadd(redis_key, {'bob': 100})**
- 判断是否为空时要用：is | is not  ，而不是==
- 筛选函数zincrby() 的调用，网上书上是：zincrby(redis_key, 'bob',-1) 类似这样的调用，本意是让bob的score减一，但是他参数写反了，应该是：**zincrby(redis_key, -1,'bob')**

最后，我用下面的注释写了简单的单元测试，保证每一个方法都可以正常调用。

明天写获取模块。


---
####新的一天
>最近突然有所松懈，突然间变得好累。早上起不来，上午没精神，下午没体力，晚上没效率。学习的动力似乎突然消失。我怎么了？
似乎是休息方面除了问题，持续一个多月的学习，没有运动过，更别说出去走走，散散心。好不容易来的清明假期，也没有出去玩，我似乎失去了活力、激情。记得当年学习时除了精力不允许时，我总是很活跃，上了大学以后不知怎么了，失去了活力，失去了激情，失去了那种冲动。很怀念那个想什么做什么的我。

不说了，进入正题。接着昨天的文，今天写获取模块，从各大网站上获取代理。
我选了代理66、快代理、旗云代理这三个代理网站，作为代理的来源。

这次我跟着书上做的，遇到了点问题。由于我基础不太好，对与面对对象编程的掌握不到位，并不能理解抽象基类的使用。总之先给代码：
```
from pyquery import PyQuery as pq
import requests


class ProxyMetaclass(type):
    """定义一个抽象基类，来获取以crawler_开头的方法"""
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count +=1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
    """从各大网站提取代理"""
    def get_proxies(self, callback):
        """获取代理

        :param callback: 调用的方法名称
        :return: 返回得到的代理列表"""
        proxies = []
        for proxy in eval("self.{}()").format(callback):
            print('成功获取到代理', proxy)
            proxies.append(proxy)
        return proxies

    def crawl_daili66(self, page_count=4):
        """从代理66上获取代理

        :param page_count:页码
        :return: 代理"""
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = requests.get(url)
            if html:
                doc = pq(html.text)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])

    def crawl_kuaidaili(self,page_count=4):
        """从快代理上获取代理

        :param page_count:页码
        :return: 代理"""
        start_url = 'https://www.kuaidaili.com/free/inha/{}/'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = requests.get(url)
            if html.status_code == 200:
                doc = pq(html.text)
                trs = doc('tbody tr')
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])

    def crawl_qiyundaili(self, page_count=4):
        """从旗云代理上获取代理

        :param page_count:页码
        :return: 代理"""
        start_url = 'http://www.qydaili.com/free/?action=china&page={}'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = requests.get(url)
            if html.status_code == 200:
                doc = pq(html.text)
                trs = doc('tbody tr').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])
```

首先我定义了一个ProxyMetaclass的元类，也就是抽象基类。这是为了获取所有以‘crawl_’开头的方法定义的，虽然我现在看不懂，但是书上这么说的。

先过这里，下面的三个方法就是我们获取代理的函数。我就不讲了，太简单了。三个页面源码差不多。唯一注意的地方，就是你用的requests还是urllib，这两个源码的烈性不一样，一个要调用text属性，一个要调用read()方法。还有就是pyquery的使用，说实话很好用。我觉的比beautifulsoup好使。

现在不知道怎么了，写完了这个水之又水的文，我就不想学了，想睡了。不行啊!!!

昨天投了6份简历，只有一份被查看了。。。。然后就没然后了。。。。。还是学的不够好，简历也不够吸引人。

我发现所有的书，越写越烂，我看书也是越来越没动力。

---
#####又是新的一天
前天写了存储模块，昨天写了获取模块，今天写了检测模块。

我们通过获取模块得到了各大代理网站的ip代理地址和端口，用存储模块将得到的代理存储到redis数据库中，并用检测模块从数据库中读取IP代理进行检测，给代理打分。

检测模块的原理是这样的，从数据库中调用代理，并用这个代理去访问设定的网站，查看是否可用，以此更改代理分数。

这里用的是aiohttp异步访问，因为有的代理访问速度慢，所以需要等待一段时间，在程序等待返回结果的时候我们可以让程序去执行别的任务，加快检测的效率。

异步io我没学明白。就跟着书做了。之后的结果我们还要用一个调度模块来实现。

代码：
```
import aiohttp
import asyncio
import time
from saver import RedisClient
from aiohttp.client import ClientConnectorError
from aiohttp.client import ClientError


VALID_STATUS_CODES = [200]
TEST_URL = 'http://www.baidu.com'  # 应该改成要爬取的网站
BATCH_TEST_SIZE = 100


class Tester(object):
    """测试代理的可用性"""
    def __init__(self):
        """连接数据库"""
        self.redis = Redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """测试单个代理

        :param proxy: 代理
        :return: None"""
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(TEST_URL, proxy=real_proxy,
                                       timeout=15) as respone:
                    if respone.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应不合法', proxy)
            except (TimeoutError, AttributeError, ClientError,
                    ClientConnectorError):
                self.redis.decrease(proxy)
                print('代理请求失败')

    def run(self):
        """测试主函数"""
        print('测试器开始运行')
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            # 批量测试
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i:BATCH_TEST_SIZE + i]
                task = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(task))
                time.sleep(5)
        except Exception as e:
            print('测试器发生故障', e.args)
```

异步IO等我买了《流畅的python》之后再研究吧，手边没有好的学习资源。

我不太喜欢看视频学习，更喜欢看书自己学习。不知道为什么，身边的人都更喜欢看视频学习。
我看视频学习，看的时候非常清楚，等看完了，也就完了，什么也没记住。。。

可能我比较传统吧。。但是不是啊。。。

现在一边看数据结构和算法，一边看爬虫，有点忙不过来。。。

----
#####再一次新的一天

api接口是为了让我们能够通过简单的request就能得到一个可用的随机代理而设计的，它使程序不需要向本地主机的redis数据库获取代理。这样方便我们将他部署到服务器上，随时可以调用。

这里我用了Flask这个轻量级web开发框架，简单的生成了一个web程序程序，并在127.0.0.1:5000这个端口开放。每次只要访问/random就可以直接得到一个代理了。

代码：
```
from flask import Flask,g
from saver import RedisClient


__all__ = ['app']
app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis

@app.route('/')
def index():
    return '<h2>Welcome to Proxy Pool Systeml </h2>'

@app.route('/random')
def get_proxy():
    """随机获取可用代理"""
    conn = get_conn()
    return conn.random()

@app.route('/count')
def get_counts():
    """获取代理池总量"""
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run()

```
我们运行之后解雇如下，控制台输出：

![控制台](https://upload-images.jianshu.io/upload_images/15391438-6c5e4d2bbc9c4e67.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我们打开浏览器访问这个端口，可以看到如下：

![image.png](https://upload-images.jianshu.io/upload_images/15391438-67c02167f1627050.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我们访问/random

![代理](https://upload-images.jianshu.io/upload_images/15391438-fd7717ea055ae649.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

之后我们只需要向这个端口发送请求就可以得到代理了。

这个真的没什么难度。

突然想去看看python后端开发的东西了，等我学完手边的爬虫书吧！

---

#####还有两天

前几天开始的IP代理池维护今天终于要见成果了。

我们一共写了4个模块：
```
获取模块----------->存储模块<--------------->检测模块
                      |
                      |
                      |
                      |
                      V
                   接口模块
```

一共四个模块：获取模块（crawler.py）、存储模块（saver.py）、检测模块（tester.py）、接口模块（api.py），其中获取模块我用了一个getter.py来调度爬虫，将数据存到数据库。

getter.py

---
```
from saver import RedisClient
from crawler import Crawler


POOL_UPPER_THRESHOLD = 10000


class Getter():
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """判断是否达到了代理池限制"""
        if self.redis.count() > POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        """调度获取器"""
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_lable in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_lable]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)
```

有了这个getter之后，我们就可以写run.py来串联所有的模块，让程序运行起来。

```
import time
from api import app
from getter import Getter
from tester import Tester
from multiprocessing import Process

TESTER_CYCLE = 30
GETTER_CYCLE = 30
TESTER_ENABLE = True
GETTER_ENABLE = True
API_ENABLE = True


class Scheduler():
    def schedule_tester(self, cycle=TESTER_CYCLE):
        """定时检测代理"""
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        """定时获取代理"""
        getter = Getter()
        while True:
            print('获取器开始运行')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """开启api"""
        app.run()

    def run(self):
        """运行代理池"""

        # 开放api
        if API_ENABLE:
            api_process = Process(target=self.schedule_api)
            api_process.start()

        # 开始循环测试
        if TESTER_ENABLE:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()

        # 开始循环获取新的代理
        if GETTER_ENABLE:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()


if __name__ == '__main__':
    p = Scheduler()
    p.run()
```

这里我们用了多进程，让getter、tester、和api一直运行下去，getter定时调用爬虫爬取各大免费ip代理网站，tester定时检测代理的可用性。getter将的得到代理存到数据库，tester从数据库取代理检测可用性，判定分数。api一直开启，在127.0.0.1:5000端口提供随机代理。

注意！运行前一定要开启数据库。
这个程序调度三个模块，让他们同时运行，我运行一段时间后，效果如下：

  ![image.png](https://upload-images.jianshu.io/upload_images/15391438-993a684fdc7ba04f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

程序会一直运行下去，直到手动停止，或者代理池为空。

我们打开redis可视化工具：

![代理](https://upload-images.jianshu.io/upload_images/15391438-1ba478823b79faa6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

一共有2500条数据，可用代理有500左右的代理分数为100，：

![结果](https://upload-images.jianshu.io/upload_images/15391438-bc43bb5f80941394.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

效果挺满意，我们打开浏览器，访问127.0.0.1:5000

![image.png](https://upload-images.jianshu.io/upload_images/15391438-4d3e7e7fdf009e3f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/15391438-86ebbad4ba3b57e6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

每次刷新这个页面都可以得到一个新的代理。

![今天](https://upload-images.jianshu.io/upload_images/15391438-2e51bb3ec3bb9939.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

刚又运行了下，又多了不少个，真好。这下不愁没代理了。不过我是拿的百度首页做测试的，用的时候还要将测试对象改成爬取的网站。

刚才拿到了华章电子书vip卡，可以用一个月，但是只能在微信里看，我看看能不能给整下来，慢慢看。

真好。

-----
####最后一天


