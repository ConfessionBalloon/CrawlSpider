# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json

import requests
from scrapy import signals
import random
from boss_demo.models import ProxyModel
from twisted.internet.defer import DeferredLock

class UserAgentDownloadMiddlewares(object):
    USERAGENT = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; SV1; Crazy Browser 9.0.04)",
        "Cyberdog/2.0 (Macintosh; PPC)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; Deepnet Explorer 1.5.3; Smart 2x2; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; pl-pl) AppleWebKit/312.8 (KHTML, like Gecko, Safari) DeskBrowse/1.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) Gecko/20070404 K-Ninja/2.1.3",
        "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16"
    ]
    def process_request(self, request, spider):
        useragent = random.choice(self.USERAGENT)
        request.headers['User-Agent'] = useragent

class IPProxyDownloadMiddlewares(object):

    PROXY_URL = "http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=11&pack=33075&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions="

    def __init__(self):
        super(IPProxyDownloadMiddlewares, self).__init__()
        self.current_proxy = None
        self.Lock = DeferredLock()

    def process_request(self, request, spider):
        if 'proxy' not in request.meta or self.current_proxy.is_expiring:
            self.update_proxy()

        request.meta['proxy'] = self.current_proxy.proxy

    def process_response(self, request, response, spider):
        if response.status != 200 or 'captcha' in response.url:
            if not self.current_proxy.blacked:
                self.current_proxy.blacked = True
            print('%s这个代理被加入黑名单了' % self.current_proxy.ip)
            self.update_proxy()
            return request
        return response

    def update_proxy(self):
        self.Lock.acquire()
        if not self.current_proxy or self.current_proxy.is_expiring or self.current_proxy.blacked:
            response = requests.get(self.PROXY_URL)
            text = response.text
            print('重新获取了一个代理：',text)
            result = json.loads(text)
            if len(result['data']) > 0:
                data = result['data'][0]
                proxy_model = ProxyModel(data)
                self.current_proxy = proxy_model
        self.Lock.release()