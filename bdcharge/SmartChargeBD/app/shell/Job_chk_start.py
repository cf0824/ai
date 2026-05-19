# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
# 判断进程是否存在，如果不存在了，则直接启动。
# litz,20190831
##########################################################################################
import datetime
import logging
import os
import time
from os.path import dirname, abspath

import psutil

# 日志初始化,日志名称

# 获取根目录
base_dir = dirname(dirname(dirname(abspath(__file__))))
# 修改成linux目录
localhome = base_dir.replace('\\', '/')  # 本地目录
print(localhome)
LOG_DIR = 'logs'  # log directory name

print(localhome)
global logger, fh
logger = logging.getLogger(str(os.getpid()))


def loger_init():
    # 日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    logname = os.path.basename(__file__).split('.py')[0]

    log_dir = os.path.join(localhome, LOG_DIR, time.strftime('%Y-%m-%d'))
    os.makedirs(log_dir, exist_ok=True)

    log_file_name = f"{logname}_{now_time}.log"
    log_file_path = os.path.join(log_dir, log_file_name)
    print(log_file_path)
    print(log_file_name)
    fh = logging.FileHandler(log_file_path)  # 定义一个写文件的handler
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter(
        '[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] [%(process)-7d] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    # print('public',logger)
    if not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh


def judgeprocess(processname):
    log, fh = loger_init()
    pl = psutil.pids()
    # log.info(f'所有的活动进程pid:{pl}')
    flag = -1
    for pid in pl:
        try:
            tmpprcname = psutil.Process(pid).cmdline()
            # log.info(f'pid, tmpprcname:{pid},{tmpprcname}')
        except Exception as e:
            print(e)
            continue
        for procname in tmpprcname:
            if processname in procname and "grep" not in procname:
                flag = 0
                break
        if flag == 0:
            break
    else:
        print("not found")

    return flag


# 检查进程是否存在,不存在则重启
def chk_start_proc(shellpath, shellname):
    log, fh = loger_init()
    if judgeprocess(shellname) == 0:
        log.info("检测到进程【" + str(shellname) + "】已经存在！")
    else:
        #cmd = "nohup python " + shellpath + shellname + " &"
        cmd ="nohup python3 " + shellpath + shellname + " > /dev/null 2>&1 &"

        log.info("进程【" + str(shellname) + "】不存在，重启!")
        log.info(cmd)
        ret = os.system(cmd)
        # print(datetime.datetime.now(),"重完命令执行完成：", ret)


def main():
    log, fh = loger_init()
    try:
        log.info('开始检查程序是否存在,如果不存在则重启')
        chk_start_proc(localhome + '/app/shell/', 'handle_cmd2.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_args.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_eq_online.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_order_check.py')
        chk_start_proc(localhome + '/app/shell/', 'pre_order_check.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_wx_cashout.py')
        chk_start_proc(localhome + '/app/shell/', 'send_wx_temp_msg.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_deduction_money.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_card_order.py')
        chk_start_proc(localhome + '/app/shell/', 'open_charge_resend.py')
        chk_start_proc(localhome + '/app/shell/', 'handle_card_order_stop.py')
        log.info('检查程序是否存在完成!')
    except Exception as e:
        log.error(e, exc_info=True)


# 持续运行
if __name__ == '__main__':
    main()
