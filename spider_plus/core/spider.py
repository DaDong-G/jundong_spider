from spider_plus.item import Item
from spider_plus.https.request import Request


class Spider(object):
    """
    1. 构建请求信息(初始的)，也就是生成请求对象(Request)
    2. 解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
    """

    start_urls = []

    def start_requests(self):
        """构建初始请求对象并返回"""
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        """解析请求并返回新的请求对象、或者数据对象"""
        yield Item(response.body)  # 返回item对象
