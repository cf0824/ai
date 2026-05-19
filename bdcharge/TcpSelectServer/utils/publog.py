__author__ = 'litz'
############################################################################################
# 共函数库
# add by litz,20181110
############################################################################################
import os
import datetime
import logging
import logging.handlers


# 日志初始化,日志名称
# global logger, fh
# logger = logging.getLogger(str(os.getpid()))
import threading


def loger_init(logname):
    # # 日志中添加自定义字段，终端ID和线程ID
    logger = logging.getLogger(str(os.getpid()))
    logger.removeHandler(logger.handlers)

    now_date = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    if os.path.exists('logs/'):
        log_file_temp = 'logs/'+logname+'_'+now_date+'.log'
    else:
        log_file_temp = logname + '_' + now_date + '.log'

    # fh = logging.handlers.RotatingFileHandler(log_file_temp, maxBytes=1024*1024*100, backupCount=30)
    fh = logging.handlers.TimedRotatingFileHandler(log_file_temp, when='midnight', interval=1, backupCount=30)
    # fh.addFilter(thread_id)
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    # fh_formatter = logging.Formatter(
    #     '[%(process)-4d][%(thread_id)-6d][%(levelname)-5s][%(filename)-10s line:%(lineno)-4d][%(asctime)s] [%(message)s]')  # 设置输出格式
    fh_formatter = logging.Formatter(
        '[%(process)-4d][%(levelname)-5s][%(filename)-10s,line:%(lineno)-4d][%(asctime)s] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    #print('public',logger)
    # if not logger.handlers:
    logger.addHandler(fh)  # 将handler加入logger
    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(fh_formatter)
    return logger, fh

