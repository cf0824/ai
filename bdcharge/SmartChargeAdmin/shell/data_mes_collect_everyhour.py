# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#统计每小时产量数据收集。
#litz,20190917
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

#每小时产量数据收集
def deal_collect():
    #日志文件初始化
    log, fh = loger_init()
    log.info('开始收集每小时产量数据!')
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
        log.info("MySql数据库连接失败!"+str(e) )
        return -1

    #先获取本次处理时间
    now_time = datetime.datetime.now()
    this_time_hour = (now_time+datetime.timedelta(hours=-16)).strftime("%H")
    this_time_day = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d")
    this_time_time_b = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:00:00")
    this_time_time_e = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:59:59")
    this_time_time_b2 = (now_time + datetime.timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S")
    # print(this_time_hour)
    # print(this_time_day)

    try:
        #都哪些制令单号需要统计
        sql="select distinct order_id from yw_project_snid_detail where tran_date > '%s'" % this_time_time_b2
        log.info(sql)
        cur.execute(sql)
        rows = cur.fetchall()

        for item in rows:
            orderid=item[0] #制令单号
            log.info('制令号：'+str(orderid) )
            #获取数据
            sql = "select *  from yw_project_collect_info_hh where order_id='%s' and time_day='%s' and time_hour='%s'" % (orderid, this_time_day, this_time_hour)
            log.info(sql)
            cur.execute(sql)
            coll_row = cur.fetchall()
            log.info('coll_row='+str(len(coll_row)) )
            if len(coll_row)==0:
                #还没有收集信息，现在收集一下
                # 统计上一小时的产量
                sql = "select count(*) as rownum from yw_project_snid_detail where order_id='%s' and state='1' and tran_date>='%s' and tran_date <='%s'" \
                      % (orderid, this_time_time_b, this_time_time_e)
                log.info( sql )
                cur.execute( sql )
                coll_row = cur.fetchone()
                log.info('coll_row2='+ str(len(coll_row) ) )
                sql="insert into yw_project_collect_info_hh values('%s','%s','%s','%s','%s')" % (orderid, now_time, this_time_day, this_time_hour, coll_row[0] )
                log.info(sql)
                cur.execute(sql)
                mysql_conn.commit()
                print("插入统计数据成功!")
    except Exception as e:
        log.info("MySql数据库处理失败!" +str(e) )
        return -1
    finally:
        cur.close()
        # 关闭链接
        mysql_conn.close()
        log.info('收集每小时产量数据结束!')

#持续运行
if __name__ == '__main__':
    while True:
        try:
            deal_collect()
        except Exception as ex:
            logger.info( str(ex) )

        time.sleep(900)




