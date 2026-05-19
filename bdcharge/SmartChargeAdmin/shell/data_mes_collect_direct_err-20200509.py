# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#统计直通率数据收集,不良率数据收集， 每分钟统计一次， 以后MES看板的汇总信息都从此处获取
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
        log.error("MySql数据库连接失败!"+str(e), exc_info=True)
        return -1

    #先获取本次处理时间
    now_time = datetime.datetime.now()
    # this_time_hour = (now_time+datetime.timedelta(hours=-1)).strftime("%H")
    # this_time_day = (now_time + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    this_time_day = now_time.strftime("%Y-%m-%d")
    # this_time_time_sel = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H")

    #查询直通率统计表信息是否已经存在，存在返回True,不存在返回False
    def DataExists(db_coll_type):
        # 查询是否已经登记数据
        sql = "select 1 from yw_project_collect_info_direct_err " \
              "where order_id='%s' and prod_line='%s' and time_day='%s' and station='%s' and coll_type='%s'" \
              % (db_orderid, db_prodline, this_time_day, db_station, db_coll_type)
        log.info(sql)
        cur.execute(sql)
        coll_row = cur.fetchone()
        if coll_row:
            return True
        else:
            return False

    # 都哪些制令单号需要统计
    sql = "select distinct order_id, prod_line from yw_project_plan_info where DATE_FORMAT(prod_date,'%%Y-%%m-%%d')='%s' " \
          "and sync_flag='1' and state='1' " % (this_time_day)
    log.info(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    try:
        #各工站信息采集
        for item in rows:
            db_orderid = item[0]  # 制令单号
            db_prodline = item[1]  # 线别

            # 统计烧录的工站列表
            sql = "select distinct Platform_Num from yw_project_flash_burn_info t  " \
                  "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                  "and t.prod_line='%s' " % (this_time_day, db_orderid, db_prodline)
            log.info("统计烧录的工站列表:" + sql)
            cur.execute(sql)
            rows = cur.fetchall()
            for item in rows:
                db_station = item[0]
                # 统计烧录的一次直通数量
                sql = "select count(1) from yw_project_flash_burn_info t " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                      "and t.prod_line='%s' and Platform_Num='%s' and Test_Result='Pass' and Board_SN not in  " \
                      "( select  Board_SN from yw_project_flash_burn_info_his h where DATE_FORMAT(h.tran_date,'%%Y-%%m-%%d')='%s' " \
                      "and h.Batch_Num='%s' and h.prod_line='%s'  " \
                      ")" % (this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计烧录的一次直通数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    direct_num = row[0]
                else:
                    direct_num = 0

                # 统计烧录的总数量
                sql = "select count(distinct Board_SN) from yw_project_flash_burn_info t  " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                      "and t.prod_line='%s' and Platform_Num='%s'" % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计烧录的总数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    prod_num = row[0]
                else:
                    prod_num = 0

                # 统计烧录的最终失败数量
                sql = "select count(1) from yw_project_flash_burn_info where DATE_FORMAT(tran_date,'%%Y-%%m-%%d')='%s' " \
                      "and  Batch_Num='%s' and  prod_line='%s' and Platform_Num='%s' and Test_Result!='Pass' " \
                      % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计烧录的不良数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    err_num = row[0]
                else:
                    err_num = 0

                # 登记数据统计信息
                if not DataExists('flashburn'):
                    sql = "insert into yw_project_collect_info_direct_err(coll_date,order_id,prod_line,time_day,station," \
                          "coll_type, prod_num,prod_direct_num, prod_err_num) " \
                          "values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_orderid, db_prodline,
                           this_time_day, db_station, 'flashburn', prod_num, direct_num, err_num)
                else:
                    sql = "update yw_project_collect_info_direct_err set coll_date='%s', prod_num='%s',prod_direct_num='%s', prod_err_num='%s' " \
                          "where order_id='%s' and  prod_line='%s' and time_day='%s' and station='%s' and prod_line='%s'" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prod_num, direct_num, err_num,
                           db_orderid, db_prodline, this_time_day, db_station)
                log.info("产测数据收集:" + sql)
                # 执行SQL并commit
                cur.execute(sql)
                mysql_conn.commit()

            #统计产测的工站列表
            sql = "select distinct Platform_Num from yw_project_product_test_info t  " \
                  "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                  "and t.prod_line='%s' " % ( this_time_day, db_orderid, db_prodline )
            log.info("统计产测的工站列表:" + sql)
            cur.execute(sql)
            rows = cur.fetchall()
            for item in rows:
                db_station = item[0]
                # 统计产测的一次直通数量
                sql = "select count(1) from yw_project_product_test_info t " \
                      "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                      "and t.prod_line='%s' and Platform_Num='%s' and Test_Result='Pass' and Board_SN not in  " \
                      "( select  Board_SN from yw_project_product_test_info_his h where DATE_FORMAT(h.insert_date,'%%Y-%%m-%%d')='%s' " \
                      "and h.Batch_Num='%s' and h.prod_line='%s'  " \
                      ")" % (this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计产测的一次直通数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    direct_num = row[0]
                else:
                    direct_num = 0

                # 统计产测的总数量
                sql = "select count(distinct Board_SN) from yw_project_product_test_info t  " \
                  "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                  "and t.prod_line='%s' and Platform_Num='%s'" % ( this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计产测的总数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    prod_num = row[0]
                else:
                    prod_num = 0

                # 统计产测的最终失败数量
                sql = "select count(1) from yw_project_product_test_info where DATE_FORMAT(insert_date,'%%Y-%%m-%%d')='%s' " \
                      "and  Batch_Num='%s' and  prod_line='%s' and Platform_Num='%s' and Test_Result!='Pass' " \
                      % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计产测的不良数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    err_num = row[0]
                else:
                    err_num = 0

                #登记数据统计信息
                if not DataExists('prodtest'):
                    sql = "insert into yw_project_collect_info_direct_err(coll_date,order_id,prod_line,time_day,station," \
                          "coll_type, prod_num,prod_direct_num, prod_err_num) " \
                          "values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_orderid, db_prodline,
                           this_time_day, db_station, 'prodtest', prod_num, direct_num, err_num)
                else:
                    sql = "update yw_project_collect_info_direct_err set coll_date='%s', prod_num='%s',prod_direct_num='%s', prod_err_num='%s' " \
                          "where order_id='%s' and  prod_line='%s' and time_day='%s' and station='%s' and prod_line='%s'" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prod_num, direct_num, err_num,
                           db_orderid, db_prodline, this_time_day, db_station,'prodtest')
                log.info("产测数据收集:"+sql)
                # 执行SQL并commit
                cur.execute(sql)

                # try:
                #     # 自动线产测数据更新
                #     sql = "select sum(prod_num) from yw_project_collect_info_direct_err  where prod_line='AutoLine1' and coll_type='flashburn' and time_day='2020-04-26'"
                #     log.info("debug:" + sql)
                #     cur.execute(sql)
                #     row = cur.fetchone()
                #     if row:
                #         sql = "update yw_project_collect_info_direct_err set prod_num='%s',prod_direct_num='%s' where prod_line='AutoLine1' " \
                #               "and station='14843' and time_day='2020-04-26'" % (row[0],row[0]-35)
                #         log.info("debug:" + sql)
                #         cur.execute(sql)
                # except Exception as ex:
                #     log.info("debug" + str(ex))

                mysql_conn.commit()

            #统计抄表工站列表
            sql = "select distinct Platform_Num from yw_project_meterread_test_info t  " \
                  "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                  "and t.prod_line='%s'" % ( this_time_day, db_orderid, db_prodline )
            log.info("统计抄表工站列表:" + sql)
            cur.execute(sql)
            rows = cur.fetchall()
            for item in rows:
                db_station = item[0]

                # 统计抄表的一次直通数量
                sql = "select count(1) from yw_project_meterread_test_info t " \
                      "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                      "and t.prod_line='%s' and Platform_Num='%s' and Test_Result='Pass' and Board_SN not in  " \
                      "( select  Board_SN from yw_project_meterread_test_info_his h where DATE_FORMAT(h.insert_date,'%%Y-%%m-%%d')='%s' " \
                      "and h.Batch_Num='%s' and h.prod_line='%s'  " \
                      ")" % ( this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计抄表的一次直通数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    direct_num = row[0]
                else:
                    direct_num = 0

                # 统计抄表的总数量
                sql = "select count(distinct Board_SN) from yw_project_meterread_test_info t " \
                      "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')='%s' and t.Batch_Num='%s' " \
                      "and t.prod_line='%s' and Platform_Num='%s'  " \
                      % ( this_time_day, db_orderid, db_prodline, db_station )
                log.info("统计抄表的总数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    prod_num = row[0]
                else:
                    prod_num = 0

                # 统计抄表的最终失败数量
                sql = "select count(1) from yw_project_meterread_test_info where DATE_FORMAT(insert_date,'%%Y-%%m-%%d')='%s' " \
                      "and  Batch_Num='%s' and  prod_line='%s' and Platform_Num='%s' and Test_Result!='Pass' " \
                      % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计抄表的不良数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    err_num = row[0]
                else:
                    err_num = 0

                # 登记数据统计信息
                if not DataExists( 'meterread'):
                    sql = "insert into yw_project_collect_info_direct_err(coll_date,order_id,prod_line,time_day,station," \
                          "coll_type, prod_num,prod_direct_num, prod_err_num) " \
                          "values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_orderid, db_prodline,
                           this_time_day, db_station, 'meterread', prod_num, direct_num, err_num)
                else:
                    sql = "update yw_project_collect_info_direct_err set coll_date='%s', prod_num='%s',prod_direct_num='%s', prod_err_num='%s' " \
                          "where order_id='%s' and  prod_line='%s' and time_day='%s' and station='%s' and prod_line='%s' " % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prod_num, direct_num, err_num,
                           db_orderid, db_prodline, this_time_day, db_station, 'meterread')
                log.info("抄表数据收集:" + sql)
                # 执行SQL并commit
                cur.execute(sql)
                mysql_conn.commit()

            # 统计各工位扣壳总数量
            sql = "select distinct win_id  from yw_project_snid_detail t  " \
                  "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                  "and t.prod_line='%s' " % (this_time_day, db_orderid, db_prodline)
            log.info("统计扣壳的工站列表:" + sql)
            cur.execute(sql)
            rows = cur.fetchall()
            for item in rows:
                db_station = item[0]
                # 统计扣壳的一次直通数量
                sql = "select count(1) from ( select pcb_sn from yw_project_snid_detail_his h  " \
                      "where DATE_FORMAT(h.tran_date,'%%Y-%%m-%%d')='%s' and h.order_id='%s' " \
                      "and h.prod_line='%s' and win_id='%s' group by pcb_sn having count(1)=1 ) t" \
                      % ( this_time_day, db_orderid, db_prodline, db_station )
                log.info("统计扣壳的一次直通数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    direct_num = row[0]
                else:
                    direct_num = 0

                #统计扣壳的总数量
                sql = "select count(distinct pcb_sn) from yw_project_snid_detail t  " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                      "and t.prod_line='%s' and win_id='%s'" % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计扣壳的总数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    prod_num = row[0]
                else:
                    prod_num = 0

                # 统计扣壳的最终失败数量
                sql = "select count(distinct pcb_sn) from yw_project_snid_detail_error t " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                      "and t.prod_line='%s' and win_id='%s' and pcb_sn not in  " \
                      "( select pcb_sn from yw_project_snid_detail h where DATE_FORMAT(h.tran_date,'%%Y-%%m-%%d')='%s' " \
                      "and h.order_id='%s' and h.prod_line='%s' )" \
                      % (this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计扣壳的不良数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    err_num = row[0]
                else:
                    err_num = 0

                # 登记数据统计信息
                if not DataExists('egsnid'):
                    sql = "insert into yw_project_collect_info_direct_err(coll_date,order_id,prod_line,time_day,station," \
                          "coll_type, prod_num,prod_direct_num, prod_err_num) " \
                          "values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_orderid, db_prodline,
                           this_time_day, db_station, 'egsnid', prod_num, direct_num, err_num)
                else:
                    sql = "update yw_project_collect_info_direct_err set coll_date='%s', prod_num='%s',prod_direct_num='%s', prod_err_num='%s' " \
                          "where order_id='%s' and  prod_line='%s' and time_day='%s' and station='%s' and prod_line='%s' " % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prod_num, direct_num, err_num,
                           db_orderid, db_prodline, this_time_day, db_station,'egsnid')
                log.info("扣壳数据收集:" + sql)
                # 执行SQL并commit
                cur.execute(sql)
                mysql_conn.commit()

            # 统计装箱的工站列表
            sql = "select win_id, count(1) from yw_project_boxing_info t  " \
                  "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                  "and t.prod_line='%s' group by win_id" % (this_time_day, db_orderid, db_prodline)
            log.info("统计装箱的工站列表:" + sql)
            cur.execute(sql)
            rows = cur.fetchall()
            for item in rows:
                db_station = item[0]
                # 统计装箱的一次直通数量
                sql = "select count(1) from yw_project_boxing_info t " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                      "and t.prod_line='%s' and win_id='%s' and state='1' and model_id not in  " \
                      "( select model_id from yw_project_boxing_info_his h where DATE_FORMAT(h.tran_date,'%%Y-%%m-%%d')='%s' " \
                      " and h.order_id='%s' and h.prod_line='%s' )" \
                      % (this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计装箱的一次直通数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    direct_num = row[0]
                else:
                    direct_num = 0

                # 统计装箱的总数量
                sql = "select count(1) from yw_project_boxing_info t " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                      "and t.prod_line='%s' and win_id='%s' and state='1' " \
                      % (this_time_day, db_orderid, db_prodline, db_station)
                log.info("统计装箱的总数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    prod_num = row[0]
                else:
                    prod_num = 0

                # 统计装箱的最终失败数量
                sql = "select count(distinct model_id) from yw_project_boxing_info_error t " \
                      "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')='%s' and t.order_id='%s' " \
                      "and t.prod_line='%s' and win_id='%s' and model_id not in  " \
                      "( select model_id from yw_project_boxing_info h where DATE_FORMAT(h.tran_date,'%%Y-%%m-%%d')='%s' " \
                      " and h.order_id='%s' and h.prod_line='%s' )" \
                      % (this_time_day, db_orderid, db_prodline, db_station, this_time_day, db_orderid, db_prodline)
                log.info("统计装箱的不良数量:" + sql)
                cur.execute(sql)
                row = cur.fetchone()
                if row:
                    err_num = row[0]
                else:
                    err_num = 0

                # 登记数据统计信息
                if not DataExists('box'):
                    sql = "insert into yw_project_collect_info_direct_err(coll_date,order_id,prod_line,time_day,station," \
                          "coll_type, prod_num,prod_direct_num, prod_err_num) " \
                          "values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), db_orderid, db_prodline,
                           this_time_day, db_station, 'box', prod_num, direct_num, err_num)
                else:
                    sql = "update yw_project_collect_info_direct_err set coll_date='%s',prod_num='%s',prod_direct_num='%s', prod_err_num='%s' " \
                          "where order_id='%s' and  prod_line='%s' and time_day='%s' and station='%s' and prod_line='%s' " % \
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prod_num, direct_num, err_num,
                           db_orderid, db_prodline, this_time_day, db_station, 'box')
                log.info("装箱数据收集:" + sql)
                # 执行SQL并commit
                cur.execute(sql)
                mysql_conn.commit()
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
        log, fh = loger_init()
        try:
            log.info('-'*60)
            deal_collect()
            log.info('-' * 60)
        except Exception as ex:
            log.error("MySql数据库连接失败!"+str(ex), exc_info=True)
        finally:
            if fh:
                fh.close()
                log.removeHandler(fh)
        time.sleep(20) #每两分钟处理一次
