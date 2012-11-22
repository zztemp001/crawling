#coding=utf-8

#使用wb参数写二进制文件

def save_dict_as_row(conn=None, table_name=None, dict_data=None):
    if not (conn and table_name): return False
    try:
        query_str = 'insert into %s (%s) values (%s)' % (table_name, ','.join(dict_data.keys()), ','.join('?'*len(dict_data)))
        conn.execute(query_str, tuple(dict_data.values()))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False