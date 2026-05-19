# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

##########################################################################################
#扫码配对程序中mysql数据和sqlserver数据同步有问题，写个程序增强同步功能。
#litz,20190830
##########################################################################################

import time
import datetime
import pymssql
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
def deal_match():

    log, fh=loger_init( )

    try:
        sqlserver_conn = pymssql.connect(server='192.168.2.222', user='sa', password='Lqiot.com', database="lq_hplc", timeout=20, autocommit=True)#sqlserver数据库链接句柄
        cursor = sqlserver_conn.cursor()  # 获取光标
    except Exception as e:
        print("SqlServer数据库连接失败!", e)
        return  -1

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
    sql = "select * from yw_project_snid_detail_his where sync_flag='N' and sync_num<3 limit 1000"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标

    i=0
    for item in rows:
        # print(item)
        his_id=item[0]
        his_jhid=item[2]
        his_pcsn=item[5]
        his_modelid=item[6]
        his_gwid=item[7]
        # print('his_id=',his_id,'his_jhid=',his_jhid,'his_pcsn=',his_pcsn,'his_modelid=',his_modelid,'his_gwid=',his_gwid)
        i=i+1
        if i%10 == 0:
            print(i)

        #先查询是否已经同步完成
        selsql="select count(1) from T_RealTimeProduceMX where rtpnmx_status='20' and rtpnmx_code='%s' and rj_jihuadanhao='%s'"
        sql = selsql % (his_modelid, his_jhid)
        # print(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        IsExist=row[0]
        # print('IsExist=',IsExist)
        if IsExist>0:
            update_histable(mysql_conn, 'Y', '已经同步过了', his_id)
            continue

        #先更新
        updsql = "update top (1) t_barcode set bc_shellcode = '%s', bc_chipid  = '%s', bc_zhuangkedatetime = getdate(), bc_productionstatus = '20' where bc_barcode = '%s'"
        sql = "BEGIN TRANSACTION;" + updsql % (his_modelid, his_gwid, his_pcsn) +  ";COMMIT TRANSACTION;"
        print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(str(e))
            if 'unique index' in str(e):
                update_histable(mysql_conn, 'N', '芯片ID重复', his_id)
                # #找到原来出问题的芯片ID，不让装箱。
                # selsql="select bc_shellCode from  t_barcode  where bc_chipid='%s'" % his_gwid
                # cursor.execute(selsql)
                # row = cursor.fetchone()
                # old_modelid = row[0]
                #
                # # 判断原来的modelid，不允许装箱
                # updsql = "select * from T_RealTimeProduceMX where rtpnmx_status='30' and rtpnmx_code like '%%s'"
                # sql = "BEGIN TRANSACTION;" + updsql % (his_modelid, his_gwid, his_pcsn) + ";COMMIT TRANSACTION;"
                #
                # # 更新原来的modelid，不允许装箱
                # updsql = "select * from T_RealTimeProduceMX where rtpnmx_status='30' and rtpnmx_code like '%%s'"
                # sql = "BEGIN TRANSACTION;" + updsql % (his_modelid, his_gwid, his_pcsn) + ";COMMIT TRANSACTION;"
                #
                # old_modelid



            else:
                update_histable(mysql_conn, 'N',str(e), his_id)
            continue

        #插入模块表信息
        inssql = "INSERT INTO T_RealTimeProduceMX(rtpnmx_datetime,rtpnmx_status,rtpnmx_code, rj_jihuadanhao) VALUES(GETDATE(), '20', '%s', '%s')"
        sql = "BEGIN TRANSACTION;" + inssql % (his_modelid, his_jhid) + ";COMMIT TRANSACTION;"
        print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(str(e))
            update_histable(mysql_conn, 'N',str(e), his_id)
            continue

        # 再次查询是否已经同步完成
        selsql = "select count(1) from T_RealTimeProduceMX where rtpnmx_status='20' and rtpnmx_code='%s' and rj_jihuadanhao='%s'"
        sql = selsql % (his_modelid, his_jhid)
        print(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        IsExist = row[0]
        if IsExist > 0:
            update_histable(mysql_conn, 'Y', '同步成功', his_id)
        else:
            update_histable(mysql_conn, 'N', 'insert语句没报错,但对方库中无记录', his_id)

        mysql_conn.commit()
        sqlserver_conn.commit()
    print("due num:" + str(i))
    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()

def update_histable(mysql_conn, sync_flag, sync_msg, his_id):
    cur = mysql_conn.cursor()
    sql = "update yw_project_snid_detail_his set sync_num=sync_num+1, sync_flag='%s', errmsg='%s', sync_time='%s' where id='%s'" % ( sync_flag, sync_msg, datetime.datetime.now(),his_id)
    try:
        cur.execute(sql)
    except Exception as ex:
        print('update_histable error!',ex)
    cur.close()
    mysql_conn.commit()

#持续运行
if __name__ == '__main__':
    while True:
        try:
            deal_match()
        except Exception as ex:
            print(ex)

        time.sleep(5)




