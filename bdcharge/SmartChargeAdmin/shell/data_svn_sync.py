# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import time
import datetime
import logging
import os

##########################################################################################
#评审单附件同步到SVN服务器，写个程序异步同步。
#litz,2020420
##########################################################################################
class SvnOpera:
    def __init__(self, path='/home/admin/lqkj_admin/SVN/项目外来文件'):
        self.path = path

    def svnUp(self):
        os.chdir(self.path)
        os.system('svn up')
        log.info('svn up ok')
    def update(self):
        os.chdir(self.path)
        res = os.popen('svn status')
        for item in res:
            log.info('item='+str(item) )
            if item.find('?') != -1:
                uri = item.replace('?', '').strip()
                os.system('svn add "%s"' % uri)
                log.info('svn add "%s"' % uri)
            elif item.find('!') != -1:
                uri = item.replace('!', '').strip()
                os.system('svn delete "%s"' % uri)
                log.info('svn delete "%s"' % uri)
        os.system("svn ci -m 'OASystem Add'")

#日志初始化,日志名称
localhome="/home/admin/lqkj_admin/"
global logger, fh
logger = logging.getLogger(str(os.getpid()))
def loger_init( ):
    #日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    logname = os.path.basename(__file__).split('.py')[0]
    if os.path.exists(localhome+'log/'):
        log_file_temp = localhome+'log/'+logname+'_'+now_time+'.log'
    else:
        log_file_temp = logname + '_' + now_time + '.log'
    # print(log_file_temp)
    fh = logging.FileHandler(log_file_temp)  # 定义一个写文件的handler
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter(
        '[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] [%(process)-7d] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    #print('public',logger)
    if  not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh

#SVN文件同步
def svn_sync():
    try:
        so = SvnOpera()
        so.update()
        # 更新svn
        so.svnUp()
    except Exception as ex:
        log.error('程序运行错误:'+str(ex), exc_info = True)
        return  -1


#持续运行
if __name__ == '__main__':
    log, fh = loger_init()
    while True:
        try:
            # print('svn sync---begin')
            svn_sync()

        except Exception as ex:
            # log.error(ex, exc_info = True)
            pass

        time.sleep(15) #10秒钟同步一次





