# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#统计产量信息数据收集, 每分钟统计一次， 以后MES看板的汇总信息都从此处获取
#litz,20200413
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
    this_time_hour = (now_time+datetime.timedelta(hours=-1)).strftime("%H")
    # this_time_day = (now_time + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    this_time_day = now_time.strftime("%Y-%m-%d")
    this_time_time_sel = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H")

    #查询小时统计表信息是否已经存在，存在更新，不存在插入
    def HHSave( paratype ):
        # 查询是否已经登记数据
        sql = "select prod_num,snid_num,prodtest_num,meterread_num from yw_project_collect_info_hh " \
              "where order_id='%s' and prod_line='%s' and time_day='%s'  and time_hour='%s'" \
              % (db_orderid, db_prodline, this_time_day, db_hour)
        log.info(sql)
        cur.execute(sql)
        coll_row = cur.fetchone()
        # log.info('coll_row='+str(len(coll_row)) )
        if coll_row:
            if paratype == 'boxing':
                sql = "update yw_project_collect_info_hh set coll_date='%s',prod_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and time_day='%s' and time_hour='%s' " \
                      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_prodnum ,
                         db_orderid, db_prodline, this_time_day, db_hour)
            elif paratype == 'product_test':
                sql = "update yw_project_collect_info_hh set coll_date='%s',prodtest_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and time_day='%s' and time_hour='%s' " \
                      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_prodtestnum ,
                         db_orderid, db_prodline, this_time_day, db_hour)
            elif paratype == 'snid':
                sql = "update yw_project_collect_info_hh set coll_date='%s',snid_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and time_day='%s' and time_hour='%s' " \
                      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_snidnum ,
                         db_orderid, db_prodline, this_time_day, db_hour)
            elif paratype == 'meterread_test':
                sql = "update yw_project_collect_info_hh set coll_date='%s',meterread_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and time_day='%s' and time_hour='%s' " \
                      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_meterreadnum,
                         db_orderid, db_prodline, this_time_day, db_hour)
            elif paratype == 'flashburn':
                sql = "update yw_project_collect_info_hh set coll_date='%s',flashburn_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and time_day='%s' and time_hour='%s' " \
                      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_flashburnnum,
                         db_orderid, db_prodline, this_time_day, db_hour)
            log.info("更新小时统计表数据："+sql)
        else:
            sql = "insert into yw_project_collect_info_hh(order_id,prod_line,coll_date,time_day,time_hour," \
                  "prod_num,snid_num,prodtest_num,meterread_num,flashburn_num) " \
                  "values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                  % (db_orderid, db_prodline, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), this_time_day,
                     db_hour, db_prodnum, db_snidnum, db_prodtestnum, db_meterreadnum, db_flashburnnum)
            log.info("插入小时统计表数据：" + sql)
        #执行SQL并commit
        cur.execute(sql)
        mysql_conn.commit()

        if paratype == 'boxing':
            #更新项目计划表已完成数量
            sql = "select sum(prod_num) from yw_project_collect_info_hh " \
                  "where order_id='%s' and prod_line='%s' and time_day='%s' " % ( db_orderid, db_prodline, this_time_day )
            cur.execute(sql)
            coll_row = cur.fetchone()
            if coll_row:
                count_actnum = coll_row[0]
                sql = "update yw_project_plan_info set finish_num='%s' " \
                      "where order_id='%s' and prod_line='%s' and prod_date='%s' " \
                      % ( count_actnum, db_orderid, db_prodline, this_time_day )
                #执行SQL并commit
                cur.execute(sql)
                mysql_conn.commit()

    try:
        db_prodnum = 0
        db_snidnum = 0
        db_prodtestnum = 0
        db_meterreadnum = 0
        db_flashburnnum = 0
        # 统计当日产测的产量
        sql = "select Batch_Num, prod_line, DATE_FORMAT(insert_date,'%%H'), count(1) from yw_project_product_test_info " \
              "where Test_Result='Pass' and DATE_FORMAT(insert_date,'%%Y-%%m-%%d')='%s' " \
              "group by Batch_Num, prod_line, DATE_FORMAT(insert_date,'%%H')" % this_time_day
        log.info("统计当日产测的产量:" + sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for item in rows:
            db_orderid = item[0]
            db_prodline = item[1]
            db_hour = item[2]
            db_prodtestnum = item[3]
            HHSave('product_test')

        db_prodtestnum =0
        # 统计按小时扣壳的产量
        sql = "select order_id, prod_line, DATE_FORMAT(tran_date,'%%H'), count(1) from yw_project_snid_detail " \
              "where state='1' and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')='%s' " \
              "group by order_id, prod_line, DATE_FORMAT(tran_date,'%%H')" % (this_time_day)
        log.info("统计按小时扣壳的产量:" + sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for item in rows:
            db_orderid = item[0]
            db_prodline = item[1]
            db_hour = item[2]
            db_snidnum = item[3]
            HHSave("snid")

        db_snidnum = 0
        # 统计当日校表的产量
        sql = "select Batch_Num, prod_line, DATE_FORMAT(insert_date,'%%H'), count(1) from yw_project_meterread_test_info " \
              "where Test_Result='Pass' and DATE_FORMAT(insert_date,'%%Y-%%m-%%d')='%s' " \
              "group by Batch_Num, prod_line, DATE_FORMAT(insert_date,'%%H')" % this_time_day
        log.info("统计当日校表的产量:" + sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for item in rows:
            db_orderid = item[0]
            db_prodline = item[1]
            db_hour = item[2]
            db_meterreadnum = item[3]
            HHSave('meterread_test')

        db_meterreadnum = 0
        # 统计当日装箱的产量
        sql = "select order_id, prod_line, DATE_FORMAT(tran_date,'%%H'), count(1) from yw_project_boxing_info " \
              "where state='1' and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')='%s' " \
              "group by order_id, prod_line, DATE_FORMAT(tran_date,'%%H')" % this_time_day
        log.info("统计当日装箱的产量:" + sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for item in rows:
            db_orderid = item[0]
            db_prodline = item[1]
            db_hour = item[2]
            db_prodnum = item[3]
            HHSave('boxing')

        db_flashburnnum = 0
        # 统计当日烧录的产量
        sql = "select Batch_Num, prod_line, DATE_FORMAT(tran_date,'%%H'), count(1) from yw_project_flash_burn_info " \
              "where Test_Result='Pass' and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')='%s' " \
              "group by Batch_Num, prod_line, DATE_FORMAT(tran_date,'%%H')" % (this_time_day)
        log.info("统计当日烧录的产量:" + sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for item in rows:
            db_orderid = item[0]
            db_prodline = item[1]
            db_hour = item[2]
            db_flashburnnum = item[3]
            HHSave('flashburn')

    except Exception as e:
        log.error("MySql数据库处理失败!" +str(e), exc_info = True)
        return -1
    finally:
        cur.close()
        # 关闭链接
        mysql_conn.close()
        log.info('收集每小时产量数据结束!')

#持续运行
if __name__ == '__main__':
    while True:
        log, fh = loger_init()
        try:
            deal_collect()
        except Exception as ex:
            log.error("MySql数据库连接失败!" + str(ex), exc_info=True)
        finally:
            if fh:
                fh.close()
                log.removeHandler(fh)
        time.sleep(60) #每分钟处理一次


