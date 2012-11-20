#coding=utf-8
#from proxy import get_proxy_list

#线程数
THREAD_NUM = 10

#重试次数
RETRY_NUM = 3

#超时，以秒计算
TIME_OUT = 60

#线程最大延时，以秒计算
SLEEP_TIME_SEED = 5

#内存栈大小，32768的倍数，建议两倍以上
STACK_SIZE = 32768 * 16

#是否支持gzip抓取
USE_GZIP = False

#是否缓存DNS查询结果，如果是，则将域名第一次查询到的ip置换掉请求网址的相应部分
CACHE_DNS = True

#是否要加入请求信息头
USE_HEADER = True
HEADERS = [
    ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'),
    ('Connection', 'Keep-Alive'),
    ('Cache-Control', 'no-cache'),
    ('Content-Type', 'text/xml'),
    ('X-Forwarded-For', '192.168.0.1'),  #预防对方网站透过代理得到本机IP
]

#是否使用cookie
USE_COOKIE = True
COOKIE_FILE_PATH = ''

#是否使用代理
USE_PROXY = True
PROXY_LIST = []
if USE_PROXY:
    try:
        pass
        #PROXY_LIST = get_proxy_list()  #从代理数据库中获取列表 [(proxy_type, host, port, user, password),...]
    except Exception, error_msg:
        print u'获取代理列表失败'

#是否需要事先登录
NEED_LOGIN = False
LOGIN_URL = ''
LOGIN_FORM_DATA = {
    'username': '',
    'password': '',
}
LOGIN_SUCCEED_STR = ''

#日志文件
LOG_FILE = 'running.log'
