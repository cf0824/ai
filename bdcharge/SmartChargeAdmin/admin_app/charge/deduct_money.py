#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：deduct_money.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/6/5 9:27 
@Description :
'''
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

def add_deduct_cfg(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['time_interval', str, True, '时间间隔'],
        ['user_id', int, True, '扣费对象'],
        ['money', str, True, '金额']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        type_id = form_var.get('type_id')
        user_id = form_var.get('user_id')
        time_interval = form_var.get('time_interval')
        money = form_var.get('money')
        state = form_var.get('state')
        remark = form_var.get('remark')
        data = {
            'type_id': type_id,
            'user_id': user_id,
            'time_interval': time_interval,
            'money': money,
            'state': state,
            'remark': remark,
            'create_time': datetime.datetime.now()
        }
        db.insert('s_deduction_cfg', data)



        return resp
    except Exception as e:
        log.info(f'添加扣费配置失败', exc_info=True)
        raise


def update_deduct_cfg(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_var['time_interval'] = int(form_var.get('time_interval'))
    form_var['money'] = float(form_var.get('money'))

    verify_dict = [
        ['id', int, True, 'id'],
        ['time_interval', int, True, '时间间隔'],
        ['user_id', int, True, '扣费对象'],
        ['money', float, True, '金额']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()
        id = form_var.get('id')
        type_id = form_var.get('type_id')
        user_id = form_var.get('user_id')
        time_interval = form_var.get('time_interval')
        money = form_var.get('money')
        state = form_var.get('state')
        remark = form_var.get('remark')
        data = {
            'type_id': type_id,
            'user_id': user_id,
            'time_interval': time_interval,
            'money': money,
            'state': state,
            'remark': remark,
            'update_time': datetime.datetime.now()
        }
        db.update('s_deduction_cfg', data, {'id': id})

        return resp
    except Exception as e:
        log.info(f'添加扣费配置失败', exc_info=True)
        raise

def add_deduct_detail(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'传入的数据form_var: {form_var}')

    verify_dict = [
        ['money', str, True, '金额'],
        ['user_id', int, True, '扣费对象']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        type_id = form_var.get('type_id')
        user_id = form_var.get('user_id')
        money = form_var.get('money')
        state = form_var.get('state')
        remark = form_var.get('remark')
        data = {
            'type_id': type_id,
            'user_id': user_id,
            'money': money,
            'state': state,
            'remark': remark,
            'create_time': datetime.datetime.now()
        }
        db.insert('s_deduction_detail', data)

        return resp
    except Exception as e:
        log.info(f'添加扣费配置失败:{e}', exc_info=True)
        raise

    