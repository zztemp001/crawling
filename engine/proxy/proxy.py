#coding=utf-8

import re
import sqlite3
import urllib, urllib2
import time
import socket
import threading
from Queue import Queue
from zzlib.common.system import Logger

from libxml2 import htmlParseDoc as htmlParser

class VerifyProxy():
    def __init__(self, pool_size=15):
        socket.setdefaulttimeout(20)  #设置代理检验的超时时长
        self.conn = sqlite3.connect('proxy.db', check_same_thread=False)
        self.logger = Logger('proxy.log')  #用于保存log信息的文件

        self.pool_size = pool_size
        self.lock = threading.Lock()
        self.raw_queue = Queue()

    def verify_proxy(self):
        self.logger.p_log('开始检验代理...')

        #从数据库中获取需要检验的代理列表
        try:
            proxies = self.conn.execute('select distinct host, port from proxy').fetchall()
            self.logger.p_log('从数据库中获取到不重复的代理共 %d 个，准备逐个校验中' % len(proxies))
            proxies = proxies[20:30]
        except Exception, e:
            self.logger.p_log('读取代理数据库错误，退出...')
            return False

        #生成线程池，大小为pool_size，缺省为10
        for i in range(self.pool_size):
            thread = threading.Thread(target=self.__verify_proxy)
            thread.setDaemon(True)
            thread.start()

        #将获取到的待检验的代理放入序列proxy_queue中
        for host, port in proxies:
            self.raw_queue.put({'host': str(host), 'port': str(port)})
        #将队列加入线程池，程序开始，直至队列为空
        self.raw_queue.join()
        self.__del__()

    def __verify_proxy(self):
        #检验代理，成功的保存在verified_queue中
        while True:
            proxy = self.raw_queue.get()
            start_time = time.time()
            ip_there = self.__get_ip_from_myip_cn(proxy['host'], proxy['port'])
            #ip_there = self.__get_ip_from_dyndns_org(proxy['host'], proxy['port'])
            with self.lock:
                time_used = time.time() - start_time + 1
                if ip_there:
                    try:
                        self.conn.execute('update proxy set speed=? where host=? and port=?', (time_used, proxy['host'], proxy['port']))
                        self.conn.commit()
                        self.logger.p_log('代理 %s:%s [%d 秒] 校验成功，并已成功入库' % (proxy['host'], proxy['port'], time_used))
                    except Exception, e:
                        self.logger.p_log('代理 %s:%s [%d 秒] 校验成功，但在数据库更新状态时发生异常' % (proxy['host'], proxy['port'], time_used))
                        self.logger.p_log(e)
                else:
                    self.logger.p_log('代理 %s:%s [%d 秒] 校验失败' % (proxy['host'], proxy['port'], time_used))
            self.raw_queue.task_done()
            time.sleep(1)
        return

    def __del__(self):
        #删除校验不成功的数据
        try:
            self.conn.execute('delete from proxy where speed is null')
            self.logger.p_log('未通过校验的代理已从数据库中删除')
        except Exception, e:
            self.logger.p_log('从数据库中删除未通过校验的代理时发生错误')

        #关闭数据库
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None
        return


    def __get_ip_from_dyndns_org(self, host=None, port=None):
        if not host or not port: return False
        url = 'http://checkip.dyndns.org/'
        proxy = {'http': 'http://' + host + ':' + port}
        try:
            content = urllib.urlopen(url, proxies=proxy).read()
            if content:
                ip_there = content.split(': ')[1].split('</body>')[0]
                return ip_there
        except Exception, e:
            return False

    def __get_ip_from_myip_cn(self, host=None, port=None):
        if not host or not port: return False
        url = 'http://www.myip.cn'
        xpath = '/html/body/center/div[4]/font[1]/b'
        proxy = {'http': 'http://' + host + ':' + port}

        try:
            html = urllib.urlopen(url, proxies=proxy).read()
            doc = htmlParser(html, 'utf-8')
            content = doc.xpathEval(xpath)[0].content
            if content:
                ip_there = content.split(' ')[1]
                return ip_there
        except Exception, e:
            return False


class MyProxy():
    conn = sqlite3.connect('proxy.db')

    def __init__(self):
        socket.setdefaulttimeout(30)  #设置代理检验的超时时长
        self.logger = Logger('proxy.log')  #用于保存log信息的文件
        self.logger.p_log('开始获取代理...')

        #类实例化时，打开数据库并清空数据
        try:
            self.conn.execute('create table if not exists proxy (host CHAR, port CHAR, proxy_type CHAR, user CHAR, password CHAR, checked BOOL, speed INT, catch_from CHAR, catch_time TIME)')
            self.conn.execute('delete from proxy')
            self.conn.commit()
        except Exception, e:
            self.logger.p_log('打开数据库时出错，程序退出...')
            return False

    def __del__(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None
        self.logger.p_log('程序已退出...')

    def fetch_proxy(self):
        self.__fetch_sitedigger()
        self.__fetch_proxylist()

    def verify_proxy(self):
        job = VerifyProxy()
        job.verify_proxy()
        del job

    def get_proxy(self, speed=60):
        ''' 返回数据库的代理列表，格式为：[(host, port), ...]
        level是代理的级别，在代理验证时生成，取值范围（1，9），级别越高，速度越高
        函数返回响应速度（秒）小于speed的代理
        '''
        if type(speed) is not int: return False
        if speed > 9 or speed < 0: speed = 0
        try:
            proxies = self.conn.execute('select host, port from proxy where speed<=%d' % speed).fetchall()
        except:
            return False
        #格式已经是[(host, port), ...]
        return proxies

    def __fetch_sitedigger(self):
        catch_from = 'site-digger.net'
        url = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
        xpath = '//*[@id="content_detail"]/div[3]/p[3]/textarea'

        try:
            html = urllib2.urlopen(url).read()
            doc = htmlParser(html, 'utf-8')
            doc = htmlParser(html, 'utf-8')
            content = doc.xpathEval(xpath)[0].content
            if not content: return False
            self.logger.p_log('成功代开网页，获取内容的长度为：%d 字节' % len(content))
        except:
            self.logger.p_log('打开目标网页 %s 获取内容时出错，退出中...' % (url))

        proxies = []
        for ip_port in content.split('\n')[2:-2]:
            try:
                proxy = (ip_port.split(':')[0], ip_port.split(':')[1])
            except Exception, e:
                self.logger.p_log('处理记录：%s 是发生错误' % ip_port)
            if proxy not in proxies:
                proxies.append(proxy)

        self.logger.p_log('成功获取 %d 个代理，正在准备存入数据库中...' % len(proxies))
        self.__save_proxy(proxies, catch_from)

    def __fetch_proxylist(self):
        catch_from = 'proxylist.net'
        urls = [
            'http://www.proxylists.net/http.txt',
            'http://www.proxylists.net/http_highanon.txt'
        ]
        proxies = []
        for url in urls:
            try:
                content = urllib2.urlopen(url).read()
                if not content: return False
                self.logger.p_log('成功代开网页，获取内容的长度为：%d 字节' % len(content))
                for ip_port in content.split('\r\n')[:-1]:
                    try:
                        proxy = (ip_port.split(':')[0], ip_port.split(':')[1])
                    except Exception, e:
                        self.logger.p_log('处理记录：%s 是发生错误' % ip_port)
                    if proxy not in proxies:
                        proxies.append(proxy)
            except:
                pass
        self.logger.p_log('成功获取 %d 个代理，正在准备存入数据库中...' % len(proxies))
        self.__save_proxy(proxies, catch_from)

    def __save_proxy(self, proxies, catch_from=''):
        if proxies:
            for host, port in proxies:
                try:
                    row = self.conn.execute('select host from proxy where host=%s and port=%s' % (host, port)).fetchone()
                except:
                    row = None
                try:
                    if row:
                        self.logger.p_log('代理 %s:%s 已存在' % (host, port))
                        continue
                    else:
                        self.conn.execute('insert into proxy (host, port, proxy_type, catch_from, catch_time) values (?,?,?,?,?)', (host, port, 'http', catch_from, time.time()))
                except Exception, e:
                    self.logger.p_log('代理 %s:%s 保存失败' % (host, port))
            self.conn.commit()  #记得及时提交

        self.logger.p_log('目标代理列表已入库，等待校验中...')


if __name__ == '__main__':
    job = MyProxy()
    job.fetch_proxy()
    job.verify_proxy()
    del job
