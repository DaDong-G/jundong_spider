from spider_plus.https.request import Request
from .scheduler import Scheduler
from .downloader import Downloader
from .pipline import Pipeline
from .spider import Spider
import time
from datetime import datetime

from spider_plus.middlewares.spider_middlewares import SpiderMiddleware
from spider_plus.middlewares.downloader_middlewares import DownloaderMiddleware


class Engine(object):
    def __init__(self, spider):
        # self.spider = Spider()
        self.spider = spider
        self.downloader = Downloader()
        self.pipeline = Pipeline()
        self.scheduler = Scheduler()

        self.spider_mid = SpiderMiddleware()
        self.downloader_mid = DownloaderMiddleware()
        self.total_request_nums = 0
        self.total_response_nums = 0

    def start(self):
        """启动整个引擎"""
        print('爬虫启动')
        start_time = datetime.now()
        self._start_engine()
        end_time = datetime.now()
        print('爬虫结束---耗时--{}'.format(end_time - start_time))

    def _start_engine(self):
        for start_request in self.spider.start_requests():
            # 1. 对start_request进过爬虫中间件进行处理
            #  添加spider_mid request 中间件
            start_request = self.spider_mid.process_request(start_request)

            # 2 把初始化请求添加给调度器
            self.scheduler.add_request(start_request)

            self.total_response_nums += 1

    def _execute_request_response_item(self):
        # 3 从调度器获取请求对象，交给下载器发起请求，获取一个响应对象
        request = self.scheduler.get_request()
        if request is None:
            return
        # 添加 downloader_mid  request 中间件
        request = self.downloader_mid.process_request(request)

        # 4 从调度器获取一个请求对象，交给下载器,发送请求，
        response = self.downloader.get_response(request)

        # 添加 downloader_response 中间件
        response = self.downloader_mid.process_response(response)
        #  添加 spider_response 中间件
        response = self.spider_mid.process_response(response)

        # 5  解析请求
        for result in self.spider.parse(response):
            # 6 判断结果
            # 6.1 如果是请求对象，就就给 调度器
            if isinstance(result, Request):
                result = self.spider_mid.process_response(result)
                self.scheduler.add_request(result)

            # 6.2 如果是数据就丢给 管道处理
            else:
                self.pipeline.process_item(result)



