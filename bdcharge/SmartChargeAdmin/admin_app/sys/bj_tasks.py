#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  Agricultural_Museum -> bj_tasks.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   bj_tasks.py
@Time    :   2024/2/21 8:51
@Desc    :
             ┏┓       ┏┓
            ┏┛┻━━━━━━━┛┻┓
            ┃    ☃      ┃
            ┃  ┳┛   ┗┳  ┃
            ┃     ┻     ┃
            ┗━┓       ┏━┛
              ┃       ┗━━━━┓
              ┃ 神兽保佑     ┣┓
              ┃　永无BUG！   ┏┛
              ┗┓┓┏━━━┳┓┏━━━┛
               ┃┫┫   ┃┫┫
               ┗┻┛   ┗┻┛
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
=================================================="""
import datetime
import logging

from django.db import connection, transaction
from admin_app import public as public2
from admin_app.sys import public
from admin_app.tools import handle, excel_tool
from admin_app.tools.ErrorMsg import err_msg
from admin_cfg.settings import BASE_DIR


# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


def from_bank_get_staffs(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})

    bank = form_var.get('bank')
    log.info(f"bank={bank}")
    try:
        transfer = []  # 全部数据, 数据变量
        transferData = []  # 已选中数据，绑定变量
        transfer_keys = []
        cur = connection.cursor()  # 创建游标
        cur.execute("SELECT id, name FROM bj_task_staff WHERE bank_id = %s", [bank])
        rows = cur.fetchall()

        log.info(rows)

        for item in rows:
            transfer.append({"key": item[0], "label": str(item[0]) + '-' + item[1], "disabled": False})
            transfer_keys.append(item[0])

    except Exception as ex:
        log.error("生成穿梭框数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        return err_msg('生成穿梭框数据失败')
    form_var['staffs'] = transferData
    form_var['show_staffs'] = transfer

    resp['form_var'] = form_var
    return resp


def tasks_add(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    tasks = form_var.get('tasks')
    log.info('tasks: %s' % tasks)
    staffs = form_var.get('staffs')
    log.info('staffs: %s' % staffs)
    if not staffs:
        return err_msg('参数错误 员工信息')

    try:
        with transaction.atomic():
            create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO bj_user_task (task_id, staff_id, create_time,status) VALUES (%s, %s, %s,%s)"
            with connection.cursor() as cursor:
                for staff in staffs:
                    values = (tasks, staff, create_time, 0)
                    cursor.execute(sql, values)
            message = '保存成功！'
            resp['respmsg'] = message
    except Exception as e:
        message = f'保存失败：{str(e)}'
        return err_msg(message)
    return resp


@transaction.atomic()
def import_base_task_data(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    import_file = form_var.get('import_file')
    if not import_file:
        return err_msg('请先上传导入excel文件')

    cursor = connection.cursor()
    sql = "select md5_name from sys_fileup where file_id=%s"
    cursor.execute(sql, import_file)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('文件不存在')
    md5_name = row[0]
    # 查询模板配置
    keys, keys_index = ['name', 'type', 'quantity', 'cycle'], [0, 1, 2, 3]

    file_path = '%s/fileup/%s' % (BASE_DIR, md5_name)
    log.info(f"file_path={file_path}")
    result = excel_tool.get_excel_data(file_path, keys, begin_row=1, sheet_index=0, keys_index=keys_index)
    now = datetime.datetime.now()

    # 写入数据
    for item in result:
        sql = "insert into bj_base_task(name,type,quantity,cycle,status,create_time) value(%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (item['name'], item['type'], item['quantity'], item['cycle'], '0', now))
    return resp


@transaction.atomic()
def import_reward_task_data(request, data, resp):
    form_var = data.get('form_var', {})
    import_file = form_var.get('import_file')
    if not import_file:
        return err_msg('请先上传导入excel文件')

    cursor = connection.cursor()
    sql = "select md5_name from sys_fileup where file_id=%s"
    cursor.execute(sql, import_file)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('文件不存在')
    md5_name = row[0]
    # 查询模板配置
    keys, keys_index = ['name', 'type', 'quantity', 'cycle', 'point'], [0, 1, 2, 3, 4]

    file_path = '%s/fileup/%s' % (BASE_DIR, md5_name)

    result = excel_tool.get_excel_data(file_path, keys, begin_row=1, sheet_index=0, keys_index=keys_index)
    now = datetime.datetime.now()

    # 写入数据
    for item in result:
        sql = "insert into bj_reward_task(name,type,quantity,cycle,point,status,create_time) value(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (item['name'], item['type'], item['quantity'], item['cycle'], item['point'], '0', now))
    return resp
