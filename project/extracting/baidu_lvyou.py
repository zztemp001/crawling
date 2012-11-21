#coding=utf-8

import sqlite3, random, json

def init_db(db='', table='', keys=None):
    if not db: return False
    try:
        conn = sqlite3.connect(db)
        if table and keys is not None:
            query_str = 'create table if not exists %s (%s)' % (table, ','.join([key + ' TEXT' for key in keys]))
            conn.execute(query_str)
            conn.commit()
        return conn
    except Exception, e:
        print e
        return False

def get_data(data=None, keys=None):
    if not (data and keys): return False
    result = dict.fromkeys(keys)
    for key in keys:
        try:
            result[key] = get_item(data, key)
        except Exception, e:
            print e
    return result

def save_data(conn=None, new_row=None):
    try:
        query_str = 'insert into jingdian_final (%s) values (%s)' % (','.join(new_row.keys()), ','.join('?'*len(new_row)))
        conn.execute(query_str, tuple(new_row.values()))
        conn.commit()
    except Exception, e:
        print e

def get_item(data=None, key=None):
    ''' 缺省返回空字符串 u''
    如果是数字，则转换为str
    如果是列表或字典，则转换为json.dumps
    '''
    if key in data:
        t = type(data[key])
        if t is int or t is float: return str(data[key])
        if t is list or t is dict: return json.dumps(data[key])
        return data[key]
    else: return u''

def run():
    db = r'D:\backup\database\sqlite\processing\baidu_lvyou.db'
    table = 'jingdian_final'
    keys = ['abstract', 'abstract_new', 'cid', 'ext', 'fmap_x', 'fmap_y', 'module',
            'is_china', 'scene_album', 'full_url', 'going_count', 'gone_count',
            'is_flagged', 'is_hot', 'level', 'lower_count', 'lower_desc', 'map_info',
            'map_x', 'map_y', 'parent_ano_sid', 'parent_sid', 'pic_list', 'pic_url',
            'reference', 'scene_layer', 'self_notes', 'sid', 'sname', 'star', 'uid',
            'vid', 'user_plan', 'view_count']
    keys += ['accommodation', 'attention', 'dining', 'entertainment', 'geography_history',
             'hot_scene_show_type', 'highlight', 'brief', 'info', 'special_tpl_id',
             'leave_info', 'line', 'new_geography_history', 'notes_list_top',
             'relate_scene', 'shopping', 'ticket_info', 'traffic', 'unmissable',
             'useful', 'plane_ticket']
    conn = init_db(db, table, keys)

    total = conn.execute('select count(*) from jingdian').fetchone()[0]

    for row_id in range(1, total+1):
        try:
            row = conn.execute('select scene_sid, scene_sname, main_info, content from jingdian where rowid=%d' % row_id).fetchone()
            data = json.loads(str(row[2]))
            content = json.loads(str(row[3]))
            data.update(content)
            new_row = get_data(data, keys)
            save_data(conn, new_row)
            print row_id, row[1]
        except Exception, e:
            print e

if __name__ == '__main__':
    run()