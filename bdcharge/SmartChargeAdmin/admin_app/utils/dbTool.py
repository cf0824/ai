#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：消费机管理后台(本地) 
@File    ：dbtool.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/6/20 14:57 
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
'''
import datetime

from django.db import transaction
from admin_app.tools import handle
from admin_app.utils.dbFunc import MySQLDB
from admin_app.tools.ErrorMsg import err_msg
from admin_app.sys import public
from admin_app.utils.seqFunc import generator

log = public.logger


# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)

def Get_Max(table_name, field_name, length):

        db = MySQLDB()
        sql = f"""SELECT MAX(RIGHT({field_name}, {length})) AS max_last_digits  
                    FROM {table_name}  
                    WHERE LENGTH({field_name}) >= {length}  
                    AND RIGHT({field_name}, {length}) REGEXP '^[0-9]{{{length}}}$'; """
        result = db.fetchone(sql)
        log.info(f"result = {result}")
        log.info(f"result = {type(result)}")
        max_number = result['max_last_digits']
        log.info(f"max_number = {max_number}")
        log.info(f"max_number = {type(max_number)}")
        max_number = int(max_number)

        return max_number