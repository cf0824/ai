#通过采购给的excel补全焊点数量, 不支持xls格式

import os
import xlwt
import xlrd
from xlutils.copy import copy
import pymysql

#转换BOM文件
def changeinto(filename):
    try:
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
            print("MySql数据库连接失败!" + str(e))
            return -1

        workbook = xlrd.open_workbook(filename=filename, formatting_info=True)
        sheet1 = workbook.sheet_by_name('BOM')
        # print('sheet1名称:{}\nsheet1列数: {}\nsheet1行数: {}'.format(sheet1.name, sheet1.ncols, sheet1.nrows))
        start_row=5

        print('复制出一个新excel')
        # 复制出一个新excel
        newexcel = copy(workbook)
        print('newexcel=',newexcel)

        NewXlsName = os.path.splitext(filename)[0] + '(转联桥BOM)' + os.path.splitext(filename)[1]
        # 获取新excel的工作区
        ws = newexcel.get_sheet(0)
        for i in range(start_row,sheet1.nrows):
            description = sheet1.cell(i,1).value

            if description.strip()==None or len(description.strip())==0:
                continue
            print('description=',description)

            sql = "select distinct lqerp_desc, lqerp_prdno  from yw_lqerp_wqbom2lqbom where wq_desc='%s'" % (description)
            print(sql)
            cur.execute(sql)
            rows=cur.fetchall()
            bom_desc = ''
            bom_prdno = ''
            for item in rows:
                bom_desc = bom_desc+'\r\n'+item[0]
                bom_prdno = bom_prdno+'\r\n'+item[1]
            ws.write(i, 5, bom_desc)
            ws.write(i, 6, bom_prdno)
            print("bom_desc=",bom_desc)
        newexcel.save(NewXlsName)
        mysql_conn.commit()
        mysql_conn.close()

    except Exception as e:
        print(e)
        mysql_conn.close()

#导入BOM文件
def importfile(filename):
    try:
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
            print("MySql数据库连接失败!" + str(e))
            return -1

        workbook = xlrd.open_workbook(filename=filename)
        sheet1 = workbook.sheet_by_name('BOM')
        print('sheet1名称:{}\nsheet1列数: {}\nsheet1行数: {}'.format(sheet1.name, sheet1.ncols, sheet1.nrows))
        start_row=5

        for i in range(start_row,sheet1.nrows):
            description = sheet1.cell(i,1).value
            qty = sheet1.cell(i,2).value
            reference = sheet1.cell(i,3).value

            if str(qty).strip() == None or len(str(qty).strip()) == 0:
                pass
            else:
                tmp_qty = qty
            if reference.strip() == None or len(reference.strip()) == 0:
                pass
            else:
                tmp_reference = reference

            bom_desc = sheet1.cell(i, 5).value
            bom_prdno = sheet1.cell(i, 6).value

            if str(bom_desc).strip() == None or len(str(bom_desc).strip()) == 0:
                pass
            else:
                tmp_bom_desc = bom_desc
            if str(bom_prdno).strip() == None or len(str(bom_prdno).strip()) == 0:
                pass
            else:
                tmp_bom_prdno = bom_prdno

            if str(qty).strip() == None or len(str(qty).strip()) == 0:
                qty = tmp_qty
            if reference.strip() == None or len(reference.strip()) == 0:
                reference = tmp_reference
            if str(bom_desc).strip() == None or len(str(bom_desc).strip()) == 0:
                bom_desc = tmp_bom_desc
            if str(bom_prdno).strip() == None or len(str(bom_prdno).strip()) == 0:
                bom_prdno = tmp_bom_prdno

            if description.strip()==None or len(description.strip())==0:
                continue
            print('description=',description, 'qty=', qty, 'reference=',reference, 'bom_desc=', bom_desc, 'bom_prdno=',bom_prdno)

            sql = "select * from yw_lqerp_wqbom2lqbom where wq_desc='%s' and lqerp_prdno='%s'" % (description, bom_prdno)
            print(sql)
            cur.execute(sql)
            rows=cur.fetchall()
            if len(rows)>0:
                continue
            else:

                insertsql = "insert into yw_lqerp_wqbom2lqbom(wq_desc,wq_qty,wq_refer,lqerp_desc,lqerp_prdno) values('%s','%s','%s','%s','%s')" \
                      % (description, qty, reference, bom_desc, bom_prdno)
                print(insertsql)
                cur.execute(insertsql)

        mysql_conn.commit()
        mysql_conn.close()

    except Exception as e:
        print(e)
        mysql_conn.close()


if __name__=="__main__":
    # print "I'm the second." .
    # file_path = "E:\\联桥2019\\联桥科技\\研发中心\\研发部\\物奇BOM转换"
    # print(file_path)
    # for i, j, k in os.walk(file_path):
    #     print('search', i)
    #     for item in k:
    #         print(item)
    #         filename=i+'\\'+item
    # importfile( filename )

    filename="E:\\联桥2019\\联桥科技\\研发中心\\研发部\\徐明明\\2.0样机图纸\\二采2.0入库资料\\CBB819-PLC049\\602010-XBM1511E-XV2.0_试产BOM_V1.0_20190724.xls"
    changeinto(filename)
    print('程序运行结束!')

