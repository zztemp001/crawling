#coding=utf-8

import json, random, sqlite3

def extract_all(data=None, keys=None):
    if not (data and keys): return False
    result = dict.fromkeys(keys)
    for key in keys:
        try:
            result[key] = __get_json_item_by_key(data, key)
        except Exception, e:
            print e
    return result

def get_item(data=None, key=None):
    return __get_json_item_by_key(data, key, False)

def get_list(data=None, key=None):
    return __get_json_item_by_key(data, key, True)

def __get_json_item_by_key(data=None, key=None, is_get_list=False, splitter='__'):
    ''' 缺省返回空字符串 u''
    如果是数字，则转换为str
    如果是列表或字典，则转换为json.dumps
    '''
    default = list() if is_get_list else u''
    if not data or not key: return default
    path_list = key.split(splitter)
    for key in path_list:
        if key in data:
            data = data[key]
        else:
            return default
    t = type(data)
    if t is int or t is float: return str(data)
    if (t is list and not is_get_list) or t is dict: return json.dumps(data)
    return data

def get_html_items_by_xpath(data=None, xpath=None):
    pass

if __name__ == '__main__':
    conn = sqlite3.connect(r'D:\backup\database\sqlite\processing\baidu_lvyou.db')
    #total = conn.execute('select count(*) from jingdian').fetchone()[0]
    #row_id = random.randint(1, total)
    row_id = 8095
    row = conn.execute('select scene_sname, main_info, content from jingdian where rowid=%d' % row_id).fetchone()
    print row_id, row[0]
    print 'main_info: ', str(row[1])
    print 'content: ', str(row[2])
    data = json.loads(str(row[1]))
    content = json.loads(str(row[2]))
    data.update(content)
    item_key = 'user_plan > user_plan > plan'
    item_value = __get_json_item_by_key(data, item_key, get_list=False)
    print item_key, item_value
    if type(item_value) is list:
        for v in item_value:
            print v