# encoding=utf-8

# 使用Proxy：第二步，增加middleware.py及相关方法

# 导入base64，用于需要认证的代理
import base64
import random
from settings import PROXIES
from scrapy import log

class ProxyMiddleware(object):
    # 覆盖process_request方法
    def process_request(self, request, spider):
        # 随机在列表中选择一个代理
        proxy = random.choice(PROXIES)
        '''
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        else:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
        '''
        request.meta['proxy'] = "http://%s" % proxy