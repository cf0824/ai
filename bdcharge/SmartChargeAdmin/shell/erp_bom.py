#通过采购给的excel补全焊点数量, 不支持xls格式

import openpyxl
import pymssql


def duemain():
    try:

        sqlserver_conn = pymssql.connect(server='192.168.2.18',
                                         user='sa',
                                         password='luyao123KEJI',
                                         database="db_18",
                                         timeout=20,
                                         autocommit=True)  # sqlserver数据库链接句柄
        cursor = sqlserver_conn.cursor()  # 获取光标

        sql = "select TF_BOM.BOM_NO,TF_BOM.ID_NO from TF_BOM where prd_no='319100087'"
        print(sql)
        cursor.execute(sql)
        rows=cursor.fetchall()
        # print(rows)
        for item1 in rows:
            print('第一层：',item1)
            updsql="update MF_BOM set END_DD='2019-10-17 00:00:00.000' where BOM_NO='%s'" %  item1[0]
            print(updsql)
            cursor.execute(updsql)

            sql = " select BOM_NO,ID_NO from TF_BOM where ID_NO = '%s'" % item1[0]
            # print(sql)
            cursor.execute(sql)
            rows2=cursor.fetchall()
            for item2 in rows2:
                print('第二层：',item2)
                updsql = "update MF_BOM set END_DD='2019-10-17 00:00:00.000' where BOM_NO='%s'" % item2[0]
                print(updsql)
                cursor.execute(updsql)

                sql = " select BOM_NO,ID_NO from TF_BOM where ID_NO = '%s'" % item2[0]
                # print(sql)
                cursor.execute(sql)
                rows3 = cursor.fetchall()
                for item3 in rows3:
                    print('第三层：',item3)
                    updsql = "update MF_BOM set END_DD='2019-10-17 00:00:00.000' where BOM_NO='%s'" % item3[0]
                    print(updsql)
                    cursor.execute(updsql)
                    # sql = " select BOM_NO,ID_NO from TF_BOM where ID_NO = '%s'" % item3[0]
                    # # print(sql)
                    # cursor.execute(sql)
                    # rows4 = cursor.fetchall()
                    # for item4 in rows4:
                    #     print('第四层：', item4)
                    #     sql = " select BOM_NO,ID_NO from TF_BOM where ID_NO = '%s'" % item4[0]
                    #     # print(sql)
                    #     cursor.execute(sql)
                    #     rows5 = cursor.fetchall()
                    #     for item5 in rows5:
                    #         print('第五层：', item5)

        sqlserver_conn.commit()
        sqlserver_conn.close()
    except Exception as e:
        print(e)
        sqlserver_conn.close()


duemain()
