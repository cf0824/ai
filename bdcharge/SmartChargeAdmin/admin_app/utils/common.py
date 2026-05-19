#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  django_admin -> common.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   common.py
@Time    :   2024-06-19 10:44
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
from admin_app.utils.dbFunc import MySQLDB


# 转换成 固定键名（"key"和"value"）的字典列表
def convert_to_fixed_key_value_list(data, key_field, value_field):
    return [{"key": item[key_field], "value": item[value_field]} for item in data if key_field in item and value_field in item]


def convert_single_dict_to_fixed_key_value(item, key_field, value_field):
    return {"key": item[key_field], "value": item[value_field]}


def get_sys_ywty_target(dict_name, dict_code, key="DICT_TARGET"):
    mysql_db = MySQLDB()
    sql = """  
        SELECT DICT_TARGET  FROM sys_ywty_dict WHERE DICT_Name = %s  and DICT_CODE=%s;  
    """
    query = (dict_name, dict_code)
    result = mysql_db.fetchone(sql, query)

    return result[key]


def get_card_type_target(card_type):
    mysql_db = MySQLDB()
    sql = """  
        SELECT *  FROM sc_card_type WHERE CardsNo = %s ;  
    """
    query = (card_type,)
    result = mysql_db.fetchone(sql, query)
    return result


def get_card_status_target(card_type):
    mysql_db = MySQLDB()
    sql = """  
        SELECT StatusName  FROM sc_card_status WHERE StatusNo = %s ;  
    """
    query = (card_type,)
    result = mysql_db.fetchone(sql, query)
    return result['StatusName']


def get_posts_target(post_no):
    name = "默认职务"
    if post_no:
        mysql_db = MySQLDB()
        sql = """  
            SELECT PostName  FROM sys_post WHERE PostNo = %s ;  
        """
        query = (post_no,)
        result = mysql_db.fetchone(sql, query)

        if result:
            name = result['PostName']

    return name


def get_org_target(org_id):
    name = "默认机构"
    if org_id:
        mysql_db = MySQLDB()
        sql = """  
            SELECT ORG_NAME  FROM sys_org WHERE ORG_ID = %s ;  
        """
        query = (org_id,)
        result = mysql_db.fetchone(sql, query)
        if result:
            name = result['ORG_NAME']
    return name
