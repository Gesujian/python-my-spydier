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
                                       timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应不合法', proxy)
            except (TimeoutError, AttributeError, ClientError,
                    ClientConnectorError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

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
