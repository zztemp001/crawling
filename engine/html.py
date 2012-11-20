#coding=utf-8

import re

def strip_tags_re(html):
    ''' 简单过滤html标记
    返回过滤后的字符串
    '''
    return re.sub(r'</?\w+[^>]*>','',str)

def strip_tags(htmlstr):
    ''' 过滤HTML中的标签，将HTML中标签等信息去掉
    @param htmlstr HTML字符串.
    '''
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=_replaceCharEntity(s)#替换实体
    return s

def _replaceCharEntity(htmlstr):
    ''' 替换常用HTML字符实体.
    使用正常的字符替换HTML中特殊的字符实体.
    可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    @param htmlstr HTML字符串.
    '''
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                   'lt':'<','60':'<',
                   'gt':'>','62':'>',
                   'amp':'&','38':'&',
                   'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def decode_POI(C):
    """解析大众点评POI参数，返回一个dict
    """
    digi = 16
    add = 10
    plus = 7
    cha = 36
    I = -1
    H = 0
    B = ''
    J = len(C)
    G = ord(C[-1])
    C = C[:-1]
    J -= 1

    for E in range(J):
        D = int(C[E], cha) - add
        if D >= add:
            D = D - plus
        B += _to_base36(D)
        if D > H:
            I = E
            H = D

    A = int(B[:I], digi)
    F = int(B[I+1:], digi)
    L = (A + F - int(G)) / 2
    K = float(F - L) / 100000
    L = float(L) / 100000
    return {'lat': K, 'lng': L}

def _to_base36(value):
    """将10进制整数转换为36进制字符串，用于decode_POI（）函数
    """
    if not isinstance(value, int):
        raise TypeError("expected int, got %s: %r" % (value.__class__.__name__, value))

    if value == 0:
        return "0"

    if value < 0:
        sign = "-"
        value = -value
    else:
        sign = ""

    result = []

    while value:
        value, mod = divmod(value, 36)
        result.append("0123456789abcdefghijklmnopqrstuvwxyz"[mod])

    return sign + "".join(reversed(result))

if __name__ == '__main__':
    print decode_POI('ISSCCGZUAIDSHS')