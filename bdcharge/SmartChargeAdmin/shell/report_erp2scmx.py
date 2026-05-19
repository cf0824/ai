# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import datetime

import pymssql
import pymysql

#导入有销货订单的客户信息
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

    cur = mysql_conn.cursor()
    # #获取数据
    # sql = "select * from yw_project_snid_detail where state='1' and order_id='%s' and tran_date>= '%s'" % (jhid,lasttime)
    # print(sql)
    # cur.execute(sql)
    # rows = cur.fetchall()
    # cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标
    sql="select nsr_code,name,cus_no,cus_level,CONVERT(varchar(100),modify_dd, 120) from cust where exists " \
        "( select 1 from MF_POS where cust.cus_no=mf_pos.cus_no and OS_ID='SO' and CANCEL_ID is null )"
    print('有销货订单的客户信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        if item[0]==None:
            nsrcode = item[2]
        else:
            nsrcode = item[0]
        cusname = item[1]
        cusno = item[2]
        cuslevel = item[3]
        if item[4]==None:
            cusdd = nowTime
        else:
            cusdd = item[4]

        # 插入OA系统客户信息表
        sql = "insert into yw_rece2_customer_info(cre_id,cus_name,cus_code,cus_rank,cus_tran_date,cus_enter_person,state) " \
              " values('%s','%s','%s','%s','%s','57','1')" \
              % (nsrcode, cusname, cusno, cuslevel, cusdd)
        print(sql)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()


#导入订单信息
def order_info():
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
    # #获取数据
    # sql = "select * from yw_project_snid_detail where state='1' and order_id='%s' and tran_date>= '%s'" % (jhid,lasttime)
    # print(sql)
    # cur.execute(sql)
    # rows = cur.fetchall()
    # cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标
    sql="select CONVERT(varchar(100),OS_DD, 120),OS_NO,CUS_NO,CHK_DAYS,SAL_NO,REM" \
        " from MF_POS where OS_ID='SO' and CANCEL_ID is null and OS_DD >= '2019-01-01 00:00:00.000'"
    print('查询订单信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        osdd = item[0]
        osno = item[1]
        cusno = item[2]
        chkdays = item[3]
        if item[4]==None:
            salno = ''
        else:
            salno = item[4]
        if item[5]==None:
            rem = ''
        else:
            rem = item[5]

        #获取销货总金额
        sql = "select sum(AMT) from TF_POS where OS_NO='%s'" % osno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row[0]==None:
            totalmoney = 0
        else:
            totalmoney=row[0]
        # print(osdd, osno, cusno, chkdays, salno, totalmoney)

        #根据客户号获取其组织机构代码证
        sql = "select NSR_CODE from CUST where CUS_NO ='%s'" % cusno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row==None or row[0]==None:
            nsrcode = cusno
        else:
            nsrcode = row[0]

        # 根据订单号获取已销货金额
        sql = "select sum(AMT) from TF_PSS where  OS_NO='%s'" % osno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row == None or row[0] == None:
            sendamount = 0.00  # 已发货金额
        else:
            sendamount = row[0]

        # 插入OA系统销售订单表
        sql = "insert into yw_rece2_order_info(order_tran_date,order_upd_date,order_enter_person,order_sal_id,order_cre_id,order_id, order_amount," \
              "order_paytype,send_amount, order_assperiod, order_remarks, order_state) " \
              "values('%s','%s','57','%s','%s','%s','%s','2', '%s', '%s','%s', '1')" \
              % (osdd, nowTime, salno, nsrcode, osno, totalmoney, sendamount, chkdays, rem)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()

#导入发货信息
def sentoutgoods_info():
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
    # #获取数据
    # sql = "select * from yw_project_snid_detail where state='1' and order_id='%s' and tran_date>= '%s'" % (jhid,lasttime)
    # print(sql)
    # cur.execute(sql)
    # rows = cur.fetchall()
    # cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标
    # sql="select os_no,CONVERT(varchar(100),ps_dd, 120),ps_no,sum(amt) from TF_PSS where PS_ID in ('SA','SB','SD') and exists " \
    #     " ( select 1 from MF_POS where TF_PSS.os_no=mf_pos.os_no and CANCEL_ID is null) and PS_DD >= '2019-01-01 00:00:00.000' " \
    #     " group by os_no,ps_dd,ps_no"

    # sql="select os_no,CONVERT(varchar(100),ps_dd, 120),ps_no,sum(amt) from TF_PSS where PS_ID='SA' and exists " \
    #     " ( select 1 from MF_POS where TF_PSS.os_no=mf_pos.os_no and OS_ID='SO' and CANCEL_ID is null) and PS_DD >= '2019-01-01 00:00:00.000' " \
    #     "  and exists (select 1 from MF_PSS where TF_PSS.os_no=MF_PSS.os_no and cus_no='K021')" \
    #     "  group by os_no,ps_dd,ps_no"

    sql="select a.os_no, CONVERT(varchar(100),a.ps_dd, 120),a.ps_no,a.amt,b.cus_no, a.ps_id from TF_PSS a, MF_PSS b " \
        " where a.PS_NO=b.PS_NO and a.PS_ID in ('SA','SB','SD')"
    print('查询发货信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        osno = item[0]
        psdd = item[1]
        psid = item[5]
        if item[3]==None:
            sendmoney = 0
        else:
            if psid in ('SB','SD'):
                sendmoney = item[3] * -1
            else:
                sendmoney = item[3]
        cusno=item[4]

        # 根据客户号获取其组织机构代码证
        sql = "select NSR_CODE from CUST where CUS_NO ='%s'" % cusno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row == None or row[0] == None:
            nsrcode = cusno
        else:
            nsrcode = row[0]

        # 根据订单号获取其对应的账期
        sql = "select distinct b.nsr_code,a.chk_days from MF_PSS a, cust b where a.cus_no=b.cus_no and a.OS_NO='%s'" % osno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row==None or row[1] == None:
            chkdays = 0
        else:
            chkdays = row[1]

        # 插入OA系统销售订单表
        sql = "insert into yw_rece2_order_info_sub(order_tran_date,order_upd_date,order_enter_person,cre_id,order_id, order_amount," \
              "order_assperiod, send_date, order_state) " \
              "values('%s','%s','57','%s','%s','%s','%s','%s', '1')" \
              % (psdd, nowTime, nsrcode, osno, sendmoney, chkdays, psdd)
        # print(sql)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))
    mysql_conn.commit()

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()
#导入发货信息完成

#导入发票信息
def bill_info():
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
    sql="select a.inv_no,CONVERT(varchar(100),a.inv_dd, 120),a.cus_no,a.amt,b.lz_no" \
        " from inv_no a, mf_lz b where a.bil_no=b.lz_no and a.cancel_dd is null and INV_DD >= '2019-01-01 00:00:00.000'"
    print('查询发票信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        invno = item[0]
        invdd = item[1]
        cusno= item[2]
        if item[3]==None:
            billmoney = 0.00
        else:
            billmoney=item[3]
        lzno=item[4]

        # 根据客户号获取其组织机构代码证
        sql = "select NSR_CODE from CUST where CUS_NO ='%s'" % cusno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row == None or row[0] == None:
            nsrcode = cusno
        else:
            nsrcode = row[0]

        #根据立账号获取其关联的订单号
        sql = "select a.OS_NO, sum(b.amt) from MF_PSS a, TF_LZ b  " \
              " where a.PS_NO=b.CK_NO and a.PS_ID in ('SA','SB','SD') and b.LZ_NO='%s' group by a.os_no " % lzno
        cursor.execute(sql)
        subrows = cursor.fetchall()
        glddh=''
        billmoney=0
        for subitem in subrows:
            temp = subitem[0]
            if '-' in temp:
                temp = str(temp).strip('-')[0]
            if temp in glddh:
                continue
            if glddh == '':
                glddh = temp
            else:
                glddh = glddh + ',' + temp
            billmoney = billmoney + float(subitem[1])

        # 插入OA系统销售订单表
        sql = "insert into yw_rece2_invoice_info(code_tran_date,code_upd_date,code_enter_person,cre_id,code_pay_type,code_num," \
              "code_date, order_assperiod, code_amo_money, code_annex, con_order_id, code_state) " \
              "values('%s','%s','57','%s','支票','%s','%s','%s','%s','%s', '1')" \
              % (invdd, nowTime, nsrcode, invno, invdd, '0', billmoney, lzno, glddh)
        print(sql)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()
#导入发票信息完成

#导入回款信息
def return_info():
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
    # #获取数据
    # sql = "select * from yw_project_snid_detail where state='1' and order_id='%s' and tran_date>= '%s'" % (jhid,lasttime)
    # print(sql)
    # cur.execute(sql)
    # rows = cur.fetchall()
    # cur.close()

    cursor = sqlserver_conn.cursor()  # 获取光标
    sql="select b.rp_no,b.cus_no,CONVERT(varchar(100),b.rp_dd, 120), b.amtn_cls,a.lz_no " \
        "from MF_LZ a, TC_MON b where a.arp_no=b.arp_no and RP_DD>= '2019-01-01 00:00:00.000'"
    print('查询回款信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        rpno = item[0]
        cusno= item[1]
        rpdd = item[2]

        if item[3]==None:
            returnmoney = 0
        else:
            returnmoney=item[3]
        lzno=item[4]

        # 根据客户号获取其组织机构代码证
        sql = "select NSR_CODE from CUST where CUS_NO ='%s'" % cusno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row == None or row[0] == None:
            nsrcode = cusno
        else:
            nsrcode = row[0]

        #根据立账号获取其关联的订单号
        # sql = "select distinct ck_no from TF_LZ where BIL_ID='SA' and LZ_NO='%s'" % lzno
        sql = "select distinct a.OS_NO  from MF_PSS a, TF_LZ b" \
              " where a.PS_NO=b.CK_NO and a.PS_ID='SA' and a.OS_ID='SO' and b.LZ_NO='%s'" % lzno
        # print('查询回款关联的订单号',sql)
        cursor.execute(sql)
        subrows = cursor.fetchall()
        glddh=''
        for subitem in subrows:
            temp = subitem[0]
            if '-' in temp:
                temp = str(temp).strip('-')[0]
            if temp in glddh:
                continue
            if glddh=='':
                glddh=temp
            else:
                glddh=glddh + ',' + temp

        # 插入OA系统销售订单表
        sql = "insert into yw_rece2_return_info(ret_tran_date,ret_upd_date,ret_enter_person,cre_id,ret_pay_type,ret_num," \
              "ret_date, ret_amo_money, ret_annex, con_order_id, ret_state) " \
              "values('%s','%s','57','%s','支票','%s','%s','%s','%s','%s', '1')" \
              % (rpdd, nowTime, nsrcode, rpno, rpdd, returnmoney, lzno, glddh)
        print(sql)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()
#导入回款信息完成


#导入预付款信息
def prepay_info():
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

    sql="select RP_NO,CUS_NO,CONVERT(varchar(100),RP_DD, 120), AMTN_BB, AMTN_OTHER  from TF_MON where RP_ID='1' and IRP_ID='T'"
    print('查询预付款信息：',sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    i=0#循环处理明细
    for item in rows:
        rpno = item[0]
        cusno= item[1]
        rpdd = item[2]

        if item[3]==None:
            if item[4]==None:
                prepaymoney = 0
            else:
                prepaymoney = item[4]
        else:
            prepaymoney=item[3]
        # lzno=item[4]

        # 根据客户号获取其组织机构代码证
        sql = "select NSR_CODE from CUST where CUS_NO ='%s'" % cusno
        cursor.execute(sql)
        row = cursor.fetchone()
        if row == None or row[0] == None:
            nsrcode = cusno
        else:
            nsrcode = row[0]

        glddh=''

        # 插入OA系统销售订单表
        sql = "insert into yw_rece2_return_info(ret_tran_date,ret_upd_date,ret_enter_person,cre_id,ret_pay_type,ret_num," \
              "ret_date, ret_amo_money, ret_annex, con_order_id, remarks,ret_state) " \
              "values('%s','%s','57','%s','支票','%s','%s','%s','%s','%s','预付款','1')" \
              % (rpdd, nowTime, nsrcode, rpno, rpdd, prepaymoney, '预付款', glddh)
        # print(sql)
        cur.execute(sql)
        mysql_conn.commit()

        i=i+1
        if i%10 == 0:
            print(i)
            # break

    print("due num:"+str(i))

    #关闭链接
    mysql_conn.close()
    sqlserver_conn.close()
#导入预付款信息完成

cust_info()  #导入有销货订单的客户信息
# order_info()  #导入订单信息
# sentoutgoods_info() #导入发货信息
# bill_info() #导入发票信息
# return_info() #导入回款信息
# prepay_info()   #导入预付款信息
