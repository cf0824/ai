# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import datetime

import pymssql
import pymysql

#扫码配对工装登记扫码信息
def deal_match():
    sqlserver_conn = pymssql.connect(server='192.168.2.222', user='sa', password='Lqiot.com', database="lq_hplc", timeout=20, autocommit=True)#sqlserver数据库链接句柄
    mysql_conn = pymysql.Connect(
        host='192.168.2.174',
        port=3306,
        user='lqkj',
        passwd='LQkj666_2019',
        db='lqkj_db',
        charset='utf8')
    jhid='JH1908A019'

    #先获取本次处理时间
    thisduetime=datetime.datetime.now()

    cur = mysql_conn.cursor()

    #获取上一次处理的时间
    sql = "select last_time from yw_project_snid_sync where type='sqlserver'"
    cur.execute(sql)
    row = cur.fetchone()
    lasttime=row[0]
    #print(lasttime)

    #获取数据
    sql = "select * from yw_project_snid_detail where state='1' and pcb_sn like 'ff4132%'"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标
    cursor.execute("truncate table T_RealTimeProduceMX_temp")

    i=0
    for item in rows:
        #print(item)
        i=i+1
        if i%10 == 0:
            print(i)

        updsql = "update top (1) t_barcode set bc_shellcode = '%s', bc_chipid  = '%s', bc_zhuangkedatetime = getdate(), bc_productionstatus = '20' where bc_barcode = '%s'"
        sql = "BEGIN TRANSACTION;" + updsql % (item[6], item[7], item[5]) +  ";COMMIT TRANSACTION;"
        #print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(str(e))
            continue

        inssql = "INSERT INTO T_RealTimeProduceMX_temp(rtpnmx_datetime,rtpnmx_status,rtpnmx_code, rj_jihuadanhao) VALUES(GETDATE(), '20', '%s', '%s')"
        sql = "BEGIN TRANSACTION;" + inssql % (item[6], jhid) + ";COMMIT TRANSACTION;"
        #print(sql)
        cursor.execute(sql)

    print("due num:"+str(i))
    #同步一下
    cursor.close()
    cursor = sqlserver_conn.cursor()  # 获取光标
    msql="insert into T_RealTimeProduceMX(rtpnmx_datetime,rtpnmx_status,rtpnmx_code, rj_jihuadanhao) " \
         "select a.rtpnmx_datetime,a.rtpnmx_status,a.rtpnmx_code, a.rj_jihuadanhao from T_RealTimeProduceMX_temp a " \
         "where not exists  (select 1 from T_RealTimeProduceMX b where a.rtpnmx_code=b.rtpnmx_code)"
    ret=cursor.execute(msql)
    print("同步结果："+str(ret))
    cursor.close()

    #更新本次处理时间
    cur = mysql_conn.cursor()
    sql = "update yw_project_snid_sync set last_time='%s' where type='sqlserver'" % thisduetime
    cur.execute(sql)
    cur.close()
    mysql_conn.commit()
    sqlserver_conn.commit()
    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()

deal_match()



