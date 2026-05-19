# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#统计直通率数据收集,每月质控需要
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

#每小时产量数据收集,各工站第一次操作成功的
def total_collect2( prodline, start_date, end_date ):
    #日志文件初始化
    log, fh = loger_init()
    log.info('直通率统计!')
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

    # 开始统计
    try:
        print('%s -- %s - %s 直通率计算：' % (prodline, start_date, end_date) )
        sql = "select count(1) from (select min(id),Board_SN,Test_Result from yw_project_product_test_info_his " \
              "where DATE_FORMAT(insert_date,'%%Y-%%m-%%d')>='%s' and DATE_FORMAT(insert_date,'%%Y-%%m-%%d')<='%s' " \
              "and prod_line='%s' group by Board_SN ) temp " \
              "where Test_Result!='Pass'  "  % (start_date, end_date, prodline )
        log.info("产测第一次失败数量:"+sql)
        cur.execute(sql)
        row = cur.fetchone()
        prodtest_firsterr_num = row[0]
        print('产测第一次失败数量:', prodtest_firsterr_num)

        sql = "select count( DISTINCT t.Board_SN ) from yw_project_product_test_info t " \
              "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')>='%s' and  DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')<='%s' " \
              "and t.prod_line='%s'"  \
              % (start_date, end_date, prodline)
        log.info("产测投产总数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        prodtest_all_num = row[0]
        print('产测投产总数量:', prodtest_all_num)
        if prodtest_all_num > prodtest_firsterr_num:
            prodtest_direct_rate = ((prodtest_all_num-prodtest_firsterr_num)/prodtest_all_num)*100
        else:
            prodtest_direct_rate = 100
        print('产测直通率:', prodtest_direct_rate)
######################################################################################################################################################
        sql = "select count(1) from (select min(id),Board_SN,Test_Result from yw_project_meterread_test_info_his " \
              "where DATE_FORMAT( insert_date,'%%Y-%%m-%%d')>='%s' and DATE_FORMAT( insert_date,'%%Y-%%m-%%d')<='%s'" \
              " and prod_line='%s' group by Board_SN ) temp " \
              "where Test_Result!='Pass'  "  % (start_date, end_date, prodline )
        log.info("抄表第一次失败数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        meterread_firsterr_num = row[0]
        print('抄表第一次失败数量:', meterread_firsterr_num)

        sql = "select count( DISTINCT t.Board_SN ) from yw_project_meterread_test_info t " \
              "where DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')>='%s' and DATE_FORMAT(t.insert_date,'%%Y-%%m-%%d')<='%s' " \
              "and t.prod_line='%s' " % (start_date, end_date, prodline)
        log.info("抄表投产总数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        meterread_all_num = row[0]
        print('抄表投产总数量:', meterread_all_num)
        if meterread_all_num > meterread_firsterr_num:
            meterread_direct_rate = ( (meterread_all_num-meterread_firsterr_num) / meterread_all_num) * 100
        else:
            meterread_direct_rate = 100
        print('抄表直通率:', meterread_direct_rate)
######################################################################################################################################################
        sql = "select count(DISTINCT pcb_sn) from yw_project_snid_detail_error where DATE_FORMAT(tran_date,'%%Y-%%m-%%d')>='%s' " \
              "and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')<='%s' and prod_line='%s' " % (start_date, end_date, prodline )
        log.info("装壳第一次失败数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        snid_firsterr_num = row[0]
        print('装壳第一次失败数量:', snid_firsterr_num)

        sql = "select count( DISTINCT t.pcb_sn ) from yw_project_snid_detail t  " \
              "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')>='%s' and DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')<='%s' " \
              "and t.prod_line='%s'" % (start_date, end_date, prodline)
        log.info("装壳投产总数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        snid_all_num = row[0]
        print('装壳投产总数量:', snid_all_num)
        if snid_all_num > snid_firsterr_num:
            snid_direct_rate = ( (snid_all_num - snid_firsterr_num) / snid_all_num) * 100
        else:
            snid_direct_rate = 100
        print('装壳直通率:', snid_direct_rate)

######################################################################################################################################################
        sql = "select count(DISTINCT model_id) from yw_project_boxing_info_error where DATE_FORMAT(tran_date,'%%Y-%%m-%%d')>='%s' " \
              " and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')<='%s' and prod_line='%s' " % (start_date, end_date, prodline )

        # sql = "select count(DISTINCT model_id) from yw_project_boxing_info_error where DATE_FORMAT(tran_date,'%%Y-%%m')='%s' " \
        #       " and DATE_FORMAT(tran_date,'%%Y-%%m-%%d')<='%s' and prod_line='%s' " % (start_date, end_date, prodline)
        log.info("装箱第一次失败数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        box_firsterr_num = row[0]
        print('装箱第一次失败数量:', box_firsterr_num)

        sql = "select count( DISTINCT t.model_id ) from yw_project_boxing_info t  " \
              "where DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')>='%s' and DATE_FORMAT(t.tran_date,'%%Y-%%m-%%d')<='%s' " \
              "and t.prod_line='%s' " % (start_date, end_date, prodline)
        log.info("装箱投产总数量:" + sql)
        cur.execute(sql)
        row = cur.fetchone()
        box_all_num = row[0]
        print('装箱投产总数量:', box_all_num)
        if box_all_num > box_firsterr_num:
            box_direct_rate = ( (box_all_num-box_firsterr_num) / box_all_num)*100
        else:
            box_direct_rate = 100
        print('装箱直通率:', box_direct_rate)
######################################################################################################################################################

        total_direct_rate = prodtest_direct_rate * meterread_direct_rate * snid_direct_rate  * box_direct_rate
        print('直通率相乘:', round(total_direct_rate/1000000, 4))

        log.info("---------------一次直通率数据收集完毕!-----------------")
    except Exception as e:
        log.error("MySql数据库处理失败!" +str(e), exc_info = True )
        return -1
    finally:
        cur.close()
        # 关闭链接
        mysql_conn.close()
        log.info('收集每小时产量数据结束!')
#
# # 每小时产量数据收集,各工站只操作一次的成功的
# def total_collect(prodline):
#     # 日志文件初始化
#     log, fh = loger_init()
#     log.info('直通率统计!')
#     try:
#         mysql_conn = pymysql.Connect(
#             host='192.168.2.174',
#             port=3306,
#             user='lqkj',
#             passwd='LQkj666_2019',
#             db='lqkj_db',
#             charset='utf8')
#         cur = mysql_conn.cursor()
#     except Exception as e:
#         log.error("MySql数据库连接失败!" + str(e), exc_info=True)
#         return -1
#
#     # 统计上月的直通率
#     mouth_value = '2020-05'
#     # 开始统计
#     try:
#         print('%s -- %s 直通率计算：' % (prodline, mouth_value))
#         sql = "select count( DISTINCT t.Board_SN ) from yw_project_product_test_info t " \
#               "where DATE_FORMAT(t.insert_date,'%%Y-%%m')='%s' and t.Test_Result='Pass' and t.Aging_Test_Period='Before' and t.prod_line='%s' " \
#               "and not EXISTS ( select 1 from yw_project_product_test_info_his h where t.Board_SN=h.Board_SN  " \
#               "and DATE_FORMAT(h.insert_date,'%%Y-%%m')='%s' and h.Test_Result!='Pass' and h.Aging_Test_Period='Before' and h.prod_line='%s' )" \
#               % (mouth_value, prodline, mouth_value, prodline)
#         log.info("产测老化前一次直通数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         prodtest_direct_num = row[0]
#         print('产测老化前一次直通数量:', prodtest_direct_num)
#
#         sql = "select count( DISTINCT t.Board_SN ) from yw_project_product_test_info t " \
#               "where DATE_FORMAT(t.insert_date,'%%Y-%%m')='%s' and t.Aging_Test_Period='Before' and t.prod_line='%s'" \
#               % (mouth_value, prodline)
#         log.info("产测老化前投产总数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         prodtest_all_num = row[0]
#         print('产测老化前投产总数量:', prodtest_all_num)
#         prodtest_direct_rate = (prodtest_direct_num / prodtest_all_num) * 100
#         print('产测老化前直通率:', prodtest_direct_rate)
#         ######################################################################################################################################################
#         sql = "select count( DISTINCT t.Board_SN ) from yw_project_meterread_test_info t  " \
#               "where DATE_FORMAT(t.insert_date,'%%Y-%%m')='%s' and t.Test_Result='Pass'  and t.prod_line='%s' " \
#               "and not EXISTS ( select 1 from yw_project_meterread_test_info_his h where t.Board_SN=h.Board_SN  " \
#               "and DATE_FORMAT(h.insert_date,'%%Y-%%m')='%s'and h.Test_Result!='Pass'  and h.prod_line='%s'  )" \
#               % (mouth_value, prodline, mouth_value, prodline)
#         log.info("抄表一次直通数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         meterread_direct_num = row[0]
#         print('抄表一次直通数量:', meterread_direct_num)
#
#         sql = "select count( DISTINCT t.Board_SN ) from yw_project_meterread_test_info t " \
#               "where DATE_FORMAT(t.insert_date,'%%Y-%%m')='%s' and t.prod_line='%s' " % (mouth_value, prodline)
#         log.info("抄表投产总数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         meterread_all_num = row[0]
#         print('抄表投产总数量:', meterread_all_num)
#         meterread_direct_rate = (meterread_direct_num / meterread_all_num) * 100
#         print('抄表直通率:', meterread_direct_rate)
#         ######################################################################################################################################################
#
#         sql = "select count(DISTINCT t.pcb_sn) from yw_project_snid_detail t  " \
#               "where DATE_FORMAT(t.tran_date,'%%Y-%%m')='%s' and t.prod_line='%s' and t.state='1' and not EXISTS " \
#               "( select 1 from yw_project_snid_detail_his h where t.pcb_sn=h.pcb_sn " \
#               "and DATE_FORMAT(h.tran_date,'%%Y-%%m')='%s'  and h.state!='1' and h.prod_line='%s')" \
#               % (mouth_value, prodline, mouth_value, prodline)
#         log.info("装壳一次直通数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         snid_direct_num = row[0]
#         print('装壳一次直通数量:', snid_direct_num)
#
#         sql = "select count( DISTINCT t.pcb_sn ) from yw_project_snid_detail t  " \
#               "where DATE_FORMAT(t.tran_date,'%%Y-%%m')='%s' and t.prod_line='%s'" % (mouth_value, prodline)
#         log.info("装壳投产总数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         snid_all_num = row[0]
#         print('装壳投产总数量:', snid_all_num)
#         if snid_all_num > 0:
#             snid_direct_rate = (snid_direct_num / snid_all_num) * 100
#             print('装壳直通率:', snid_direct_rate)
#         else:
#             snid_direct_rate = 100
#             ######################################################################################################################################################
#
#         sql = "select count(DISTINCT t.pcb_sn) from yw_project_boxing_info t  " \
#               "where DATE_FORMAT(t.tran_date,'%%Y-%%m')='%s' and t.prod_line='%s' and t.state='1' and not EXISTS " \
#               "( select 1 from yw_project_boxing_info_his h where t.pcb_sn=h.pcb_sn " \
#               "and DATE_FORMAT(h.tran_date,'%%Y-%%m')='%s'  and h.state='1' and h.prod_line='%s' )" \
#               % (mouth_value, prodline, mouth_value, prodline)
#         log.info("装箱一次直通数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         box_direct_num = row[0]
#         print('装箱一次直通数量:', box_direct_num)
#
#         sql = "select count( DISTINCT t.pcb_sn ) from yw_project_boxing_info t  " \
#               "where DATE_FORMAT(t.tran_date,'%%Y-%%m')='%s' and t.prod_line='%s' " % (mouth_value, prodline)
#         log.info("装箱投产总数量:" + sql)
#         cur.execute(sql)
#         row = cur.fetchone()
#         box_all_num = row[0]
#         print('装箱投产总数量:', box_all_num)
#         box_direct_rate = (box_direct_num / box_all_num) * 100
#         print('装箱直通率:', box_direct_rate)
#         ######################################################################################################################################################
#
#         total_direct_rate = prodtest_direct_rate * meterread_direct_rate * snid_direct_rate * box_direct_rate
#         print('直通率相乘:', round(total_direct_rate / 1000000, 4))
#
#         log.info("---------------一次直通率数据收集完毕!-----------------")
#     except Exception as e:
#         log.error("MySql数据库处理失败!" + str(e), exc_info=True)
#         return -1
#     finally:
#         cur.close()
#         # 关闭链接
#         mysql_conn.close()
#         log.info('收集每小时产量数据结束!')
#

#持续运行
if __name__ == '__main__':

    log, fh = loger_init()
    try:
        log.info( '-' * 60 )
        total_collect2('AutoLine1', '2020-05-01', '2020-05-31'  )
        total_collect2('ManLine1', '2020-05-01', '2020-05-31')
        total_collect2('ManLine2', '2020-05-01', '2020-05-31')
        total_collect2('ManLine3', '2020-05-01', '2020-05-31')
        log.info( '-' * 60 )
    except Exception as ex:
        log.error("数据处理失败!"+str(ex), exc_info=True)
    finally:
        if fh:
            fh.close()
            log.removeHandler(fh)

