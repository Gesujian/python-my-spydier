import time
from api import app
from getter import Getter
from tester import Tester
from multiprocessing import Process
from multiprocessing import Pool

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