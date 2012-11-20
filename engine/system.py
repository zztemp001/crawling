#coding=utf-8

import subprocess, sys
import logging
import time


def run(cmd=''):
    if not cmd: return False
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def daemon_in_win32(*args, **kwargs):
    # 让python在windows的隐藏子进程中运行
    # also works for Popen.
    # It creates a new *hidden* window, so it will work in frozen apps (.exe).
    IS_WIN32 = 'win32' in str(sys.platform).lower()

    if IS_WIN32:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
    retcode = subprocess.call(*args, **kwargs)

    return retcode

class Logger():
    log_file = 'log.txt'
    log_level = logging.DEBUG
    logger = logging.getLogger()

    def __init__(self, log_file=None):
        if type(log_file) is str: self.log_file = log_file  #如果指定新的记录文件

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("[%(asctime)s]  %(message)s")

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.log_level)

    def p_log(self, msg):
        print '[ %s ]  %s' % (str(time.asctime()), msg)
        self.logger.log(self.log_level, msg=msg)

if __name__ == "__main__":
    logger = Logger()
    logger.p_log('程序行ioooo')
