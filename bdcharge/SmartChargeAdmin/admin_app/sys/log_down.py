#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  Agricultural_Museum -> log_down.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   log_down.py
@Time    :   2023/11/2 18:02
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
import glob
import os

from django.db import connection
from admin_app.tools import handle
from admin_app.sys import public
from admin_app.tools.ErrorMsg import err_msg

log = public.logger


# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


def get_log_file_names(request, data, resp):
    form_var = data.get('form_var', {})
    qry_date = form_var.get('qry_date', None)
    log.info(f"qry_date={qry_date}")
    if not qry_date:
        qry_date = datetime.datetime.now().strftime("%Y%m%d")

    if len(qry_date) == 10:
        qry_date2 = qry_date[0:4] + qry_date[5:7] + qry_date[8:10]
    elif len(qry_date) == 8:
        qry_date2 = qry_date[0:4] + '-' + qry_date[4:6] + '-' + qry_date[6:8]
    else:
        qry_date2 = datetime.datetime.now().strftime("%Y%m%d")

    localhome = public.localhome[:-1]
    log_dir = f"{localhome}/log"
    log_files = [file for file in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, file))]
    log.info(f'log_files={log_files}')
    resp_data = []
    for file in log_files:
        if qry_date2 in file or qry_date in file:
            resp_data.append({"name": file})
    form_var['table_data'] = resp_data
    resp['form_var'] = form_var
    return resp


def download_log(request, data, resp):
    form_var = data.get('form_var', {})
    name = form_var.get('name')

    localhome = public.localhome[:-1]
    log_path = f"{localhome}/log/{name}"
    if not os.path.exists(log_path):
        return err_msg('日志不存在')
    with open(log_path, 'rb') as f:
        b = f.read()
        base64_data = base64.b64encode(b)
        file_base64 = base64_data.decode()
    resp['respcode'] = '125800'
    resp['filename'] = f"{name}"
    resp['filetype'] = 'text/plain'
    resp['filedata'] = file_base64
    return resp
