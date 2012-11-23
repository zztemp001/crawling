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
            try:
                conn.execute('drop table %s' % table_name)
                conn.commit()
                print 'Table %s Dropped...' % table_name
            except Exception, e:
                print e
        if table_name and fields is not None:
            query_str = 'create table if not exists %s (%s)' % (table_name, ','.join([key + ' TEXT' for key in fields]))
            conn.execute(query_str)
            conn.commit()
            print 'Table %s have been created' % table_name
        return conn
    except Exception, e:
        print e
        return False