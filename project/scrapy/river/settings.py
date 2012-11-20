# encoding=utf-8
import os

ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR, 'river/crawled_data').replace('\\', '/')  #存放数据的主目录

USER_AGENT = 'chrome/21.0'

ROBOTSTXT_OBEY = False  # 是否遵守网站的robots.txt文件规则
DNSCACHE_ENABLED = True  # 开启DNS缓存

DOWNLOAD_DELAY = 1.25  # 下载间隔时间，以秒为单位，如果此项设置为0，则不会有任何间隔
RANDOMIZE_DOWNLOAD_DELAY = True  # 与DOWNLOAD_DELAY共同作用，实际值为DOWNLOAD_DELAY*(0.5~1.5)
DOWNLOAD_TIMEOUT = 180  # 下载超时设定，以秒为单位

CONCURRENT_ITEMS = 100  # 使用pipeline同时处理的item数量
CONCURRENT_REQUESTS = 16  # 最大下载线程数
CONCURRENT_REQUESTS_PER_DOMAIN = 8  # 针对单一域名启动的线程数
CONCURRENT_REQUESTS_PER_IP = 0  # 针对单一IP启动的线程数，如果为0，则使用域名数，如果非0，则覆盖域名设置

SPIDER_MODULES = ['river.spiders']
NEWSPIDER_MODULE = 'river.spiders'

# 缺省的Http请求头信息
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    # 'river.middlewares.ProxyMiddleware': 100,
}

ITEM_PIPELINES = [
    # 'river.pipelines.DBPipeline',
]

# log服务设置
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = os.path.join(ROOT_DIR, 'river/log/local.log').replace('\\', '/')  #日志文件
LOG_LEVEL = 'DEBUG'
LOG_STDOUT = False  #是否将屏幕显示的信息一并log进文件，缺省为False。如果为True，则屏幕不再显示信息

BAIDU_GUONEI_JINGDIAN_URLS = [
    'http://lvyou.baidu.com/scene/ajax/allview/17070a5c91ca872746461bf4?format=ajax&cid=0&pn=1&t=',  #云南
    'http://lvyou.baidu.com/scene/ajax/allview/289d2b074d001b3184b27ef7?format=ajax&cid=0&pn=1&t=',  #上海
    'http://lvyou.baidu.com/scene/ajax/allview/795ac511463263cf7ae3def3?format=ajax&cid=0&pn=1&t=',  #北京
    'http://lvyou.baidu.com/scene/ajax/allview/cc11463263cf7ae3b9d4dff3?format=ajax&cid=0&pn=1&t=',  #天津
    'http://lvyou.baidu.com/scene/ajax/allview/1fdbf740851f3e07d8d23ff7?format=ajax&cid=0&pn=1&t=',  #重庆
    'http://lvyou.baidu.com/scene/ajax/allview/79c0adc41efa15d8330ab4f5?format=ajax&cid=0&pn=1&t=',  #香港
    'http://lvyou.baidu.com/scene/ajax/allview/c19909736a7351eeeb69a4f5?format=ajax&cid=0&pn=1&t=',  #澳门
    'http://lvyou.baidu.com/scene/ajax/allview/9cf3f47a261257ae7e7e5df5?format=ajax&cid=0&pn=1&t=',  #台湾
    'http://lvyou.baidu.com/scene/ajax/allview/4810309ea171641493d817f6?format=ajax&cid=0&pn=1&t=',  #山东
    'http://lvyou.baidu.com/scene/ajax/allview/3a89363b4ffbffdcdfcc98f4?format=ajax&cid=0&pn=1&t=',  #江苏
    'http://lvyou.baidu.com/scene/ajax/allview/8e8da744ec5be32fd14c6cf7?format=ajax&cid=0&pn=1&t=',  #四川
    'http://lvyou.baidu.com/scene/ajax/allview/2f1a4dadc1b446649c1ec9f3?format=ajax&cid=0&pn=1&t=',  #湖南
    'http://lvyou.baidu.com/scene/ajax/allview/68cf7ae3b9d414ff762fddf3?format=ajax&cid=0&pn=1&t=',  #山西
    'http://lvyou.baidu.com/scene/ajax/allview/1fb09a056d0754c85f197bf5?format=ajax&cid=0&pn=1&t=',  #陕西
    'http://lvyou.baidu.com/scene/ajax/allview/75285f52dec9c3f9db7dfef3?format=ajax&cid=0&pn=1&t=',  #河南
    'http://lvyou.baidu.com/scene/ajax/allview/9520608cbb0e13551b12a1f1?format=ajax&cid=0&pn=1&t=',  #浙江
    'http://lvyou.baidu.com/scene/ajax/allview/b0240abb6cf9c05f301acdf3?format=ajax&cid=0&pn=1&t=',  #广东
    'http://lvyou.baidu.com/scene/ajax/allview/9607cc8575ed2e69961327f7?format=ajax&cid=0&pn=1&t=',  #湖北
    'http://lvyou.baidu.com/scene/ajax/allview/fb0af2c9c005c401f11576f3?format=ajax&cid=0&pn=1&t=',  #安徽
    'http://lvyou.baidu.com/scene/ajax/allview/052c5d285f52dec9c3f9f1f1?format=ajax&cid=0&pn=1&t=',  #辽宁
    'http://lvyou.baidu.com/scene/ajax/allview/55163f0fd41f9757809972f0?format=ajax&cid=0&pn=1&t=',  #福建
    'http://lvyou.baidu.com/scene/ajax/allview/4c3263cf7ae3b9d414ffdcf3?format=ajax&cid=0&pn=1&t=',  #河北
    'http://lvyou.baidu.com/scene/ajax/allview/5ec98727464640351f1219f0?format=ajax&cid=0&pn=1&t=',  #吉林
    'http://lvyou.baidu.com/scene/ajax/allview/6275641493d83c0c3f1515f7?format=ajax&cid=0&pn=1&t=',  #黑龙江
    'http://lvyou.baidu.com/scene/ajax/allview/c9b8ae5f1d3a784045d69ef1?format=ajax&cid=0&pn=1&t=',  #江西  **
    'http://lvyou.baidu.com/scene/ajax/allview/64649c1ed1b18b0036d9f4f3?format=ajax&cid=0&pn=1&t=',  #甘肃
    'http://lvyou.baidu.com/scene/ajax/allview/c2fa4653ba3ece0ae6bc95f3?format=ajax&cid=0&pn=1&t=',  #贵州
    'http://lvyou.baidu.com/scene/ajax/allview/7425aa3f6703cc8575ed39f0?format=ajax&cid=0&pn=1&t=',  #海南
    'http://lvyou.baidu.com/scene/ajax/allview/7423aa3f6703cc8575ed39f6?format=ajax&cid=0&pn=1&t=',  #青海
    'http://lvyou.baidu.com/scene/ajax/allview/295291f256c0a53ec6ad8cf7?format=ajax&cid=0&pn=1&t=',  #新疆
    'http://lvyou.baidu.com/scene/ajax/allview/f61b7498603a75a3a4c7c5f0?format=ajax&cid=0&pn=1&t=',  #西藏
    'http://lvyou.baidu.com/scene/ajax/allview/de5f301a4dadc1b44664c8f3?format=ajax&cid=0&pn=1&t=',  #广西
    'http://lvyou.baidu.com/scene/ajax/allview/f6187498603a75a3a4c7c5f3?format=ajax&cid=0&pn=1&t=',  #内蒙古
    'http://lvyou.baidu.com/scene/ajax/allview/dc65d60419efc717ac2d0af0?format=ajax&cid=0&pn=1&t=',  #宁夏
]