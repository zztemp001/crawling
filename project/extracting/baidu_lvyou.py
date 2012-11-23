#coding=utf-8

import random, json, pickle, time
from engine.extract import extract_all, show_sample
from engine.prepair import init_db
from engine.output import save_dict_as_row

DEBUG = True

#将原始的json数据生成一个初步表
def step_01():
    db = r'D:\backup\database\sqlite\processing\baidu_lvyou.db'
    source_table = 'jingdian'
    target_table = 'temp'
    fields = ['abstract', 'abstract_new', 'cid', 'ext', 'fmap_x', 'fmap_y', 'module',
            'is_china', 'scene_album', 'full_url', 'going_count', 'gone_count',
            'is_flagged', 'is_hot', 'level', 'lower_count', 'lower_desc', 'map_info',
            'map_x', 'map_y', 'parent_ano_sid', 'parent_sid', 'pic_list', 'pic_url',
            'reference', 'scene_layer', 'self_notes', 'sid', 'sname', 'star', 'uid',
            'vid', 'user_plan', 'view_count']
    fields += ['accommodation', 'attention', 'dining', 'entertainment', 'geography_history',
             'hot_scene_show_type', 'highlight', 'brief', 'info', 'special_tpl_id',
             'leave_info', 'line', 'new_geography_history', 'notes_list_top',
             'relate_scene', 'shopping', 'ticket_info', 'traffic', 'unmissable',
             'useful', 'plane_ticket']
    conn = init_db(db, target_table, fields, drop_first=DEBUG)

    total = conn.execute('select count(*) from %s' % source_table).fetchone()[0]
    if DEBUG:
        rows_range = random.sample(range(1, total+1), 5)
    else:
        rows_range = range(1, total+1)

    for row_id in rows_range:
        try:
            row = conn.execute('select scene_sid, scene_sname, main_info, content from %s where rowid=%d' % (source_table, row_id)).fetchone()
            data = json.loads(str(row[2]))
            content = json.loads(str(row[3]))
            data.update(content)
            new_row_data = extract_all(data, fields)
            save_dict_as_row(conn, target_table, new_row_data)
            print row_id, row[1]
            print str(row[2])
            print str(row[3])
        except Exception, e:
            print e

#从pic_list字段中获取景点的相片信息
def step_02():
    db = r'D:\backup\database\sqlite\processing\baidu_lvyou.db'
    source_table = 'jingdian_final'
    source_field = 'pic_list'
    target_table = 'jingdian_pic'  #正式运行时改名
    related_field = ['sid']
    fields = related_field + ['pic_url', 'full_url', 'is_cover', 'ext__size', 'ext__width',
                              'ext__height', 'ext__upload_uid', 'ext__upload_uname']
    conn = init_db(db, target_table, fields, drop_first=DEBUG)

    total = conn.execute('select count(*) from %s' % source_table).fetchone()[0]
    if DEBUG:
        rows_range = random.sample(range(1, total+1), 5)
    else:
        rows_range = range(1, total+1)

    for row_id in rows_range:
        query_str = 'select %s, %s content from %s where rowid=%d' % (related_field[0], source_field, source_table, row_id)
        try:
            row = conn.execute(query_str).fetchone()
            if len(row[1]) < 1: continue
            data = json.loads(row[1])
            if type(data) is not list: data = [data]
            for source_row_data in data:
                new_row_data = extract_all(source_row_data, fields)
                new_row_data[related_field[0]] = row[0]
                save_dict_as_row(conn, target_table, new_row_data)
                print row[0]
                print new_row_data
        except Exception, e:
            print e

#从pic_list字段中获取景点的相片信息
def extract_from_jingdian(db=None, source_table=None, target_table=None, source_field=None, source_data_path=None, related_field=None, fields=None):
    if not (db and source_table and target_table and source_field and related_field and fields): return False
    DEBUG = False

    conn = init_db(db, target_table, fields, drop_first=True)
    total = conn.execute('select count(*) from %s' % source_table).fetchone()[0]
    if DEBUG:
        rows_range = random.sample(range(1, total+1), 20)
    else:
        rows_range = range(1, total+1)

    for row_id in rows_range:
        query_str = 'select %s, %s content from %s where rowid=%d' % (related_field[0], source_field, source_table, row_id)
        try:
            row = conn.execute(query_str).fetchone()
            if not row[1]: continue
            data = json.loads(str(row[1]))  #需要时
            if source_data_path: data = data[source_data_path]
            if type(data) is not list: data = [data]
            for source_row_data in data:
                new_row_data = extract_all(source_row_data, fields)
                new_row_data[related_field[0]] = row[0]
                save_dict_as_row(conn, target_table, new_row_data)
                print '\n', row[0], 'Succeed...'
                print new_row_data
        except Exception, e:
            print e


def extract_from_jingdian_02(db=None, source_table=None, target_table=None, source_field=None, source_data_path=None, related_field=None, fields=None):
    if not (db and source_table and target_table and source_field and related_field and fields): return False
    DEBUG = False

    conn = init_db(db, target_table, fields, drop_first=True)
    total = conn.execute('select count(*) from %s' % source_table).fetchone()[0]
    if DEBUG:
        rows_range = random.sample(range(1, total+1), 30)
    else:
        rows_range = range(1, total+1)

    for row_id in rows_range:
        query_str = 'select %s, %s content from %s where rowid=%d' % (related_field[0], source_field, source_table, row_id)
        try:
            row = conn.execute(query_str).fetchone()
            if not row[1]: continue
            data = json.loads(str(row[1]))  #需要时
            if source_data_path: data = data[source_data_path]
            if type(data) is not list: data = [data]
            for source_row_data in data:
                new_row_data = dict()
                new_row_data['feature'] = source_row_data
                #new_row_data = extract_all(source_row_data, fields)
                new_row_data[related_field[0]] = row[0]
                save_dict_as_row(conn, target_table, new_row_data)
                print '\n', row[0], 'Succeed...'
                print new_row_data
        except Exception, e:
            print e

if __name__ == '__main__':
    db = r'D:\backup\database\sqlite\processing\baidu_lvyou.db'
    source_table = 'youji'
    source_field = 'content'
    source_data_path ='features_all'
    target_table = 'youji_content_features'
    related_field = ['note_id']
    #fields = related_field + ['desc']
    fields = related_field + ['feature']

    start_time = time.time()

    #show_sample(db=db, table_name=source_table, field=source_field)S

    #extract_from_jingdian(db, source_table, target_table, source_field, source_data_path, related_field, fields)
    extract_from_jingdian_02(db, source_table, target_table, source_field, source_data_path, related_field, fields)

    time_used = time.time() - start_time
    print '\n\n Total Time Used: %f' % time_used
