# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import datetime

import pymssql
import pymysql

#更新客户信息
def cust_info():
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

    cursor = sqlserver_conn.cursor()  # 获取光标
    cur = mysql_conn.cursor()

    #获取数据
    sql = "select fac_id,cre_id from yw_payable_factory_info"
    print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    i = 0
    for item in rows:
        sql = "select cus_no,cus_level from cust where nsr_code='%s' "  % item[1]
        print('查询客户号：', sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        if row and row[0]:
            sql = "update yw_payable_factory_info set fac_code='%s', fac_rank='%s' where fac_id='%s'" % (row[0], row[1], item[0])
            print('更新客户号：', sql)
            cur.execute(sql)

        i=i+1
        if i%10 == 0:
            print(i)
            # break
    cur.close()
    cursor.close()
    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()

cust_info()  #导入有销货订单的客户信息