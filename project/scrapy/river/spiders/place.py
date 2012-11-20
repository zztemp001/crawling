# coding=utf-8

import sqlite3

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item
from scrapy import log

class WorldPlaceSpider(BaseSpider):
    ''' 抓取大洲/洲片区/国家
    目标网址：http://baike.baidu.com/view/4262975.htm
    '''
    name = 'worldplace'
    allowed_domains = ['localhost', '127.0.0.1']
    start_urls = ['http://127.0.0.1/static/page/4262975.htm',]
    filename = 'river\\data\\basic.sqlite'

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        self.conn = sqlite3.connect(self.filename)
        self.conn.text_factory = 'utf-8'

        # 获取大洲名称列表
        continents = []
        cs = hxs.select('//*[@id="lemmaContent-0"]/h2')[2:]  # 有用的数据从第3条开始，依次为非洲、美洲、亚洲、欧洲、大洋洲
        for c in cs:
            continents.append(c.select('span[2]/text()').extract()[0])

        # 获取并处理洲片区和国家数据
        # 主要的数据在以下表格中，有用的数据为2～6，依次为非洲、美洲、亚洲、欧洲、大洋洲
        data = hxs.select('//*[@id="lemmaContent-0"]/table')[1:]
        rows = data.select('tr')
        for row in rows:
            # 获取洲片区信息并存入数据库
            if len(row.select('td[1]/a/text()').extract()) > 0:
                semi_continent = row.select('td[1]/a/text()').extract()[0]
                url = row.select('td[1]/a/@href').extract()[0]
            else:
                semi_continent = row.select('td[1]/text()').extract()[0]
                url = ''
            print semi_continent + "  " + url
            log.msg(semi_continent + "  " + url)
            # self.conn.execute('insert into semi_continent (title, level, url) values (?,?,?)', (semi_continent, 2, url))

            # 获取国家信息并存入数据库，一些信息有错、漏，需要手动调整
            cs = row.select('td[2]/a')
            for c in cs:
                country = c.select('text()').extract()[0]  # 国家名称
                url = c.select('@href').extract()[0]  # 国家所引用的url
                print "  " + country + "  " + url
                # self.conn.execute('insert into country (title, level, parent_title, url) values (?,?,?,?)', (country, 3, semi_continent, url))

        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

        return Item()

class NativePlaceSpider(BaseSpider):
    ''' 抓取国内省、市、县（区）、街道信息
    目标网址：http://www.stats.gov.cn/tjbz/cxfldm/2011/index.html
    '''
    name = 'nativeplace'
    allowed_domains = ['www.stats.gov.cn']
    start_urls = ['http://www.stats.gov.cn/tjbz/cxfldm/2011/index.html']
    base_url = 'http://www.stats.gov.cn/tjbz/cxfldm/2011/'  # 用于生成完整的请求地址
    database = 'river\\data\\basic.sqlite'  # 用于存储数据的数据库

    def parse(self, response):
        ''' 分析起始页，也就是“省”列表
        xpath: //tr[contains(@class, "provincetr")]/td/a
        '''
        self.conn = sqlite3.connect(self.database)
        self.conn.text_factory = 'utf-8'  # 链接数据库并设置utf-8编码

        hxs = HtmlXPathSelector(response)
        provinces = hxs.select('//tr[contains(@class, "provincetr")]/td/a')
        for p in provinces:
            province_name = p.select('text()').extract()[0]
            province_url = self.base_url + p.select('@href').extract()[0]
            print province_name + "  5  " + province_url
            # self.conn.execute('insert into province (title, level) values (?,?)', (province_name, 5))
            request = Request(province_url, callback=self.parse_city)
            request.meta['province'] = province_name
            yield request

        # 提交并关闭数据库连接
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def parse_city(self, response):
        ''' 分析城市列表，如：广州、深圳
        xpath: //tr[contains(@class, "citytr")]
        '''
        self.conn = sqlite3.connect(self.database)
        self.conn.text_factory = 'utf-8'  # 链接数据库并设置utf-8编码

        hxs = HtmlXPathSelector(response)
        cities = hxs.select('//tr[contains(@class, "citytr")]')
        for c in cities:
            if c.select('td[2]/a') and c.select('td[1]/a'):
                city_name = c.select('td[2]/a/text()').extract()[0]
                city_url = self.base_url + c.select('td[2]/a/@href').extract()[0]
                city_no = c.select('td[1]/a/text()').extract()[0]
                print response.meta['province'] + "  " + city_name + "  " + city_no + "  " + city_url
                # self.conn.execute('insert into city (title, level, parent_title, stat_code) values (?,?,?,?)', (city_name, 6, response.meta['province'], city_no))
                request = Request(city_url, callback=self.parse_county)
                request.meta['province'] = response.meta['province']
                request.meta['city'] = city_name
                yield request

        # 提交并关闭数据库连接
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def parse_county(self, response):
        ''' 分析城区/县，如罗湖、福田、从化
        xpath: //tr[contains(@class, "countytr")]
        注意有“市辖区”无链接的情形，如深圳市的城区列表页 http://www.stats.gov.cn/tjbz/cxfldm/2011/44/4403.html
        '''
        self.conn = sqlite3.connect(self.database)
        self.conn.text_factory = 'utf-8'  # 链接数据库并设置utf-8编码

        url_fix = response.url.split('/')[-2]  # 经分析，系统生成这一级url需要补上所在省的编号

        hxs = HtmlXPathSelector(response)
        counties = hxs.select('//tr[contains(@class, "countytr")]')
        for county in counties:
            if county.select('td[2]/a') and county.select('td[1]/a'):
                county_name = county.select('td[2]/a/text()').extract()[0]
                county_url = self.base_url + url_fix + "/" + county.select('td[2]/a/@href').extract()[0]
                county_no = county.select('td[1]/a/text()').extract()[0]
                print response.meta['province'] + "  " + response.meta['city'] + "  " + county_name + "  " + county_no + "  " + county_url
                # self.conn.execute('insert into county (title, level, parent_title, parent_parent_title, stat_code) values (?,?,?,?,?)', (county_name, 7, response.meta['city'], response.meta['province'], county_no))
                request = Request(county_url, callback=self.parse_town)
                request.meta['province'] = response.meta['province']
                request.meta['city'] = response.meta['city']
                request.meta['county'] = county_name
                yield request

        # 提交并关闭数据库连接
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def parse_town(self, response):
        ''' 分析街道/镇，如香蜜湖、斗山镇
        xpath: //tr[contains(@class, "towntr")]
        '''
        self.conn = sqlite3.connect(self.database)
        self.conn.text_factory = 'utf-8'  # 链接数据库并设置utf-8编码

        hxs = HtmlXPathSelector(response)
        towns = hxs.select('//tr[contains(@class, "towntr")]')
        for t in towns:
            if t.select('td[2]/a') and t.select('td[1]/a'):
                town_name = t.select('td[2]/a/text()').extract()[0]
                town_url = t.select('td[2]/a/@href').extract()[0]
                town_no = t.select('td[1]/a/text()').extract()[0]
                print response.meta['province'] + "  " + response.meta['city'] + "  " + response.meta['county'] + "  " + town_name + "  " + town_no + "  " + self.base_url + town_url
                self.conn.execute('insert into town (title, level, parent_title, parent_parent_title, stat_code) values (?,?,?,?,?)', (town_name, 8, response.meta['county'], response.meta['city'], town_no))

        # 提交并关闭数据库连接
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

