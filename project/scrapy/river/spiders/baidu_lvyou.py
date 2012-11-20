# coding=utf-8

import os
import time
import random
import json
import sqlite3

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item
from scrapy import log

from river.settings import DATA_DIR, BAIDU_GUONEI_JINGDIAN_URLS

class Baidu03Spider(BaseSpider):
    ''' 抓取百度旅游游记/攻略信息
    # 通过ajax，用景点id和景点名称作为关键字搜索
    # 如果搜索结果的note_list >= 24，则产生下一页的请求
    # 如果搜索结果的0 < note_list < 24，则尝试存储结果后返回
    # 如果搜索结果的note_list <= 0，则直接返回
    # 每日以“最新”为搜索条件，如果页面中的游记在数据中没有，则获取存储，每日抓取前100条
    # base_url = 'http://lvyou.baidu.com/search/ajax/query?format=ajax&sid=c20613551b123dff1e40affb&word=%E5%B7%B4%E5%8E%98%E5%B2%9B&pn=0&rn=24&t=1352081450947'
    '''
    name = 'baidu_youji'
    allowed_domains = ['lvyou.baidu.com', 'hiphotos.baidu.com']
    DATABASE_FILE = os.path.join(DATA_DIR, 'baidu_youji.db').replace('\\', '/')  #数据库
    base_url = 'http://lvyou.baidu.com/search/ajax/query?format=ajax&sid=%s&word=%s&pn=%d&rn=24&t='

    #读取数据库的景点id、景点名称，生成首轮url
    conn = sqlite3.connect(DATABASE_FILE)
    scenes = conn.execute('select scene_sid, scene_sname from jingdian where jingdian=1').fetchall()
    start_urls = []
    for sid, sname in scenes:
        start_urls.append(base_url % (sid, sname, 0))
    random.shuffle(start_urls)  #随机打乱顺序
    #调试用
    #start_urls = start_urls[:3]

    #关闭数据库
    if conn is not None:
        conn.close()
        conn = None

    def parse(self, response):
        #打开数据库并设置utf-8编码
        self.conn = sqlite3.connect(self.DATABASE_FILE)
        self.conn.text_factory = 'utf-8'

        #如果解析页面数据错误，则直接返回
        try:
            page = json.loads(response.body)
            page = page['data']
        except:
            log.msg(response.url + u'  读取页面数据错误')
            print response.url + u'  读取页面数据错误'
            return

        #如果拿不到游记列表，则直接返回
        try:
            notes = page['notes_list']
            key_id = page['related_parent_sid']
            key_name = page['word']
            total = int(page['page']['total'])
            pn = int(page['page']['pn'])
        except:
            log.msg(response.url + u'  读取游记列表、关键字、搜索id时发生问题')
            print response.url + u'  读取游记列表、关键字、搜索id时发生问题'
            return

        #打印基本信息
        print u'正在处理: ', key_id, key_name, str(response.status), str(len(response.body)), u'总计:', total, u'本页开始:', pn, u'本页包含:', str(len(notes))

        #如果游记数量有24条，则根据关键字和id生成新的ajax_url
        if len(notes) >= 24:
            new_ajax = self.base_url % (key_id, key_name, pn + 24)
            request = Request(new_ajax, callback=self.parse)
            yield request

        #得到游记的信息并存储
        if len(notes) > 0:
            for note in notes:
                try:
                    note_id = note['nid']
                    note_title = note['title']
                    content = json.dumps(note, ensure_ascii=False)
                    #存入数据库
                    self.conn.execute(
                        'insert into raw (note_id, note_title, content, key_id, key_name) values (?,?,?,?,?)',
                        (note_id, note_title, content, key_id, key_name)
                    )
                    self.conn.commit()
                    log.msg(note_id + note_title + key_name + u' 保存成功')
                    print note_id, note_title, key_name, u' 保存成功'
                except:
                    log.msg(key_name + u' 保存数据时发生异常')
                    print key_name, u' 保存数据时发生异常'
        else:
            log.msg(key_name + u' 处理游记内容时发生异常')
            print key_name, u' 处理游记内容时发生异常'

        #当游记数量大于0，小于24时，表示已经抓取了全部数据，设置数据库状态
        if len(notes) > 0 and len(notes) < 24:
            try:
                self.conn.execute('update jingdian set catch_note=1 where scene_sid="%s"' % key_id)
                self.conn.commit()
                log.msg(key_id + key_name + u' 状态保存成功')
                print key_id, key_name, u' 状态保存成功'
            except:
                log.msg(key_id + key_name + u' 状态保存失败')
                print key_id, key_name, u' 状态保存失败'

        #关闭数据库
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None


class Baidu02Spider(BaseSpider):
    #抓取百度旅游海外景点信息
    name = 'baidu_jingdian'
    allowed_domains = ['lvyou.baidu.com', 'hiphotos.baidu.com']
    start_urls = ['http://lvyou.baidu.com/scene/']

    ajax_base_url = 'http://lvyou.baidu.com/scene/ajax/allview/%s?format=ajax&cid=0&pn=%d&t='  # 用于生成完整的ajax请求地址
    DATABASE_FILE = os.path.join(DATA_DIR, 'baidu_jingdian.db').replace('\\', '/')  #数据库

    def parse(self, response):
        #取得各国id生成ajax_url发送给parse_json处理
        hxs = HtmlXPathSelector(response)
        urls = hxs.select('//*[@id="body"]/section/article/div/div[2]/div[2]/div[2]/div[2]/div/div/a/@href').extract()
        for url in urls[1:]:
            ajax_url = self.ajax_base_url % (url.split('/')[-1], 1)
            log.msg(ajax_url + u'  【国际】第一页ajax_url成功生成')
            request = Request(ajax_url, callback=self.parse_json)
            request.meta['china'] = 0  #非中国景点
            yield request

        #产生国内景点首个url
        for url in BAIDU_GUONEI_JINGDIAN_URLS[1:]:
            request = Request(url, callback=self.parse_json)
            log.msg(url + u'  【国内】第一页ajax_url成功生成')
            request.meta['china'] = 1  #中国景点
            yield  request

    def parse_json(self, response):
        #打开数据库并设置utf-8编码
        self.conn = sqlite3.connect(self.DATABASE_FILE)
        self.conn.text_factory = 'utf-8'

        #打印基本信息
        print 'precessing: ', response.url, str(response.status), str(len(response.body))

        #如果拿不到数据，则直接返回
        try:
            all = json.loads(response.body)
        except:
            log.msg(response.url + u'  读取页面数据错误')
            return

        #判断是否需要生成其他的ajax_url，如果子景点总量大于16，且当前页码为1时
        try:
            main_total = int(all['data']['scene_total'])  #子景点总量
            page_no = int(all['data']['current_page'])  #当前页码
            main_sid = all['data']['sid']  #本景点id，用于生成新的ajax_url
        except:
            log.msg(response.url + u'  获取scene_total异常')
            main_total = 0
            page_no = 1
            main_id = ''
        if main_total > 16 and page_no < 2:
            #如果符合条件，则从第2页开始生成
            for pn in range(2, main_total / 16 + 2):
                try:
                    ajax_url = self.ajax_base_url % (main_sid, pn)
                    log.msg(ajax_url + u'  新的ajax_url成功生成')
                    request = Request(ajax_url, callback=self.parse_json)
                    request.meta['china'] = response.meta['china']
                    yield request
                except:
                    log.msg(response.url + u'  生成更多ajax_url异常')

        #分析scene_list数据
        try:
            scene_list = all['data']['scene_list']
            for scene in scene_list:
                #尝试取得每个scene/content/unmissable，
                scene_content = json.loads(scene['content'])  #载入scene中content，json
                try:
                    unmissable = len(scene_content['unmissable']['list'])
                except:
                    unmissable = 0
                    log.msg(response.url + u'  获取unmissable异常')

                if unmissable > 0:
                    #如果有unmissable，则用该scene的id生成新的第一页ajax_url
                    try:
                        ajax_url = self.ajax_base_url % (scene['sid'], 1)
                        log.msg(ajax_url + u'  新的ajax_url成功生成')
                        request = Request(ajax_url, callback=self.parse_json)
                        request.meta['china'] = response.meta['china']
                        yield request
                    except:
                        log.msg(response.url + u'  为scene_list生成首个ajax_url异常')
                else:
                    #否则表示已经是尽头，直接存储（id, title, parent_id, main_info, content, time）
                    try:
                        scene_content_str = json.dumps(scene_content, ensure_ascii=False)  #dump为字符串
                        scene_sname = scene['sname']
                        scene_sid = scene['sid']
                        scene_parent_sid = scene['parent_sid']
                        del(scene['content'])
                        scene_info_str = json.dumps(scene, ensure_ascii=False) #将每个scene主要信息dump为字符串
                        is_china = int(response.meta['china'])
                        #存入数据库
                        self.conn.execute(
                            'insert into raw (scene_sname, scene_sid, parent_sid, main_info, content, catch_time, china, jingdian) values (?,?,?,?,?,?,?,?)',
                            (scene_sname, scene_sid, scene_parent_sid, scene_info_str, scene_content_str, time.time(), is_china, 1)
                        )
                        self.conn.commit()
                    except:
                        log.msg(response.url + u'  单个scene信息入库异常')
        except:
            log.msg(response.url + u'  获取scene_list异常')

        #分析、存储主信息（id, title, parent_id, main_info, content, time）
        try:
            main_content = json.loads(all['data']['content'])
            main_content_str = json.dumps(main_content, ensure_ascii=False)
            main_sid = all['data']['sid']
            main_sname = all['data']['sname']
            main_parent_sid = all['data']['parent_sid']
            del(all['data']['content'])
            main_info_str = json.dumps(all['data'], ensure_ascii=False)
            is_china = int(response.meta['china'])
            #存入数据库
            try:
                self.conn.execute(
                    'insert into raw (scene_sname, scene_sid, parent_sid, main_info, content, catch_time, china, jingdian) values (?,?,?,?,?,?,?,?)',
                    (main_sname, main_sid, main_parent_sid, main_info_str, main_content_str, time.time(), is_china, 0)
                )
                self.conn.commit()
            except:
                log.msg(response.url + u'  主干信息入库异常')
        except:
            log.msg(response.url + u'  获取主干信息异常')

        #关闭数据库
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None


class Baidu01Spider(BaseSpider):
    #抓取百度旅游国内景点信息
    name = 'baidu_guonei_jingdian'
    allowed_domains = ['lvyou.baidu.com', 'hiphotos.baidu.com']
    start_urls = BAIDU_GUONEI_JINGDIAN_URLS[:1]  #仅用于测试，随便选一个开始

    ajax_base_url = 'http://lvyou.baidu.com/scene/ajax/allview/%s?format=ajax&cid=0&pn=%d&t='  # 用于生成完整的ajax请求地址
    DATABASE_FILE = os.path.join(DATA_DIR, 'baidu_guonei_jingdian.db').replace('\\', '/')  #数据库

    def parse(self, response):
        #打开数据库并设置utf-8编码
        self.conn = sqlite3.connect(self.DATABASE_FILE)
        self.conn.text_factory = 'utf-8'

        #打印基本信息
        print 'precessing: ', response.url, str(response.status), str(len(response.body))

        #如果拿不到数据，则直接返回
        try:
            all = json.loads(response.body)
        except:
            log.msg(response.url + u'  读取页面数据错误')
            return

        #判断是否需要生成其他的ajax_url，如果子景点总量大于16，且当前页码为1时
        try:
            main_total = int(all['data']['scene_total'])  #子景点总量
            page_no = int(all['data']['current_page'])  #当前页码
            main_sid = all['data']['sid']  #本景点id，用于生成新的ajax_url
        except:
            log.msg(response.url + u'  获取scene_total异常')
            main_total = 0
            page_no = 1
            main_id = ''
        if main_total > 16 and page_no < 2:
            #如果符合条件，则从第2页开始生成
            for pn in range(2, main_total / 16 + 2):
                try:
                    ajax_url = self.ajax_base_url % (main_sid, pn)
                    log.msg(ajax_url + u'  新的ajax_url成功生成')
                    request = Request(ajax_url, callback=self.parse)
                    yield request
                except:
                    log.msg(response.url + u'  生成更多ajax_url异常')

        #分析scene_list数据
        try:
            scene_list = all['data']['scene_list']
            for scene in scene_list:
                #尝试取得每个scene/content/unmissable，
                scene_content = json.loads(scene['content'])  #载入scene中content，json
                try:
                    unmissable = len(scene_content['unmissable']['list'])
                except:
                    unmissable = 0
                    log.msg(response.url + u'  获取unmissable异常')

                if unmissable > 0:
                    #如果有unmissable，则用该scene的id生成新的第一页ajax_url
                    try:
                        ajax_url = self.ajax_base_url % (scene['sid'], 1)
                        log.msg(ajax_url + u'  新的ajax_url成功生成')
                        request = Request(ajax_url, callback=self.parse)
                        yield request
                    except:
                        log.msg(response.url + u'  为scene_list生成首个ajax_url异常')
                else:
                    #否则表示已经是尽头，直接存储（id, title, parent_id, main_info, content, time）
                    try:
                        scene_content_str = json.dumps(scene_content, ensure_ascii=False)  #dump为字符串
                        scene_sname = scene['sname']
                        scene_sid = scene['sid']
                        scene_parent_sid = scene['parent_sid']
                        del(scene['content'])
                        scene_info_str = json.dumps(scene, ensure_ascii=False) #将每个scene主要信息dump为字符串
                        #存入数据库
                        self.conn.execute(
                            'insert into raw (scene_sname, scene_sid, parent_sid, main_info, content, catch_time) values (?,?,?,?,?,?)',
                            (scene_sname, scene_sid, scene_parent_sid, scene_info_str, scene_content_str, time.time())
                        )
                        self.conn.commit()
                    except:
                        log.msg(response.url + u'  单个scene信息入库异常')
        except:
            log.msg(response.url + u'  获取scene_list异常')

        #分析、存储主信息（id, title, parent_id, main_info, content, time）
        try:
            main_content = json.loads(all['data']['content'])
            main_content_str = json.dumps(main_content, ensure_ascii=False)
            main_sid = all['data']['sid']
            main_sname = all['data']['sname']
            main_parent_sid = all['data']['parent_sid']
            del(all['data']['content'])
            main_info_str = json.dumps(all['data'], ensure_ascii=False)
            #存入数据库
            try:
                self.conn.execute(
                    'insert into raw (scene_sname, scene_sid, parent_sid, main_info, content, catch_time) values (?,?,?,?,?,?)',
                    (main_sname, main_sid, main_parent_sid, main_info_str, main_content_str, time.time())
                )
                self.conn.commit()
            except:
                log.msg(response.url + u'  主干信息入库异常')
        except:
            log.msg(response.url + u'  获取主干信息异常')

        #关闭数据库
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None