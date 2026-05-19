#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：user.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/8 14:21 
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

def update_user_info(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['user_id', int, True, '用户id']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        user_id = form_var.get('user_id')
        identity = form_var.get('identity')
        state = form_var.get('state')
        remark_name = form_var.get('remark_name')
        data = {
            'identity': identity,
            'state': state,
            'remark_name': remark_name
        }
        db.update('s_user_info', data, {'user_id': user_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def change_gift_money(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    form_var['change_gift_money'] = float(form_var.get('change_gift_money'))
    verify_dict = [
        ['user_id', int, True, '用户id'],
        ['change_gift_money', float, True, '赠送余额'],
        ['change_type', str, True, '增加/减少']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        user_id = form_var.get('user_id')
        change_type = form_var.get('change_type')
        change_gift_money = float(form_var.get('change_gift_money'))
        sql = "select * from view_user_account_ok where user_id = %s"
        arg = (user_id,)
        result = db.fetchone(sql, arg)
        log.info(f'result:{result}')
        gift_money = result.get('gift_money')
        if not gift_money:
            gift_money = 0.00
        if change_type == '1':
            new_gift_money = change_gift_money + gift_money
            remark = '管理员赠送余额'
        elif change_type == '2':
            new_gift_money = gift_money - change_gift_money
            remark = '管理员扣除赠送余额'
        else:
            return err_msg(msg='类型错误')
        if new_gift_money < 0:
            return err_msg(msg=f'扣得太多了！赠送余额不能小于0')
        data = {
            'gift_money': new_gift_money
        }
        data1 = {
            "change_type": 'in',
            # "change_money":
        }
        db.update('view_user_account_ok', data, {"user_id": user_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def add_user_identity(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['identify', str, True, '身份']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        identify = form_var.get('identify')
        data = {
            'identify': identify,
            'create_time': datetime.datetime.now()
        }
        db.insert('s_user_identify', data)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def update_user_identity(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['identify_id', int, True, 'id'],
        ['identify', str, True, '身份']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        identify_id = form_var.get('identify_id')
        identify = form_var.get('identify')
        data = {
            'identify': identify,
            'update_time': datetime.datetime.now()
        }
        db.update('s_user_identify', data, {"identify_id": identify_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def recharge_money(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    form_var['money'] = float(form_var.get('money'))
    verify_dict = [
        ['user_id', int, True, '用户id'],
        ['money', float, True, '充值金额'],
        ['remark', str, True, '备注']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        user_id = form_var.get('user_id')
        money = float(form_var.get('money'))
        remark = form_var.get('remark')
        if money <= 0.00:
            return err_msg(msg=f'金额需大于0')
        sql = "select * from view_user_account_ok where user_id = %s"
        arg = (user_id,)
        result = db.fetchone(sql, arg)
        log.info(f'result:{result}')
        real_money = result.get('real_money')
        ok_money = result.get('ok_money')
        new_real_money = real_money + money
        new_ok_money = ok_money + money

        data1 = {
            "real_money": new_real_money,
            "ok_money": new_ok_money
        }
        db.update('view_user_account_ok', data1, {'user_id': user_id})
        data2 = {
            "account": new_real_money,
        }
        db.update('s_user_info', data2, {'user_id': user_id})


        data3 = {
            "change_type": "in",
            "change_money": money,
            "now_money": new_real_money,
            "user_id": user_id,
            "create_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "remark": remark
        }
        db.insert('s_account_detail', data3)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def order_error_correction(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    form_var['error_money'] = float(form_var.get('error_money'))
    verify_dict = [
        ['order_id', str, True, '订单号'],
        ['user_id', int, True, '用户id'],
        ['error_money', float, True, '纠错金额'],
        ['remark', str, True, '备注']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        user_id = form_var.get('user_id')
        order_id = form_var.get('order_id')
        error_money = float(form_var.get('error_money'))
        remark = form_var.get('remark')
        if error_money <= 0.00:
            return err_msg(msg=f'金额需大于0')
        sql = "select * from view_user_account_ok where user_id = %s"
        arg = (user_id,)
        result = db.fetchone(sql, arg)
        log.info(f'result:{result}')
        real_money = result.get('real_money')
        ok_money = result.get('ok_money')
        new_real_money = real_money + error_money
        new_ok_money = ok_money + error_money

        data1 = {
            "real_money": new_real_money,
            "ok_money": new_ok_money
        }
        db.update('view_user_account_ok', data1, {'user_id': user_id})
        data2 = {
            "account": new_real_money,
        }
        db.update('s_user_info', data2, {'user_id': user_id})


        data3 = {
            "change_type": "in",
            "change_money": error_money,
            "now_money": new_real_money,
            "user_id": user_id,
            "create_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "remark": remark
        }
        db.insert('s_account_detail', data3)

        # 消费记录中插入负值
        # 查原消费记录
        o_order_sql = "select * from s_order_info where user_id = %s and order_id = %s"
        o_order = db.fetchone(o_order_sql, (user_id, order_id,))
        log.info(f'原订单：{o_order}')
        o_order['use_money'] = -error_money
        o_order['order_id'] = 'error' + order_id
        o_order['remark'] = '订单纠错，订单号为error前缀加原订单号，除了使用金额为纠错金额，其余的和原订单一致'
        log.info(f'修改过后的订单信息:{o_order}')
        db.insert('s_order_info', o_order)
        # 分润：
        eq_id = o_order.get('eq_id', None)
        use_money = -error_money
        site_id = o_order.get('site_id')
        log.info(f'开始分账---订单：error{order_id}, 设备：{eq_id}, 使用金额：{use_money}')

        # 查询站点负责人
        sql_for_admin = "select * from s_dis_profit_cfg where site_id=%s"
        admin_users = db.fetchall(sql_for_admin, (site_id,))
        for admin_user in admin_users:
            dis_rate = admin_user.get('dis_rate')
            user_id = admin_user.get('user_id')
            dis_money = use_money * dis_rate
            log.info(f'分账详情--分账人：{user_id}, 比例：{dis_rate}, 所分金额：{dis_money}')
            data5 = {
                "order_id": 'error' + order_id,
                "eq_id": o_order.get('eq_id'),
                "site_id": o_order.get('site_id'),
                "order_money": -error_money,
                "dis_rate": dis_rate,
                "dis_money": dis_money,
                "create": datetime.datetime.now(),
                "state": '0'

            }
            db.insert('s_dis_profit_detail', data5)

        # 纠错表加记录
        data6 = {
            "order_id": order_id,
            "user_id": user_id,
            "error_money": error_money,
            "remark": remark,
            "create_time": datetime.datetime.now(),
            "create_by": public.user_id
        }
        db.insert('s_order_error_correction', data6)
        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise
    