# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import datetime

import pymssql
import pymysql

#获取带PSRAM的所有品号
def psram_info():
    try:
        sqlserver_conn = pymssql.connect(server='192.168.2.18', user='sa', password='luyao123KEJI', database="db_18", timeout=20, autocommit=True)  # sqlserver数据库链接句柄
    except:
        print('连接ERP数据库失败')
    try:
        mysql_conn = pymysql.Connect( host='192.168.2.174', port=3306, user='lqkj', passwd='LQkj666_2019', db='lqkj_db', charset='utf8')
    except:
        print('连接OA数据库失败')

    #先获取本次处理时间
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur = mysql_conn.cursor()

    cursor = sqlserver_conn.cursor()  # 获取光标
    prdno = '306CS0021'
    sql="select BOM_NO from TF_BOM where prd_no='%s' " \
        "union " \
        " select BOM_NO from TF_BOM where ID_NO in " \
        "(select BOM_NO from TF_BOM where prd_no='%s')" % (prdno, prdno)

    print('获取带PSRAM的所有品号：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        if item[0]==None:
            continue
        else:
            bomno = item[0]
        prodno=bomno.split('->')[0]
        # print('prodno=',prodno)

        #根据prodno获取是否是集中器
        sql = "select name from prdt where prd_no='%s'" % prodno
        # print(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        prodname=row[0]
        if 'CCO' in prodname or 'cco' in prodname or '集中器' in prodname:
            continue

        # print('prodno=', prodno, 'prodname=', prodname)
        i=i+1

        #获取在途数量
        sql = "select QTY_ON_PRC,QTY_ON_RSV,QTY from prdt1 where prd_no='%s'" % prodno
        # print(sql)
        cursor.execute(sql)
        subrows = cursor.fetchall()
        qty_on_prc = 0
        qty_on_rsv = 0
        qty_now = 0
        for subitem in subrows:
            qty_on_prc = qty_on_prc + int(subitem[0])
            qty_on_rsv = qty_on_rsv + int(subitem[1])
            qty_now = qty_now + int(subitem[2])

        # if qty_on_prc >0 or qty_on_rsv >0 or qty_now > 0:
        #     print( bomno, ',' ,prodno, ',', prodname, ',', qty_on_prc, ',', qty_on_rsv, ',', qty_now)
        # else:
        #     print(bomno, ',' ,prodno, ',', prodname, ',', qty_on_prc, ',', qty_on_rsv, ',', qty_now)
        print(bomno, ',', prodno, ',', prodname, ',', qty_on_prc, ',', qty_on_rsv, ',', qty_now)

        #更新BOM停用日期为今天
        #根据prodno获取是否是集中器
        sql = "update MF_BOM set END_DD='2019-12-31 00:00:00.000' where BOM_NO='%s'" % bomno
        cursor.execute(sql)
    print("due num:"+str(i))


    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()



psram_info()  #获取带PSRAM的所有品号

