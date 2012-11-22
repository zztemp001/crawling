#coding=utf-8

import sqlite3, random

def init_db(db='', table_name='', fields=None, drop_first=False):
    ''' 初始化数据库，返回一个链接
    @params: db, 数据库所在路径，绝对路径
    @params: table, keys, 如果给出，且表格不存在的情况下，使用keys生成名为table的表，字段都是Text类型
    @returns: 初始化成功，返回数据库链接，失败则返回False
    '''
    if not db: return False
    try:
        conn = sqlite3.connect(db)
        if drop_first:
            #conn.execute('drop table %s' % table_name)
            #conn.commit()
            pass
        if table_name and fields is not None:
            query_str = 'create table if not exists %s (%s)' % (table_name, ','.join([key + ' TEXT' for key in fields]))
            conn.execute(query_str)
            conn.commit()
        return conn
    except Exception, e:
        print e
        return False

def show_sample(db='', table_name='', field='', sample_count=1):
    if not (db and table_name and field): return False
    result = dict()
    try:
        conn = sqlite3.connect(db)
        total = conn.execute('select count(*) from %s' % table_name).fetchone()[0]
        rows_range = random.sample()
        row_id = 8095
        row = conn.execute('select scene_sname, main_info, content from jingdian where rowid=%d' % row_id).fetchone()
        return result
    except Exception, e:
        print e
        return False