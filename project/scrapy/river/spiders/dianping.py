# coding=utf-8

import pickle
import time
import sqlite3
from os import path
from time import time

from scrapy.spider import BaseSpider
from scrapy.http import Request, Response
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item
from scrapy import log

class DianpingSpider(CrawlSpider):
    ''' 大众点评网数据抓取
    1、获取所有市级以上的首页网址：
    2、在城市首页网址中进入分类页面：
    3、根据分类页面的商户类型二级子类别+行政区二级子类别，生成列表页首页网址。如（福田区）车公庙片区+（美食）粤菜
        列表页首页网址格式为：
    4、根据列表页首页网址，爬行所有列表页面，得到所有商铺的名称、网址、所在城市、区域、商圈，所在的分类、子分类
    5、根据商铺地址，开展详细数据的抓取，以及后期的数据更新
    6、可以通过每个分类的“rss订阅”来监控新商户的添加
    '''
    name = 'dianping'
    allowed_domain = ['www.dianping.com', '127.0.0.1']
    start_urls = ['http://127.0.0.1/static/page/dianping.htm']
    base_url = 'http://www.dianping.com'

    def parse(self, response):
        ''' 从城市列表页中得到城市首页网址，并将其送入请求序列
        1、城市分热门和非热门，热门城市用粗体表示
        2、parse函数是spider类缺省用于处理start_urls的方法
        '''
        print u'正在 %s 中获取城市列表及其网址' % response.url

        hxs = HtmlXPathSelector(response)
        cities = hxs.select('//*[@id="divPY"]/li/div/a')
        for city in cities[:5]:  # 使用前面5条记录测试
            if city.select('strong'):
                city_name = city.select('strong/text()').extract()[0]
                hot = 1
            else:
                city_name = city.select('text()').extract()[0]
                hot = 0
            city_url = city.select('@href').extract()[0]
            print str(hot) + "  " + city_name + "  " + city_url
            # 以下示范如何生成Request，以及如何使用Request.meta来在不同的页面间传递附加变量
            request = Request(self.base_url + city_url, callback=self.parse_city_home_url,)
            request.meta['city'] = city_name
            request.meta['hot'] = hot
            yield request

    def parse_city_home_url(self, response):
        ''' 获取城市分类首页地址，重点城市与一般城市有所区别
        城市总体分类页格式：/shopall/(城市编号)/0
        '''
        print u'进入 %s 中' % response.url
        city_home_url = ''
        hxs = HtmlXPathSelector(response)
        if response.meta['hot']:
            # 重点城市直接得到首页地址(/shopall/342/0)
            city_home_url = hxs.select('//*[@id="top"]/div[3]/div[1]/div/div[2]/div/a/@href').extract()[0]
        else:
            # 非重点城市通过获取美食栏目地址(/search/category/255/10)，得到该城市的编号，然后硬编码首页地址
            temp_url = hxs.select('//*[@id="top"]/div[3]/div[2]/div/ul[1]/li/ul/li[2]/ul/li[1]/a/@href').extract()[0]
            city_no = temp_url.split('/')[-2]
            city_home_url = u'/shopall/%s/0' % city_no
        print response.meta['city'] + u'首页网址：' + self.base_url + city_home_url
        return Item()

    def parse_hot_city_list_url(self, response):
        ''' 通过城市总体分类页，获取分类列表的首页地址
        重点城市（类别的二级分类×区域的二级分类，如[福田区]车公庙片区+[美食]粤菜）：http://www.dianping.com/search/category/7/10/g407r1951o10p1
        非重点城市（类别的一级分类×区域的一级分类，如邯山区+美食）：
        注意要使用o参数进行排序，确保质量好的商铺排在前面，o10为“按点评数”排序，确保有人气
        注意可能存在没有数据的组合，网站会提示“没有找到满足条件的商户。”
        '''
        pass
