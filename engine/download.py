#coding=utf-8

import random
import socket
import urllib, urllib2, cookielib

from time import sleep

from proxy import get_proxy_list

#网页下载函数返回result，包含网页内容，服务器代码，错误列表
#如果网页下载失败，统一返回一个False
result = {}
result['content'] = u''
result['code'] = 200
result['error'] = []

#设置连接超时为30秒
socket.socket.settimeout(30)

def get_page_basic(url=''):
    ''' 基本的网页抓取函数
    '''
    try:
        result['content'] = urllib2.urlopen(url).read()
    except:
        return False
    return result

def get_page(link='', post_data=None, use_headers=True, use_cookie=True, use_proxy=False):
    #初始化下载器，如果使用cookie，则做相应处理
    if use_cookie:
        cj = cookielib.CookieJar()
        # cj.load('cookie.txt')  #是否可以在这里加入一整个cookie的内容？
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler)
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)

    #使用这个下载器
    urllib2.install_opener(opener)

    #初始化一个新请求
    request = urllib2.Request(url = link)

    #使用请求网址的host部分
    if use_headers:
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;) Firefox/3'),
        request.add_header('Referer', link.split('/')[2]),
        request.add_header('X-Forwarded-For', '192.168.0.1')
        #todo: 如果需要提交二进制数据时，还要设置内容类型

    #如果有要提交的数据
    if post_data:
        post_data = urllib.urlencode(post_data)
        request.add_data(post_data)

    #如果需要通过代理访问
    if use_proxy:
        try:
            proxies = get_proxy_list()
            if proxies:
                proxy = random.choice(proxies)
                request.set_proxy(proxy['host'], proxy['type'])
        except:
            pass

    #设置返回的结果
    content = urllib2.urlopen(request).info()

    result['content'] = content

    #随机休眠一段时间
    sleep(random.randint(1,5))

    return result

if __name__ == "__main__":
    link = 'http://www.google.com'
    result = get_page(link)
    print result['content']
    print type(result['content'])