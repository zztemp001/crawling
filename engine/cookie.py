#coding=utf-8

import cookielib

#可以通过cookielib.Cookie构造一个cookie
#可以通过cookielib.CookieJar生成一个cookiejar对象
#cookiejar.set_cookie(cookie)
#cookiejar.save()

class Cookie():
    def __init__(self):
        pass

    def newCookieJar(self, cookieFileName=None):
        try:
            if cookieFileName:
                return cookielib.CookieJar(cookieFileName)
            else:
                return cookielib.CookieJar()
        except Exception, msg:
            return False

    def checkCookie(cookieNameList, cookieJar):
        ''' 检查cookijar对象中是否存在相应的键
        @param: cookieNameList, 要检索的键，类型为list
        @param: cookieJar, 要检索的cookie，类型为cookiejar对象
        @returns: 如果找到了所有的键，则返回True，否则返回False
        '''
        for cookieName in cookieNameList:
            if not cookieName in [cookie.name for cookie in cookiejar]:
                return False

        return cookieFound