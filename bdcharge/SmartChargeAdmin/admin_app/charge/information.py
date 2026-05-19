#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：information.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/8 17:42 
@Description :
'''
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from admin_cfg.settings import APP_API, HARDWARE_API, BASE_DIR
from admin_app.sys.public_db import Get_SeqNo
from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils.timeTool import compare_time


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


def get_common_args_detail(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['eq_arg_no', str, True, '参数编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_arg_no = form_var.get('eq_arg_no')
        sql = "select * from s_eq_args_common where arg_no = %s"
        arg = (eq_arg_no,)
        result = db.fetchone(sql, arg)
        log.info(f'result: {result}')
        table_data = []
        table_data.append(result)
        form_var['table_data'] = table_data
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def get_eq_info_by_eq_id(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['eq_id', int, True, '设备id']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_id = form_var.get('eq_id')
        sql = "select * from s_eq_info where eq_id = %s"
        arg = (eq_id,)
        result = db.fetchone(sql, arg)
        log.info(f'result: {result}')
        terminal_address = result.get('terminal_address')
        sql1 = "select * from s_eq_port where eq_id = %s"
        arg1 = (eq_id,)
        port_info = db.fetchall(sql1, arg1)
        log.info(f'port_info: {port_info}')
        old_port_list = ''
        for port in port_info:
            old_port_list += (port.get('eq_port') + '; ')

        form_var['old_port_list'] = old_port_list
        form_var['terminal_address'] = terminal_address
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def get_share_profit_summary(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['begin_time', str, True, '开始时间'],
        ['end_time', str, True, '结束时间'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        begin_time = form_var.get('begin_time')
        end_time = form_var.get('end_time')
        user_id = form_var.get('user_id')
        if user_id:
            sql = "select * from s_dis_profit_detail where create_time >= %s and create_time <= %s and state = %s and user_id = %s"
            arg = (begin_time, end_time, '0', user_id)
        else:
            sql = "select * from s_dis_profit_detail where create_time >= %s and create_time <= %s and state = %s"
            arg = (begin_time, end_time, '0', )
        result = db.fetchall(sql, arg)
        log.info(f'result: {result}')

        if user_id:
            sql1 = "select * from s_deduction_detail where create_time >= %s and create_time <= %s and state = %s and user_id = %s"
            arg1 = (begin_time, end_time, '0', user_id)
        else:
            sql1 = "select * from s_deduction_detail where create_time >= %s and create_time <= %s and state = %s"
            arg1 = (begin_time, end_time, '0', )
        result1 = db.fetchall(sql1, arg1)
        log.info(f'result1: {result1}')

        user_totals = {}
        for item in result:
            user_id = item['user_id']
            dis_money = item['dis_money']
            if user_id not in user_totals:
                user_totals[user_id] = 0.0
            user_totals[user_id] += dis_money

        log.info(f"user_totals: {user_totals}")

        deduction_totals = {}
        for item in result1:
            user_id = item['user_id']
            money = item['money']
            if user_id not in deduction_totals:
                deduction_totals[user_id] = 0.0
            deduction_totals[user_id] += money

        log.info(f"deduction_totals: {deduction_totals}")

        user_list = [
            {"user_id": uid, "money": format(total, '.2f'), "begin_time": begin_time, "end_time": end_time}
            for uid, total in user_totals.items()
        ]
        log.info(f"user_list: {user_list}")

        deduction_list = [
            {"user_id": uid, "deduct_money": format(money, '.2f'), "begin_time": begin_time, "end_time": end_time}
            for uid, money in deduction_totals.items()
        ]
        log.info(f"deduction_list: {deduction_list}")

        def merge_user_records_with_balance(income_list, deduction_list):
            merged_dict = {}

            # 处理收入记录
            for user in income_list:
                user_id = user['user_id']
                money = float(user['money'])  # 转换为浮点数方便计算
                merged_dict[user_id] = {
                    'user_id': user_id,
                    'money': user['money'],
                    'deduct_money': '0.00',
                    'begin_time': user['begin_time'],
                    'end_time': user['end_time'],
                    'real_money': f"{money:.2f}"  # 初始化余额等于收入
                }

            # 处理支出记录
            for deduct in deduction_list:
                user_id = deduct['user_id']
                deduct_value = float(deduct['deduct_money'])

                if user_id in merged_dict:
                    # 如果已有记录（收入），更新支出金额并重新计算余额
                    prev_balance = float(merged_dict[user_id]['balance'])
                    new_balance = prev_balance - deduct_value
                    merged_dict[user_id]['deduct_money'] = deduct['deduct_money']
                    merged_dict[user_id]['balance'] = f"{new_balance:.2f}"
                else:
                    # 如果只有支出，创建新记录（收入设为0）
                    merged_dict[user_id] = {
                        'user_id': user_id,
                        'money': '0.00',
                        'deduct_money': deduct['deduct_money'],
                        'begin_time': deduct['begin_time'],
                        'end_time': deduct['end_time'],
                        'real_money': f"{-deduct_value:.2f}"  # 余额为负支出
                    }

            # 转换为列表并按user_id排序
            result_list = sorted(merged_dict.values(), key=lambda x: x['user_id'])
            return result_list


        result_list = merge_user_records_with_balance(user_list, deduction_list)
        log.info(f'result_list： {result_list}')

        sql1 = "select wx_nickname from s_user_info where user_id = %s"
        table_data = []
        for data in result_list:
            user_id = data['user_id']
            user_info = db.fetchone(sql1, (user_id, ))
            if user_info:
                user_name = user_info.get('wx_nickname')
            else:
                data['user_name'] = "用户不存在"
            table_data.append(data)
        # table_data = []
        # table_data.append(result)
        form_var['table_data'] = table_data



        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def get_administrative_region_l2(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['region_id_1', int, True, '省']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        pid = form_var.get('region_id_1')
        sql = "select * from hup_region where pid = %s and level = %s"
        arg = (pid, '2')
        result = db.fetchall(sql, arg)
        log.info(f'result: {result}')
        table_data = []
        for data in result:
            table_data.append({'key': data.get('id'), 'value': data.get('name')})
        form_var['region_id_2_option'] = table_data
        form_var['region_id_2'] = ''
        form_var['region_id_3'] = ''
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def get_administrative_region_l3(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['region_id_2', int, True, '市']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        pid = form_var.get('region_id_2')
        sql = "select * from hup_region where pid = %s and level = %s"
        arg = (pid, '3')
        result = db.fetchall(sql, arg)
        log.info(f'result: {result}')
        table_data = []
        for data in result:
            table_data.append({'key': data.get('id'), 'value': data.get('name')})
        form_var['region_id_3_option'] = table_data
        form_var['region_id_3'] = ''
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise
