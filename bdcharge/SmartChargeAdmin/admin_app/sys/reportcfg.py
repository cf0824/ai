import sys
from django.shortcuts import render,redirect,HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from admin_cfg.settings import BASE_DIR
from PIL import Image
import re
import xlrd
import xlsxwriter
from io import BytesIO
import base64
import string
import requests

#配置操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


# 报表配置新增/修改
def report_cfg_create(request, data, resp):
    log = public.logger
    repconfig = data.get('repconfig',{})
    report_id = repconfig.get('report_id',None)
    report_name = repconfig.get('report_name',None)
    report_startRows = repconfig.get('startRows',None)
    report_startCols = repconfig.get('startCols',None)
    report_show_api = repconfig.get('show_api',None)
    report_show_tran_type = repconfig.get('show_tran_type',None)
    report_data_api = repconfig.get('data_api',None)
    report_data_tran_type = repconfig.get('data_tran_type',None)
    report_data_sql = repconfig.get('data_sql',None)
    opera_list = repconfig.get('opera_list',[])
    excel_keep = repconfig.get('excel_keep',False)
    report_cellsMap = data.get('cellsMap','{}')
    report_dataSource = data.get('dataSource','{}')
    report_rows = data.get('rows','{}')
    report_colums = data.get('colums','{}')
    report_mergeCells = data.get('mergeCells','[]')
    report_sourceData = data.get('sourceData','{}')
    user_id = public.user_id
    report_other_cfg = json.dumps({"opera_list": opera_list,"excel_keep":excel_keep})

    if not all([report_name, report_startRows, report_startCols, report_show_api, report_show_tran_type]):
        return ERROR['REQ_PARAMS_ERROR']

    cursor= connection.cursor()
    if report_id:
        sql = "update sys_report_cfg_info set report_name=%s, report_startRows=%s, report_startCols=%s, " \
              "report_show_api=%s, report_show_tran_type=%s, report_data_api=%s, report_data_tran_type=%s, " \
              "report_data_sql=%s, report_other_cfg=%s, report_cellsMap=%s, report_dataSource=%s, report_rows=%s, " \
              "report_colums=%s,report_mergeCells=%s,report_sourceData=%s,update_user_id=%s,update_date=now() where report_id=%s"
        row = cursor.execute(sql,(report_name,report_startRows,report_startCols,report_show_api,report_show_tran_type,
                                  report_data_api,report_data_tran_type,report_data_sql,report_other_cfg,report_cellsMap,report_dataSource,
                                  report_rows,report_colums,report_mergeCells,report_sourceData,user_id,report_id))
    else:
        sql = "insert into sys_report_cfg_info(report_name,report_startRows,report_startCols,report_show_api,report_show_tran_type," \
              "report_data_api,report_data_tran_type,report_data_sql,report_other_cfg,report_cellsMap,report_dataSource,report_rows,report_colums," \
              "report_mergeCells,report_sourceData,create_user_id,create_date,update_user_id,update_date) " \
              "value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,now())"
        row = cursor.execute(sql,(report_name,report_startRows,report_startCols,report_show_api,report_show_tran_type,
                                  report_data_api,report_data_tran_type,report_data_sql,report_other_cfg,report_cellsMap,report_dataSource,
                                  report_rows,report_colums,report_mergeCells,report_sourceData,user_id,user_id))
        report_id = cursor.lastrowid
    if row == 0:
        return ERROR['OPERA_FAIL']
    resp['report_id'] = report_id
    return resp

# 报表配置列表获取
def report_cfg_list(request,data,resp):
    cursor = connection.cursor()
    sql = "select report_id, report_name, update_date from sys_report_cfg_info"
    cursor.execute(sql)
    rows = cursor.fetchall()
    detail = []
    for report_id, report_name, update_date in rows:
        detail.append({
            'report_id': report_id,
            'report_name': report_name,
            'update_date': update_date
        })
    resp['detail'] = detail
    return resp

# 报表配置信息查询
def report_cfg_select(request, data, resp):
    isRender = data.get('isRender',False)
    report_id = data.get('report_id',None)
    if not report_id:
        return ERROR['REQ_PARAMS_ERROR']

    cursor = connection.cursor()
    sql = "select report_name, report_startRows, report_startCols, report_show_api, report_show_tran_type, " \
          "report_data_api, report_data_tran_type, report_data_sql, report_other_cfg, report_cellsMap, report_dataSource, " \
          "report_rows, report_colums, report_mergeCells,report_sourceData from sys_report_cfg_info where report_id = %s"
    cursor.execute(sql,report_id)
    row = cursor.fetchone()
    if row:
        resp['repconfig'] = {
            'report_id': report_id,
            'report_name': row[0],
            'startRows': row[1],
            'startCols': row[2],
            'show_api': row[3],
            'show_tran_type': row[4],
            'data_api': row[5],
            'data_tran_type': row[6],
            'data_sql': row[7] if not isRender else ''
        }
        resp['repconfig'].update(json.loads(row[8],encoding='utf-8'))
        resp['cellsMap'] = eval(row[9])
        resp['dataSource'] = eval(row[10]) if not isRender else {}
        resp['rows'] = eval(row[11])
        resp['colums'] = eval(row[12])
        resp['mergeCells'] = json.loads(row[13],encoding='utf-8')
        resp['sourceData'] = json.loads(row[14],encoding='utf-8')
    else:
        resp['repconfig'] = {
            'report_id': '',
            'report_name': '',
            'startRows': 6,
            'startCols': 10,
            'show_api': '',
            'show_tran_type': '',
            'data_api': '',
            'data_tran_type': '',
            'data_sql': '',
            'opera_list': []
        }
        resp['cellsMap'] = {}
        resp['dataSource'] = {}
        resp['rows'] = {}
        resp['colums'] = {}
        resp['mergeCells'] = []
        resp['sourceData'] = {}
    return resp

# 报表数据接口（报表整体）
def report_data_show(request, data, resp):
    log = public.logger
    report_id = data.get('report_id',None)
    sourceData = data.get('sourceData',{})
    if not report_id:
        return ERROR['REQ_PARAMS_ERROR']

    cursor = connection.cursor()
    sql  = "select report_data_sql from sys_report_cfg_info where report_id =%s"
    cursor.execute(sql,report_id)
    row = cursor.fetchone()
    if row:
        data_sql = row[0]
    else:
        resp['sourceData'] = sourceData
        return resp

    # 数据替换
    def GetRealSQL(sql):
        pattern = re.compile("\$\[(.*?)\]")
        sqlvar = pattern.findall(sql)
        for sqlitm in sqlvar:
            old = "$[" + sqlitm + "]"
            if sqlitm in sourceData.keys():
                new = "'" + str(sourceData.get(sqlitm)) + "'"
            else:
                new = "''"
            sql = sql.replace(old, new)
        # log.info('real sql=' + str(sql), extra={'ptlsh': public.req_seq})
        sql = public.SqlKeywordConver(sql, None)
        # log.info('finally sql=' + str(sql), extra={'ptlsh': public.req_seq})
        return sql

    sql_list = GetRealSQL(data_sql).split(';')
    for selsql in sql_list:
        cursor.execute(selsql)
        row = cursor.fetchone()
        description = [tuple[0] for tuple in cursor.description]
        if row:
            for index,item in enumerate(description):
                sourceData[item] = row[index]
    resp['sourceData'] = sourceData
    return  resp



# 报表单个字段数据源获取数据,返回 sql 查询数据和自定义接口参数列表
def report_data_other(request, data, resp):
    log = public.logger
    report_id = data.get('report_id',None)
    sourceData = data.get('sourceData',{})
    if not report_id:
        return ERROR['REQ_PARAMS_ERROR']

    cursor = connection.cursor()
    sql  = "select report_dataSource from sys_report_cfg_info where report_id =%s"
    cursor.execute(sql,report_id)
    row = cursor.fetchone()
    if row:
        dataSource = json.loads(row[0],encoding='utf-8')
    else:
        resp['sourceData'] = sourceData
        resp['interfaceList'] = []
        return resp

    # 数据替换
    def GetRealSQL(sql):
        pattern = re.compile("\$\[(.*?)\]")
        sqlvar = pattern.findall(sql)
        for sqlitm in sqlvar:
            old = "$[" + sqlitm + "]"
            if sqlitm in sourceData.keys():
                new = "'" + str(sourceData.get(sqlitm)) + "'"
            else:
                new = "''"
            sql = sql.replace(old, new)
        # log.info('real sql=' + str(sql), extra={'ptlsh': public.req_seq})
        sql = public.SqlKeywordConver(sql, None)
        # log.info('finally sql=' + str(sql), extra={'ptlsh': public.req_seq})
        return sql

    #对关键字进行处理
    def Keywords( keyword ):
        cursor = connection.cursor()
        new_value=keyword
        if keyword == '${USER_ID}':
            new_value=public.user_id
        elif keyword == '${USER_NAME}':
            sql="select user_name from sys_user where user_id='%s'" % public.user_id
            cursor.execute(sql)
            row=cursor.fetchone()
            new_value=row[0]
        elif keyword == '${TRAN_DATE}':
            new_value = datetime.datetime.now().strftime('%Y-%m-%d')
        elif keyword == '${TRAN_TIME}':
            new_value = datetime.datetime.now().strftime('%H:%M:%S')
        elif keyword == '${TRAN_DATETIME}':
            new_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif keyword == '${YYYY}':  #当前年份
            new_value = datetime.datetime.now().strftime('%Y')
        elif keyword == '${WEEK}':  #当年第几周
            new_value = datetime.datetime.now().strftime('%W')
        # log.info('keyword=' + str(keyword), extra={'ptlsh': public.req_seq})
        # log.info('new_value='+str(new_value), extra={'ptlsh':public.req_seq})
        return new_value

    interfaceList = []
    for valkey,item in dataSource.items():
        source = item['source']
        data_type = item['data_type']
        if source['type'] == 'SQL':
            selsql = GetRealSQL(source['value'])
            cursor.execute(selsql)
            rows = cursor.fetchall()
            if rows:
                if data_type == 'datasets':
                    sourceData[valkey] = rows
                else:
                    if len(rows) == 1:
                        if len(rows[0])== 1:
                            sourceData[valkey] = rows[0][0]
                        else:
                            sourceData[valkey] = rows[0]
                    else:
                        sourceData[valkey] = rows
        elif source['type'] == 'CUSTOMAPI':
            interfaceList.append({
                'valkey': valkey,
                'api': source['api'],
                'tran_type': source['tran_type']
            })
        elif source['type'] == 'KEYWORD':
            sourceData[valkey] = Keywords(source['value'])


    resp['interfaceList'] = interfaceList
    resp['sourceData'] = sourceData
    return resp

# 报表导出 Excel
def report_export_excel(request, data, resp):
    log = public.logger
    report_id = data.get('report_id',None)
    excel_keep = data.get('excel_keep',False)
    newmergeCells = data.get('newmergeCells',[])
    rowadd = data.get('rowadd',0)
    coladd = data.get('coladd',0)
    newCWIndex = data.get('newCWIndex',{})
    newRHIndex = data.get('newRHIndex',{})
    expandCfg = data.get('expandCfg',{})
    newCellIndex = data.get('newCellIndex',{})
    newOldList = data.get('newOldList',[])
    sourceData = data.get('sourceData',{})

    if not report_id:
        return ERROR['REQ_PARAMS_ERROR']

    cursor = connection.cursor()
    sql = "select report_name,report_startRows, report_startCols,report_cellsMap,report_rows,report_colums from sys_report_cfg_info " \
          "where report_id = %s"
    cursor.execute(sql,report_id)
    selrow = cursor.fetchone()
    if selrow:
        report_name = selrow[0]
        startRows = int(selrow[1])
        startCols = int(selrow[2])
        cellsMap = eval(selrow[3])
        rows = eval(selrow[4])
        colums = eval(selrow[5])
    else:
        return ERROR['REQ_PARAMS_ERROR']

    def insert_img_data(row,col,url,image_width,image_height):
        img_name = str(row)+str(col) + '_default.png'
        img_data = BytesIO(requests.get(url).content)
        image  = Image.open(img_data)
        x_scale = image_width / (
            image.size[0]
        ) # 固定宽度/要插入的原始图片宽
        y_scale = image_height / (
            image.size[1]
        ) # 固定高度/要插入的原始图片高
        return img_name,img_data,x_scale,y_scale


    # 生成Excel
    def make_excel(filename):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output,{'in_memory': True})
        # workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(filename.split('.')[0])
        if sourceData == {}:
            workbook.close()
            return

        # 数字索引转换字母索引（从1开始）
        def getColumnName(columnIndex):
            ret = ''
            ci = columnIndex - 1
            index = ci // 26
            if index > 0:
                ret += getColumnName(index)
            ret += string.ascii_uppercase[ci % 26]

            return ret

        # 设置行高
        def setrowHights(index):
            rate = 0.6
            if rows != {}:
                for key in newRHIndex.keys():
                    loop = newRHIndex[key]["loop"]
                    if len(loop):
                        if index >= loop[0] and index <= loop[1]:
                            worksheet.set_row(index, rows.get(newRHIndex[key]["old"],24)*rate)
                    elif int(key) == index:
                        worksheet.set_row(index, rows.get(newRHIndex[key]["old"],24)*rate)
            else:
                worksheet.set_row(index, 24*rate)


        # 设置列宽
        def setcolWidths(index):
            rate = 0.101375
            newindex = getColumnName(index+1)
            newindex = str(newindex)+':'+str(newindex)
            if colums != {}:
                for key in newCWIndex.keys():
                    loop = newCWIndex[key]["loop"]
                    if len(loop):
                        if index >= loop[0] and index <= loop[1]:
                            worksheet.set_column(newindex, colums.get(newCWIndex[key]["old"],80)*rate)
                    elif int(key) == index:
                        worksheet.set_column(newindex, colums.get(newCWIndex[key]["old"],80)*rate)
            else:
                worksheet.set_column(newindex, 80*rate)
        # # 设置图片时的行高列宽
        def setRCwh(row,col,rh,cw):
            log.info('rh=%s,cw=%s'%(rh,cw))
            if rows != {}:
                for key in newRHIndex.keys():
                    loop = newRHIndex[key]["loop"]
                    if len(loop):
                        if row >= loop[0] and row <= loop[1] and rows.get(newRHIndex[key]["old"],False):
                            if rh > rows[newRHIndex[key]["old"]]:
                                worksheet.set_row(row, rh)
                    elif int(key) == row:
                        if rh > rows[newRHIndex[key]["old"]]:
                            worksheet.set_row(row, rh)
                    else:
                        worksheet.set_row(row, rh)
            else:
                worksheet.set_row(row, rh)

            # 列宽
            newindex = getColumnName(col+1)
            newindex = str(newindex)+':'+str(newindex)
            cw = cw * 0.2
            if colums != {}:
                for key in newCWIndex.keys():
                    loop = newCWIndex[key]["loop"]
                    if len(loop):
                        if col >= loop[0] and col <= loop[1] and colums.get(newCWIndex[key]["old"],False):
                            if cw> colums[newCWIndex[key]["old"]]:
                                worksheet.set_column(newindex, cw)
                    elif int(key) == col:
                        if cw> colums[newCWIndex[key]["old"]]:
                            worksheet.set_column(newindex, cw)
                    else:
                        worksheet.set_column(newindex, cw)
            else:
                worksheet.set_column(newindex, cw)

        # 合并单元格
        def mergerCells(row,col,data,format):
            for item in newmergeCells:
                if item:
                    first_row = int(item['row'])
                    first_col = int(item['col'])
                    last_row = first_row + int(item['rowspan']) - 1
                    last_col = first_col + int(item['colspan']) - 1
                    if row>= first_row and row <= last_row and col >= first_col and col <= last_col:
                        if row == first_row and col == first_col:
                            worksheet.merge_range(first_row, first_col, last_row, last_col,data,format)
                        return True
            return False

        # mergerCells()
        # 写 Excel 前的数据处理
        json_borders = ['borderLeft','borderRight','borderTop','borderBottom']
        switch_true_items = ['fontWeight','fontStyle','textDecoration']
        switch_table = {
            'textAlign': 'align',
            'verticalAlign': 'valign',
            'fontFamily': 'font_name',
            'fontSize': 'font_size',
            'backgroundColor': 'bg_color',
            'color': 'font_color',
            'borderLeft': 'left',
            'borderRight': 'right',
            'borderTop': 'top',
            'borderBottom': 'bottom',
            'fontWeight': 'bold',
            'fontStyle':'italic',
            'textDecoration': 'underline'
        }
        font_name_switch = {
            'SimSun': "宋体",
            'FangSong': "仿宋",
            'SimHei': '黑体',
            'KaiTi': '楷体',
            'Microsoft YaHei': '微软雅黑'
        }

        def border_switch(data,key):
            bstyle = {
                key: 1 if data['type']=='solid' else 3,
                key+'_color': data['color']
            }
            return bstyle

        for ckey in cellsMap.keys():
            cellStyle = cellsMap[ckey].get('cellStyle',False)
            newStyle = {
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            }
            if cellStyle:
                for key in cellStyle.keys():
                    if key in json_borders:
                        border_data = cellStyle[key]
                        newStyle.update(border_switch(border_data,switch_table[key]))
                    elif key in switch_true_items:
                        newStyle[switch_table[key]] = True
                    else:
                        if key == 'verticalAlign' and cellStyle[key] == 'middle':
                            newStyle['valign'] = 'vcenter'
                        elif key == 'fontSize':
                            newStyle['font_size'] = int(cellStyle[key].replace('px',''))
                        elif key == 'fontFamily':
                            newStyle['font_name'] = font_name_switch.get(cellStyle[key],cellStyle[key])
                        else:
                            newStyle[switch_table[key]] = cellStyle[key]
            cellsMap[ckey]['cellStyle'] = newStyle

        row_num = startRows + rowadd
        col_num = startCols + coladd
        for row in range(row_num):
            for col in range(col_num):
                # 设置行高
                if col == 0:
                    setrowHights(row)
                # 设置列宽
                if row == 0:
                    setcolWidths(col)
                # 数据集渲染时的样式设置
                tcell, expdata = None, ""
                for expkey in expandCfg.keys():
                    expandItem = expandCfg[expkey]
                    scope = expandItem['scope']
                    if row >= scope[0] and row <= scope[2] and col >= scope[1] and col <= scope[3]:
                        tcell = cellsMap[expkey]
                        if expandItem['expand'] == 'DRight':
                            expdata = expandItem['data'][row - scope[0]][col - scope[1]]
                        elif expandItem["expand"] == "Right":
                            expdata = expandItem["data"][col - scope[1]]
                        elif expandItem["expand"] == "Down":
                            expdata = expandItem["data"][row - scope[0]]
                okey = str(row)+','+str(col)
                if newCellIndex.get(okey):
                    oldKey = newCellIndex[okey]
                    tcell = cellsMap[oldKey]
                elif not tcell and (okey not in newOldList):
                    tcell = cellsMap.get(okey,None)

                if tcell:
                    isImg = False
                    if tcell.get('cellStyle'):
                        cellStyle = tcell['cellStyle']
                    else:
                        cellStyle = {
                            'align': 'center',
                            'valign': 'vcenter',
                            'text_wrap': True
                        }

                    write_data = ""
                    if tcell.get('data'):
                        if tcell['data']['type']== 'simple':
                            write_data = tcell['data']['value']
                        elif tcell['data']['type']== 'variable':
                            if sourceData.get(tcell['data']['value']):
                                write_data = sourceData.get(tcell['data']['value'])
                            else:
                                write_data = ""
                        elif tcell['data']['type']== 'datasets' and tcell['data'].get('expand',False):
                            expand = tcell['data'].get('expand')
                            if expand == 'None':
                                write_data = str(sourceData.get(tcell['data']['value'],""))
                            else:
                                write_data = str(expdata)
                        elif tcell['data']['type']== 'image':
                            if tcell['data']['source'] == "Link":
                                url = tcell['data']['value']
                            elif tcell['data']['source'] == "Variable":
                                url = str(sourceData.get(tcell['data']['value'],""))
                            if 'http' in url:
                                width = tcell['data']['width']
                                height = tcell['data']['height']
                                img_name, img_data,x_scale,y_scale = insert_img_data(row,col,url,width,height)
                                isImg = True
                        else:
                            write_data = str(tcell['data']['value'])
                    # 写数据
                    format = workbook.add_format(cellStyle)
                    flag = mergerCells(row, col, write_data, format)
                    if not flag:
                        worksheet.write(row, col, write_data, format)
                    if isImg:
                        worksheet.insert_image(row, col, img_name, {'x_scale': x_scale, 'y_scale': y_scale, 'image_data': img_data})
                        setRCwh(row,col,width,height)
        workbook.close()
        return output



    filename=report_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx'
    output = make_excel(filename).getvalue()
    base64_data = base64.b64encode(output)
    file_base64 = base64_data.decode()
    file_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    resp['filename'] = filename
    resp['type'] = file_type
    resp['base64'] = file_base64

    # excel 存档
    if excel_keep:
        filename = BASE_DIR + '/static/report_keep_file/' + filename
        with open(filename, "wb") as f:
            f.write(output)

    return resp












