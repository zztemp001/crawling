#coding=utf-8

import threading

#线程同步锁
lock = threading.Lock()

def synchronous(f):
    def call(*args, **kwargs):
        lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            lock.release()
    return call

#获取一个待验证代理
@synchronous
def getproxy():
    global proxies
    if len(proxies)>0:
        return proxies.pop()
    else:
        return ''

#保存验证结果
@synchronous
def saveresult(proxy):
    global result

    if not(proxy in result):
        result.append(proxy)

#init thread_pool
thread_pool = []

for i in range(20):
    th = threading.Thread(target=verify,args=())
    thread_pool.append(th)

# start threads one by one
for thread in thread_pool:
    thread.start()

#collect all threads
for thread in thread_pool:
    threading.Thread.join(thread)

#encoding=utf-8
#@description：蜘蛛抓取内容。

import Queue
import threading
import urllib,urllib2
import time
from BeautifulSoup import BeautifulSoup

hosts = ["http://www.baidu.com","http://www.163.com"]#要抓取的网页

queue = Queue.Queue()
out_queue = Queue.Queue()

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()
            proxy_support = urllib2.ProxyHandler({'http':'http://xxx.xxx.xxx.xxxx'})#代理IP
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
            urllib2.install_opener(opener)

            #grabs urls of hosts and then grabs chunk of webpage
            url = urllib.urlopen(host)
            chunk = url.read()

            #place chunk into out queue
            self.out_queue.put(chunk)

            #signals to queue job is done
            self.queue.task_done()

class DatamineThread(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            chunk = self.out_queue.get()

            #parse the chunk
            soup = BeautifulSoup(chunk)
            print soup.findAll(['title'])

            #signals to queue job is done
            self.out_queue.task_done()

            start = time.time()

def main():

#spawn a pool of threads, and pass them queue instance

    t = ThreadUrl(queue, out_queue)
    t.setDaemon(True)
    t.start()

    #populate queue with data
    for host in hosts:
        queue.put(host)

    dt = DatamineThread(out_queue)
    dt.setDaemon(True)
    dt.start()


    #wait on the queue until everything has been processed
    queue.join()
    out_queue.join()

main()
print "Elapsed Time: %s" % (time.time() - start)