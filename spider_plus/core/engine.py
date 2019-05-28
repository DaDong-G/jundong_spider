from spider_plus.https.request import Request
from .scheduler import Scheduler
from .downloader import Downloader
from .pipline import Pipeline
from .spider import Spider

from spider_plus.middlewares.spider_middlewares import SpiderMiddleware
from spider_plus.middlewares.downloader_middlewares import DownloaderMiddleware


class Engine(object):
    def __init__(self):
        self.spider = Spider()
        self.downloader = Downloader()
        self.pipeline = Pipeline()
        self.scheduler = Scheduler()

        self.spider_mid = SpiderMiddleware()
        self.downloader_mid = DownloaderMiddleware()

    def start(self):
        """启动整个引擎"""
        self._start_engine()

    def _start_engine(self):
        # 1 构造url
        start_request = self.spider.start_requests()

        #  添加spider_mid request 中间件
        start_request = self.spider_mid.process_request(start_request)

        # 2 把初始化请求添加给调度器
        self.scheduler.add_request(start_request)

        # 3 从调度器获取请求对象，交给下载器发起请求，获取一个响应对象
        request = self.scheduler.get_request()

        # 添加 downloader_mid  request 中间件
        request =self.downloader_mid.process_request(request)

        # 4 从调度器获取一个请求对象，交给下载器，
        response = self.downloader.get_response(request)

        # 添加 downloader_response 中间件
        response = self.downloader_mid.process_response(response)

        # 5  解析请求
        result = self.spider.parse(response)

        # 6 判断结果
        # 6.1 如果是请求对象，就就给 调度器
        if isinstance(result, Request):
            result = self.spider_mid.process_response(result)
            self.scheduler.add_request(result)

        # 6.2 如果是数据就丢给 管道处理
        else:
            self.pipeline.process_item(result)
