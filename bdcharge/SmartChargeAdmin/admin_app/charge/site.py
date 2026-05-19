#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：site.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/16 11:05 
@Description :
'''
import base64
import os
import sys
import tempfile
import zipfile

from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
import requests
from admin_app.sys import public
import datetime
from admin_app.tools import handle

from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils.handle_sim import query_card_info


# 增删改查配置数据操作主流程
def Main_Proc(request):
    log = public.logger
    gb = globals()
    return handle.func_handle(request, gb)


# 测试
def test(request, data, resp):
    log = public.logger
    log.info('test begin')
    resp['detail'] = {'a': 1, 'b': 2}
    return resp


def add_site_user(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['site_id', int, True, 'id'],
        ['user_id', str, True, '用户id'],
        ['identify_id', str, True, '身份']

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        identify_id = form_var.get('identify_id')
        data = {
            'site_id': site_id,
            'user_id': user_id,
            'identify_id': identify_id,
            'create_time': datetime.datetime.now()
        }
        db.insert('s_site_user', data)

        return resp
    except Exception as e:
        log.info(f'获取sim卡信息失败', exc_info=True)
        raise

def update_site_user(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['id', int, True, 'id'],
        ['site_id', int, True, '站点id'],
        ['user_id', int, True, '用户id'],
        ['identify_id', str, True, '身份']

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        identify_id = form_var.get('identify_id')
        data = {
            'site_id': site_id,
            'user_id': user_id,
            'identify_id': identify_id,
            'update_time': datetime.datetime.now()
        }
        db.update('s_site_user', data, {'id': id})

        return resp
    except Exception as e:
        log.info(f'获取sim卡信息失败', exc_info=True)
        raise

def del_site_user(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['id', int, True, 'id'],
        ['site_id', int, True, '站点id'],
        ['user_id', int, True, '用户id'],
        ['identify_id', int, True, '身份']

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()
        id = form_var.get('id')

        db.delete('s_site_user', {'id': id})

        return resp
    except Exception as e:
        log.info(f'获取sim卡信息失败', exc_info=True)
        raise


def del_site(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['site_id', int, True, '站点id']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()
        site_id = form_var.get('site_id')

        db.delete('s_site_info', {'site_id': site_id})

        return resp
    except Exception as e:
        log.info(f'获取sim卡信息失败', exc_info=True)
        raise

    