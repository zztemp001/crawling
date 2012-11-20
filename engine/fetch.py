#coding=utf-8

import time, random
import base64
import urllib, urllib2, cookielib
from threading import Thread, Lock
from Queue import Queue
import zlib
from gzip import GzipFile
from StringIO import StringIO
from config import *

class ContentEncodingProcessor(urllib2.BaseHandler):
    """ A handler to add gzip capabilities to urllib2 requests
    """
    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip, deflate")
        return req

    def http_response(self, req, resp):
        old_resp = resp
        # gzip
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(
                fileobj=StringIO(resp.read()),
                mode="r"
            )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        # deflate
        if resp.headers.get("content-encoding") == "deflate":
            gz = StringIO(self.deflate(resp.read()) )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        return resp

    def deflate(self, data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)


class Fetcher:
    def __init__(self, threads, data=None):
        self.lock = Lock() #线程锁
        self.q_request = Queue() #任务队列
        self.q_response = Queue() #完成队列
        self.data = data  #需要提交的数据，如果有
        self.threads = threads  #线程池的大小

        #创建opener，如果需要登录，也需要设置cookie
        if USE_COOKIE or NEED_LOGIN:
            cj = cookielib.CookieJar()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler)
        else:
            self.opener = urllib2.build_opener(urllib2.HTTPHandler)

        #如果需要使用proxy，第一步先生成一个handler
        if USE_PROXY:
            proxy_support = urllib2.ProxyHandler()
            self.opener.add_handler(proxy_support)

        #如果需要gzip支持
        if USE_GZIP:
            gzip_support = ContentEncodingProcessor
            self.opener.add_handler(gzip_support)

        #安装这个opener
        urllib2.install_opener(opener=self.opener)

        #如果需要登录，则先登录
        if NEED_LOGIN and LOGIN_URL and LOGIN_FORM_DATA:
            if not self.handle_login():
                return False  #如果登录不成功，则直接退出

        #生成线程池
        for i in range(threads):
            t = Thread(target = self.threaded_fetch)
            t.setDaemon(True)
            t.start()

        #线程开始运行设为1，结束设为0
        self.running = 0

    def __del__(self): #解构时需等待两个队列完成
        time.sleep(0.5)
        self.q_request.join()
        self.q_response.join()

    def is_running(self):
        #只要请求序列、返回数据列、线程尚在运行，都可以从返回数据列中pop出数据
        return self.q_request.qsize() + self.q_response.qsize() + self.running

    def push(self, url):
        self.q_request.put(url)

    def pop(self):
        return self.q_response.get()

    def threaded_fetch(self):
        while True:
            url = self.q_request.get()
            with self.lock: #线程开始运行设为1
                self.running += 1
                response = self.handle_request(url, self.data, RETRY_NUM)

            self.q_response.put((url, response))
            with self.lock:
                self.running -= 1
            self.q_request.task_done()
            time.sleep(round(random.random() + 0.01, 2) * SLEEP_TIME_SEED)
        return

    #如果需要提前登录
    def handle_login(self, retries=3):
        login_data = urllib.urlencode(LOGIN_FORM_DATA)
        #检测是否能正常访问
        try:
            response = urllib2.urlopen(url=LOGIN_URL, data=login_data , timeout=TIME_OUT).read()
        except Exception, error_msg:
            if retries > 0:
                self.handle_login(retries-1)
            else:
                print 'login failed'
                return False
        #如果登录不成功，则重试
        if LOGIN_SUCCEED_STR not in response:
            self.handle_login(retries-1)
        return True

    #全能request处理
    def handle_request(self, url, data=None, retries=3):
        request = urllib2.Request(url)

        #如果有需要提交的数据
        if type(data) is dict:
            request.add_data(urllib.urlencode(data))   #Request会自动将请求方式转为POST

        #如果需要用headers
        if USE_HEADER and HEADERS:
            for key, value in HEADERS:
                request.add_header(key, value)
            #根据请求的url生成相应的Referer头
            request.add_header('Referer', url.split('/')[2])
            #随机生成X-forward-for头
            request.add_header('X-Forwarded-For', str(random.randint(1, 255)) + '.87.' + str(random.randint(1, 255)) + '.34')

        #如果需要使用代理
        if USE_PROXY and PROXY_LIST:
            proxy_type, host, port, user, password = random.choice(PROXY_LIST)
            if proxy_type is None:
                proxy_type = "http"
            if user and password:  #如果用户名/密码不为空，则需要认证
                user_pass = "%s:%s" % (urllib2.unquote(user), urllib2.unquote(password))
                creds = base64.b64encode(user_pass).strip()
                request.add_header("Proxy-authorization", "Basic " + creds)
            host_port = urllib2.unquote(host + ":" + port)
            request.set_proxy(host_port, proxy_type)

        response = ''
        try:
            print request.get_data()
            print request.get_full_url()
            print request.headers
            print request.get_host()
            print request.get_method()
            print request.get_origin_req_host()
            print request.get_selector()

            response = urllib2.urlopen(request, timeout=TIME_OUT)
            print response.getcode()
            print response.geturl()
            print response.info()
            response =response.read()
        except Exception, error_msg:
            print Exception, error_msg
            if retries > 0:
                self.handle_request(url, data, retries-1)
            else:
                print 'Request Failed: ', url
        return response

    #todo: 状态监控，logging
    #todo: 暂停、恢复
    #todo: 处理返回的信息

if __name__ == "__main__":
    urls = ['http://www.verycd.com/topics/%d/' % i for i in range(5420, 5425)]
    f = Fetcher(threads=10)
    for url in urls:
        f.push(url)
    while f.is_running():
        url, content = f.pop()
        print url, len(content)
    print 'main is ok'