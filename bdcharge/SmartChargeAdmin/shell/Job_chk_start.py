# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#判断进程是否存在，如果不存在了，则直接启动。
#litz,20190831
##########################################################################################
import os
import datetime
import psutil
import logging
import os

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
    print(log_file_temp)
    fh = logging.FileHandler(log_file_temp)  # 定义一个写文件的handler
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter(
        '[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] [%(process)-7d] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    #print('public',logger)
    if  not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh

def judgeprocess(processname):
    pl = psutil.pids()
    flag=-1
    for pid in pl:
        try:
            tmpprcname=psutil.Process(pid).cmdline()
        except Exception as e:
            print(e)
            continue
        # print(pid, tmpprcname)
        for procname in tmpprcname:
            if processname in procname and "grep" not in procname:
                flag=0
                break
        if flag==0:
            break
    else:
        print("not found")

    return flag

#检查进程是否存在,不存在则重启
def chk_start_proc(shellpath, shellname):
    log, fh = loger_init()
    if judgeprocess(shellname) == 0:
        log.info("检测到进程【"+str(shellname)+"】已经存在！")
    else:
        cmd="nohup python "+shellpath+shellname+" &"
        log.info("进程【"+str(shellname)+"】不存在，重启!")
        log.info(cmd)
        ret=os.system(cmd)
        # print(datetime.datetime.now(),"重完命令执行完成：", ret)

#持续运行
if __name__ == '__main__':
    log, fh = loger_init()
    log.info('开始检查程序是否存在,如果不存在则重启')
    # chk_start_proc('/home/admin/lqkj_admin/shell/', 'data_smpd_sync.py') #不需要和sqlserver数据库同步了，20200424
    chk_start_proc('/home/admin/lqkj_admin/shell/', 'data_mes_collect.py')
    chk_start_proc('/home/admin/lqkj_admin/shell/', 'fileup_proc.py')
    chk_start_proc('/home/admin/lqkj_admin/shell/', 'data_mes_collect_direct_err.py')
    chk_start_proc('/home/admin/lqkj_admin/shell/', 'data_svn_sync.py')
    chk_start_proc('/home/admin/lqkj_admin/shell/', 'get_workflow_data.py')  #流程审批
    log.info('检查程序是否存在完成!')
