#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  Agricultural_Museum -> back_up.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   back_up.py
@Time    :   2024/1/12 10:44
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
import base64
import datetime
import os
import pymysql
from django.db import connection, transaction, connections
from admin_app.sys import public
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.Backup import DatabaseBackup
from admin_cfg.settings import BASE_DIR

docker_home = BASE_DIR


# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


# 测试实例连接
def mysql_test_connection(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    host = form_var.get('host')
    port = form_var.get('port')
    username = form_var.get('username')
    password = form_var.get('password')

    if not host or not port or not username or not password:
        return err_msg('参数错误')

    try:
        # 尝试连接数据库
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
        )
        connection.close()
        message = '连接成功！'
        resp['respmsg'] = message
    except pymysql.Error as e:
        message = f'连接失败：{str(e)}'
        return err_msg(message)

    return resp


# 实例信息保存
def mysql_info_save(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    name = form_var.get('name')
    log.info('name: %s' % name)
    if not name:
        return err_msg('实例名称不能为空')
    host = form_var.get('host')
    log.info('host: %s' % host)
    port = form_var.get('port')
    username = form_var.get('username')
    password = form_var.get('password')
    remark = form_var.get('remark')
    if not host or not port or not username or not password:
        return err_msg('参数错误')

    try:
        with transaction.atomic():
            create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO sys_node_info (name, host, port, username, password, remark, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (name, host, port, username, password, remark, create_time)
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
            message = '保存成功！'
            resp['respmsg'] = message
    except Exception as e:
        message = f'保存失败：{str(e)}'
        return err_msg(message)
    return resp


# 根据选择实例获取对应的数据库信息
def from_node_get_database(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    node = form_var.get('node')
    if not node:
        return err_msg('请先选择相应的实例信息')
    log.info(f"node: {node}")
    cursor = connection.cursor()
    sql = "select host,port,username,password from sys_node_info where id=%s"
    cursor.execute(sql, node)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('实例信息获取失败')

    host, port, username, password = row[0], row[1], row[2], row[3]
    # 连接数据库
    try:
        db_connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        cursor = db_connection.cursor()

        # 获取所有数据库名信息
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        # database_names = [db[0] for db in databases]
        log.info(f"Database names={databases}")
        database_names = [{"key": db[0], "value": db[0]} for db in databases]
        log.info(f"database_names={database_names}")
        form_var['show_database'] = database_names
        # 关闭数据库连接
        cursor.close()
        db_connection.close()
    except Exception as e:
        return err_msg(f'获取数据库名信息失败：{str(e)}')
    resp['form_var'] = form_var
    return resp


# 根据对应数据库获取对应的数据表信息
def from_database_get_tables(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    node = form_var.get('node')
    database = form_var.get('database')

    cursor = connection.cursor()
    sql = "select host,port,username,password from sys_node_info where id=%s"
    cursor.execute(sql, node)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('实例信息获取失败')

    host, port, username, password = row[0], row[1], row[2], row[3]
    # 连接数据库
    try:
        db_connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
    except Exception as e:
        return err_msg(f'获取数据库名信息失败：{str(e)}')

    try:
        transfer = []  # 全部数据, 数据变量
        transferData = []  # 已选中数据，绑定变量
        transfer_keys = []

        cur = db_connection.cursor()  # 创建游标
        cur.execute("SELECT table_name, table_comment FROM information_schema.tables WHERE table_schema = %s", [database])
        rows = cur.fetchall()

        log.info(rows)

        for item in rows:
            transfer.append({"key": item[0], "label": item[0], "disabled": False})
            transfer_keys.append(item[0])

    except Exception as ex:
        log.error("生成穿梭框数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        return err_msg('生成穿梭框数据失败')
    form_var['tables'] = transferData
    form_var['show_tables'] = transfer

    resp['form_var'] = form_var
    return resp


# 任务规则添加
def task_cron_add(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    name = form_var.get('name')
    cron = form_var.get('cron')
    description = form_var.get('description')

    if not name or not cron:
        return err_msg('参数错误')
    try:
        with transaction.atomic():
            create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO sys_task_cron (name, cron, description, create_time) VALUES (%s, %s, %s, %s)"
            values = (name, cron, description, create_time)
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
            message = '保存成功！'
            resp['respmsg'] = message
    except Exception as e:
        message = f'保存失败：{str(e)}'
        return err_msg(message)
    return resp


# 任务添加
def backup_task_add(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    node=form_var.get('node')
    database=form_var.get('database')
    tables=form_var.get('tables')
    is_scheduled=form_var.get('is_scheduled')
    scheduled_rule=form_var.get('scheduled_rule')
    execute_sql=form_var.get('execute_sql')
    remark = form_var.get('remark')

    if not node or not database:
        return err_msg('参数错误')
    if tables:
        tables = ', '.join(tables)
    try:
        with transaction.atomic():
            create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO sys_backup_task (node_id, database_name, tables_name, data_type, cron_id, execute_sql, remark, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            log.info(f"sql: %s" % sql)
            values = (node, database, tables, is_scheduled, scheduled_rule, execute_sql, remark, create_time)
            log.info(f"values: {values}")
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
            message = '保存成功！'
            resp['respmsg'] = message
    except Exception as e:
        message = f'保存失败：{str(e)}'
        return err_msg(message)
    return resp

def get_tables_with_comments(database_name):
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT table_name, table_comment FROM information_schema.tables WHERE table_schema = %s", [database_name])
        tables_with_comments = cursor.fetchall()
        result = [{"key": table[0], "value": table[1]} for table in tables_with_comments]
        return result


def back_up_init(request, data, resp):
    log = public.logger

    log.info(f"项目根目录".format(docker_home))

    form_var = data.get('form_data', {})

    back_up_type = [
        {
            "key": 1,
            "value": "数据库"
        },
        {
            "key": 2,
            "value": "数据表"
        },
        {
            "key": 3,
            "value": "全部"
        },
    ]
    show_tables = get_tables_with_comments(database_name='manage')

    form_var['show_tables'] = ""
    form_var['back_type'] = ""
    form_var['excluded_prefixes'] = "django_,auth_,sys_"
    form_var['back_up_type'] = back_up_type
    form_var['show_tables'] = show_tables
    resp['form_var'] = form_var
    return resp


def start_back_up(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    back_type = form_var.get('back_type')
    excluded_prefixes = form_var.get('excluded_prefixes')

    if not back_type:
        return err_msg('请选择备份类型')
    back_type = int(back_type)
    if not excluded_prefixes:
        excluded_prefixes = []
    else:
        try:
            excluded_prefixes = excluded_prefixes.split(',')
        except:
            excluded_prefixes = []
    base_path = f"{docker_home}/db_back"
    db_backup = DatabaseBackup(backup_path=base_path, excluded_prefixes=excluded_prefixes, back_type=back_type)
    db_backup.backup_database()
    return resp


def get_db_file_names(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    qry_date = form_var.get('qry_date', None)
    log.info(f"qry_date={qry_date}")
    if not qry_date:
        qry_date = datetime.datetime.now().strftime("%Y-%m-%d")

    base_path = f"{docker_home}/db_back/{qry_date}"
    sql_files = [file for file in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, file))]
    log.info(f'sql_files={sql_files}')
    resp_data = []
    for file in sql_files:
        resp_data.append({"name": file})
    form_var['table_data'] = resp_data
    resp['form_var'] = form_var
    return resp


def download_sql_file(request, data, resp):
    form_var = data.get('form_var', {})
    name = form_var.get('name')
    qry_date = form_var.get('qry_date', None)
    if not qry_date:
        qry_date = datetime.datetime.now().strftime("%Y-%m-%d")

    base_path = f"{docker_home}/db_back/{qry_date}/{name}"
    if not os.path.exists(base_path):
        return err_msg('文件不存在')
    with open(base_path, 'rb') as f:
        b = f.read()
        base64_data = base64.b64encode(b)
        file_base64 = base64_data.decode()
    resp['respcode'] = '125800'
    resp['filename'] = f"{name}"
    resp['filetype'] = 'text/plain'
    resp['filedata'] = file_base64
    return resp


def execute_sql_file(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    name = form_var.get('name')
    qry_date = form_var.get('qry_date', None)
    if not qry_date:
        qry_date = datetime.datetime.now().strftime("%Y-%m-%d")

    base_path = f"{docker_home}/db_back/{qry_date}/{name}"
    if not os.path.exists(base_path):
        return err_msg('文件不存在')
    log.info(f"base_path={base_path}")
    db_backup = DatabaseBackup()
    db_backup.restore_sql_file(base_path)
    return resp
