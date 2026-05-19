# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#扫码配对程序中摄像头识别modelid有问题，写个程序判断后边的校验位是否正确。
#litz,20200401
##########################################################################################

import time
import datetime
import pymysql
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
    if os.path.exists(+'log/'):
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

#扫码配对工装登记扫码信息
def modelid_check():
    # log, fh=loger_init( )
    try:
        mysql_conn = pymysql.Connect(
            host='192.168.2.174',
            port=3306,
            user='lqkj',
            passwd='LQkj666_2019',
            db='lqkj_db',
            charset='utf8')
        cur = mysql_conn.cursor()
    except Exception as e:
        print("MySql数据库连接失败!", e)
        return -1
    #先获取本次处理时间
    thisduetime=datetime.datetime.now()

    #获取数据
    sql = "select model_id, tran_date,state from yw_project_snid_detail where DATE_FORMAT(tran_date,'%Y-%m') ='2020-02'"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    i=0
    errnum=0
    for item in rows:
        i=i+1
        modelid=item[0]
        # modelid='1110001000101234567892'
        # print('开始处理第[%s]个模块:'%i, modelid)

        zjq=0
        for j in range(0, len(modelid)-1):
            qz=(3 if(j%2 ==0) else 1)
            zjq = zjq + int(modelid[j])*int(qz)
        a, b=divmod(zjq, 10)
        checksum=(10-b if(b>0) else 0)
        if str(modelid[-1]) != str(checksum):
            if str(item[2])=='0':
                continue
            errnum=errnum+1
            print('第[%s]个模块:'%i, item[1], modelid, '校验值错,模块ID识别有误!', 'checksum=',checksum)
        else:
            # print('模块ID识别正确!')
            pass
        # break
    print('errnum=', errnum)
    mysql_conn.close()

#持续运行
if __name__ == '__main__':
    modelid_check()





