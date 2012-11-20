# coding=utf-8

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from scrapy import log

class ProxySpider(CrawlSpider):
    name = "proxy"
    domain_name = "myip.cn"
    # The following url is subject to change, you can get the last updated one from here :
    # http://www.whatismyip.com/faq/automation.asp
    start_urls = ["http://www.myip.cn"]

    def parse(self, response):
        """
        @param response 中文注释
        """
        self.log('Proxy: %s' % response.meta['proxy'])
        self.log('Request Status: %s' % str(response.status))
        self.log('Request Time: %s' % response.meta['download_latency'])
        hxs = HtmlXPathSelector(response)
        ip = hxs.select('//font[contains(@color, "#0066CC")]/b/text()').extract()[0]
        open('test.html', 'wb').write(ip.encode("utf-8"))
        self.log(ip.encode("utf-8"))
