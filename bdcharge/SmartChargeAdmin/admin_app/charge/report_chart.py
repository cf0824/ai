#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：report_chart.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/20 17:07 
@Description :
'''
from admin_app.sys import public
import datetime
from collections import defaultdict

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


def get_profit_detail_by_site(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    try:
        db = MySQLDB()
        begin_date = form_var.get('begin_date')
        end_date = form_var.get('end_date')
        site_id = form_var.get('site_id')
        if not begin_date:
            begin_date = '2025-01-01'
        if not end_date:
            end_date = datetime.date.today().strftime('%Y-%m-%d')
        log.info(f'begin_date: {begin_date}, end_date: {end_date}')
        if begin_date > end_date or end_date > (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                '%Y-%m-%d'):
            return err_msg(msg='请选择正确的时间区间')
        # 查站点
        site_list = []
        if not site_id:
            sql_site_id = "SELECT DISTINCT site_id FROM s_order_info WHERE state = '2' AND end_time BETWEEN %s AND %s"
            args = (begin_date, end_date)
            site_info = db.fetchall(sql_site_id, args)
            for site in site_info:
                site_list.append(site.get('site_id'))
        else:
            site_list.append(site_id)
        log.info(f'site_list: {site_list}')

        # 查订单
        sql_order = """
        select 
        site_id,
        COALESCE(SUM(use_money), 0) AS total_profit,
        COALESCE(sum(elec_cost), 0) as total_elec_cost,
        COALESCE(count(order_id), 0) as order_count
        from s_order_info 
        where site_id in %s 
        and state = '2' 
        and end_time BETWEEN %s AND %s
        group by site_id
        """
        args_order = (site_list, begin_date, end_date)
        order_info = db.fetchall(sql_order, args_order)
        log.info(f'order_info: {order_info}')
        if not order_info:
            form_var['table_data'] = []
            resp['form_var'] = form_var
            resp['respmsg'] = '该筛选条件下没有订单'
            return resp


        # 查设备数量
        sql_eq = """
        select 
        e.site_id, 
        s.site_name,
        COUNT(eq_id) as eq_count 
        from s_eq_info e 
        left join s_site_info s 
        on e.site_id = s.site_id
        where e.site_id in %s 
        GROUP BY e.site_id
        """
        args_eq = (site_list,)
        eq_info = db.fetchall(sql_eq, args_eq)
        log.info(f'eq_info: {eq_info}')

        # 查分润
        sql_dis_profit = """
        SELECT 
          soi.site_id,
          COALESCE(SUM(sdp.dis_money), 0) AS total_share_money
        FROM s_order_info soi  -- 以订单表作为主表
        LEFT JOIN s_dis_profit_detail sdp 
          ON soi.order_id = sdp.order_id   -- LEFT JOIN保留所有订单
        WHERE 
          soi.site_id IN %s 
          AND soi.state = '2'
          AND soi.end_time BETWEEN %s AND %s
        GROUP BY soi.site_id;
        """
        args_dis_profit = (site_list, begin_date, end_date)
        dis_profit = db.fetchall(sql_dis_profit, args_dis_profit)
        log.info(f'dis_profit: {dis_profit}')

        merged = defaultdict(dict)

        # 合并 order_info
        for order in order_info:
            site = order['site_id']
            merged[site].update({
                'site_id': site,
                'total_profit': order['total_profit'],
                'total_elec_cost': order['total_elec_cost'],
                'order_count': order['order_count']
            })

        # 合并 dis_profit
        for dp in dis_profit:
            site = dp['site_id']
            merged[site].update({
                'total_share_money': dp['total_share_money']
            })

        # 合并 eq_info
        for eq in eq_info:
            site = eq['site_id']
            merged[site].update({
                'eq_count': eq['eq_count'],
                'site_name': eq['site_name']
            })

        # 生成排序后的结果列表
        result = sorted(merged.values(), key=lambda x: x['site_id'])
        log.info(f'result: {result}')
        for item in result:
            item['mch_profit'] = round((item['total_profit'] - item['total_share_money'] - item['total_elec_cost']), 4)
            item['begin_date'] = begin_date
            item['end_date'] = end_date

        log.info(f'result: {result}')
        table_data = result

        form_var['table_data'] = table_data
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def get_profit_detail_by_eq(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    try:
        db = MySQLDB()
        begin_date = form_var.get('begin_date')
        end_date = form_var.get('end_date')
        site_id = form_var.get('site_id')
        eq_id = form_var.get('eq_id')
        if not begin_date:
            begin_date = '2025-01-01'
        if not end_date:
            end_date = datetime.date.today().strftime('%Y-%m-%d')
        log.info(f'begin_date: {begin_date}, end_date: {end_date}')
        if begin_date > end_date or end_date > (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                '%Y-%m-%d'):
            return err_msg(msg='请选择正确的时间区间')
        # 站点
        site_list = []
        if not site_id:
            sql_site_id = "SELECT DISTINCT site_id FROM s_order_info WHERE state = '2' AND end_time BETWEEN %s AND %s"
            args = (begin_date, end_date)
            site_info = db.fetchall(sql_site_id, args)
            for site in site_info:
                site_list.append(site.get('site_id'))
        else:
            site_list.append(site_id)
        log.info(f'site_list: {site_list}')

        # 查设备
        eq_list = []
        if not eq_id:
            sql_eq_id = "SELECT DISTINCT eq_id FROM s_order_info WHERE site_id in %s and state = '2' AND end_time BETWEEN %s AND %s"
            args = (site_list, begin_date, end_date)
            eq_info = db.fetchall(sql_eq_id, args)
            for eq in eq_info:
                eq_list.append(eq.get('eq_id'))
        else:
            eq_list.append(eq_id)
        log.info(f'eq_list: {eq_list}')


        # 查订单
        sql_order = """
        select 
        eq_id, 
        site_id,
        COALESCE(SUM(use_money), 0) AS total_profit,
        COALESCE(sum(elec_cost), 0) as total_elec_cost,
        COALESCE(count(order_id), 0) as order_count
        from s_order_info 
        where site_id in %s and eq_id in %s
        and state = '2' 
        and end_time BETWEEN %s AND %s
        group by eq_id, site_id
        """
        args_order = (site_list, eq_list, begin_date, end_date)
        order_info = db.fetchall(sql_order, args_order)
        log.info(f'order_info: {order_info}')
        if not order_info:
            form_var['table_data'] = []
            resp['form_var'] = form_var
            resp['respmsg'] = '该筛选条件下没有订单'
            return resp


        # 查设备名称、通讯地址
        sql_eq = """
        select 
        e.eq_id, 
        e.terminal_address,
        s.site_name 
        from s_eq_info e
        left join s_site_info s
        on e.site_id = s.site_id
        where e.site_id in %s and e.eq_id in %s
        GROUP BY e.eq_id
        """
        args_eq = (site_list, eq_list)
        eq_info = db.fetchall(sql_eq, args_eq)
        log.info(f'eq_info: {eq_info}')

        # 查分润
        sql_dis_profit = """
        SELECT 
          soi.eq_id,
          COALESCE(SUM(sdp.dis_money), 0) AS total_share_money
        FROM s_order_info soi
        LEFT JOIN s_dis_profit_detail sdp 
          ON soi.order_id = sdp.order_id  -- 通过LEFT JOIN保留无分润订单
          AND sdp.order_id IS NOT NULL    -- 显式声明关联条件（可选）
        WHERE 
          soi.site_id IN %s 
          AND soi.eq_id IN %s
          AND soi.state = '2'
          AND soi.end_time BETWEEN %s AND %s
        GROUP BY soi.eq_id;
        """
        args_dis_profit = (site_list, eq_list, begin_date, end_date)
        dis_profit = db.fetchall(sql_dis_profit, args_dis_profit)
        log.info(f'dis_profit: {dis_profit}')

        merged = defaultdict(dict)

        # 合并 order_info
        for order in order_info:
            eq = order['eq_id']
            merged[eq].update({
                'eq_id': eq,
                'site_id': order['site_id'],
                'total_profit': order['total_profit'],
                'total_elec_cost': order['total_elec_cost'],
                'order_count': order['order_count']
            })

        # 合并 dis_profit
        for dp in dis_profit:
            eq = dp['eq_id']
            merged[eq].update({
                'total_share_money': dp['total_share_money']
            })

        # 合并 eq_info
        for eq_dict in eq_info:
            eq_id = eq_dict['eq_id']
            merged[eq_id].update({
                'terminal_address': eq_dict['terminal_address'],
                'site_name': eq_dict['site_name']
            })

        # 生成排序后的结果列表
        result = sorted(merged.values(), key=lambda x: x['eq_id'])
        log.info(f'result: {result}')
        for item in result:
            item['mch_profit'] = round((item['total_profit'] - item['total_share_money'] - item['total_elec_cost']), 4)
            item['begin_date'] = begin_date
            item['end_date'] = end_date

        log.info(f'result: {result}')
        table_data = result
        # table_data = []
        # for data in user_list:
        #     user_id = data['user_id']
        #     user_info = db.fetchone(sql1, (user_id, ))
        #     user_name = user_info.get('wx_nickname')
        #     data['user_name'] = user_name
        #     table_data.append(data)
        # # table_data = []
        # # table_data.append(result)

        form_var['table_data'] = table_data
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
    raise

def get_share_profit_detail_by_site(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')


    try:
        db = MySQLDB()
        begin_date = form_var.get('begin_date')
        end_date = form_var.get('end_date')
        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        if not begin_date:
            begin_date = '2025-01-01'
        if not end_date:
            end_date = datetime.date.today().strftime('%Y-%m-%d')
        log.info(f'begin_date: {begin_date}, end_date: {end_date}')
        if begin_date > end_date or end_date > (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                '%Y-%m-%d'):
            return err_msg(msg='请选择正确的时间区间')
        # 站点
        site_list = []
        if not site_id:
            sql_site_id = "SELECT DISTINCT site_id FROM s_dis_profit_detail WHERE create_time BETWEEN %s AND %s"
            args = (begin_date, end_date)
            site_info = db.fetchall(sql_site_id, args)
            for site in site_info:
                site_list.append(site.get('site_id'))
        else:
            site_list.append(site_id)
        log.info(f'site_list: {site_list}')

        # 查用户
        user_list = []
        if not user_id:
            sql_user_id = "SELECT DISTINCT user_id FROM s_dis_profit_detail WHERE site_id in %s AND create_time BETWEEN %s AND %s"
            args = (site_list, begin_date, end_date)
            user_info = db.fetchall(sql_user_id, args)
            for user in user_info:
                user_list.append(user.get('user_id'))
        else:
            user_list.append(user_id)
        log.info(f'user_list: {user_list}')


        # 查订单
        sql_share = """
        select 
        d.user_id, 
        u.wx_nickname as user_name,
        d.site_id,
        s.site_name as site_name,
        d.dis_rate,
        COALESCE(SUM(d.dis_money), 0) AS dis_money,
        COALESCE(count(d.order_id), 0) as share_count,
        COALESCE(SUM(CASE WHEN d.state = '1' THEN d.dis_money ELSE 0 END), 0) AS already_shared,
        COALESCE(SUM(CASE WHEN d.state = '0' THEN d.dis_money ELSE 0 END), 0) AS pending_share         
        from s_dis_profit_detail d 
        left join s_user_info u on d.user_id = u.user_id
        left join s_site_info s on d.site_id = s.site_id
        where d.site_id in %s and d.user_id in %s
        and d.create_time BETWEEN %s AND %s
        group by d.user_id, d.site_id, d.dis_rate
        """
        args_share = (site_list, user_list, begin_date, end_date)
        share_info = db.fetchall(sql_share, args_share)
        log.info(f'share_info: {share_info}')
        if not share_info:
            form_var['table_data'] = []
            resp['form_var'] = form_var
            resp['respmsg'] = '该筛选条件下没有分润'
            return resp

        for item in share_info:
            item['begin_date'] = begin_date
            item['end_date'] = end_date

        log.info(f'share_info: {share_info}')
        table_data = share_info


        form_var['table_data'] = table_data
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
    raise


def get_recharge_detail_by_time(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')


    try:
        db = MySQLDB()
        begin_date = form_var.get('begin_date')
        end_date = form_var.get('end_date')
        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        if not begin_date:
            begin_date = '2025-01-01'
        if not end_date:
            end_date = datetime.date.today().strftime('%Y-%m-%d')
        log.info(f'begin_date: {begin_date}, end_date: {end_date}')
        if begin_date > end_date or end_date > (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'):
            return err_msg(msg='请选择正确的时间区间')

        # 查充值
        sql_recharge = """
        select 
        COALESCE(SUM(change_money), 0) AS recharge_amount       
        from s_wx_tran_detail
        where state = '2' and change_type = 'in'
        and finish_time BETWEEN %s AND %s
        """
        args_recharge = (begin_date, end_date)
        recharge_info = db.fetchall(sql_recharge, args_recharge)
        log.info(f'recharge_info: {recharge_info}')

        # 查卡充值
        sql_card_recharge = """
                select 
                COALESCE(SUM(change_money), 0) AS card_recharge_amount       
                from s_wx_tran_card_detail
                where state = '2' and change_type = 'in'
                and finish_time BETWEEN %s AND %s
                """
        args_card_recharge = (begin_date, end_date)
        card_recharge_info = db.fetchall(sql_card_recharge, args_card_recharge)
        log.info(f'card_recharge_info: {card_recharge_info}')

        # 查提现
        sql_cashout = """
                select 
                COALESCE(SUM(amount), 0) AS cashout_amount       
                from s_wx_cashout_detail_1
                where user_varify_state = '1'
                and finish_time BETWEEN %s AND %s
                """
        args_cashout = (begin_date, end_date)
        cashout_info = db.fetchall(sql_cashout, args_cashout)
        log.info(f'cashout_info: {cashout_info}')

        # 查在线支付
        sql_charge_online = """
                select 
                COALESCE(SUM(charge_money), 0) as in_amount,
                COALESCE(SUM(return_money), 0) as out_amount
                from s_order_info 
                where charge_type = 'money' 
                and pay_way = 'online' 
                and end_time BETWEEN %s AND %s
        """
        args_charge_online = (begin_date, end_date)
        charge_online = db.fetchall(sql_charge_online, args_charge_online)
        log.info(f'charge_online: {charge_online}')

        table_list = []
        data = {
            "recharge_amount": recharge_info[0].get("recharge_amount"),
            "card_recharge_amount": card_recharge_info[0].get("card_recharge_amount"),
            "cashout_amount": cashout_info[0].get("cashout_amount"),
            "in_amount": charge_online[0].get("in_amount"),
            "out_amount": charge_online[0].get("out_amount"),
            "begin_date": begin_date,
            "end_date": end_date
        }
        table_list.append(data)

        form_var['table_data'] = table_list
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
    raise


def get_user_wallet_sum(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')


    try:
        db = MySQLDB()

        # 查钱包
        sql_user_wallet = """
                        select 
                        COALESCE(SUM(real_money), 0) as real_money,
                        COALESCE(SUM(ok_money), 0) as ok_money,
                        COALESCE(SUM(ice_money), 0) as ice_money,
                        COALESCE(SUM(gift_money), 0) as gift_money
                        from view_user_account_ok v 
                        join s_user_info u on v.user_id = u.user_id 
                        where u.state = '0'

                """

        user_wallet = db.fetchall(sql_user_wallet)
        log.info(f'user_wallet: {user_wallet}')

        table_list = []
        data = {
            "real_money": user_wallet[0].get("real_money"),
            "ok_money": user_wallet[0].get("ok_money"),
            "ice_money": user_wallet[0].get("ice_money"),
            "gift_money": user_wallet[0].get("gift_money")
        }
        table_list.append(data)
        log.info(f'table_list: {table_list}')

        form_var['table_data'] = table_list
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
    raise

def get_profit_detail_by_region(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    try:
        db = MySQLDB()
        begin_date = form_var.get('begin_date')
        end_date = form_var.get('end_date')
        site_id = form_var.get('site_id')
        if not begin_date:
            begin_date = '2025-01-01'
        if not end_date:
            end_date = datetime.date.today().strftime('%Y-%m-%d')
        log.info(f'begin_date: {begin_date}, end_date: {end_date}')
        if begin_date > end_date or end_date > (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                '%Y-%m-%d'):
            return err_msg(msg='请选择正确的时间区间')
        # 查站点
        site_list = []
        if not site_id:
            sql_site_id = "SELECT DISTINCT site_id FROM s_order_info WHERE state = '2' AND end_time BETWEEN %s AND %s"
            args = (begin_date, end_date)
            site_info = db.fetchall(sql_site_id, args)
            for site in site_info:
                site_list.append(site.get('site_id'))
        else:
            site_list.append(site_id)
        log.info(f'site_list: {site_list}')

        # 查订单
        sql_order = """
        select 
        site_id,
        COALESCE(SUM(use_money), 0) AS total_profit,
        COALESCE(sum(elec_cost), 0) as total_elec_cost,
        COALESCE(count(order_id), 0) as order_count
        from s_order_info 
        where site_id in %s 
        and state = '2' 
        and end_time BETWEEN %s AND %s
        group by site_id
        """
        args_order = (site_list, begin_date, end_date)
        order_info = db.fetchall(sql_order, args_order)
        log.info(f'order_info: {order_info}')
        if not order_info:
            form_var['table_data'] = []
            resp['form_var'] = form_var
            resp['respmsg'] = '该筛选条件下没有订单'
            return resp

        # 查设备数量
        sql_eq = """
        select 
        e.site_id, 
        s.site_name,
        COUNT(eq_id) as eq_count 
        from s_eq_info e 
        left join s_site_info s 
        on e.site_id = s.site_id
        where e.site_id in %s 
        GROUP BY e.site_id
        """
        args_eq = (site_list,)
        eq_info = db.fetchall(sql_eq, args_eq)
        log.info(f'eq_info: {eq_info}')

        # 查分润
        sql_dis_profit = """
        SELECT 
          soi.site_id,
          COALESCE(SUM(sdp.dis_money), 0) AS total_share_money
        FROM s_order_info soi  -- 以订单表作为主表
        LEFT JOIN s_dis_profit_detail sdp 
          ON soi.order_id = sdp.order_id   -- LEFT JOIN保留所有订单
        WHERE 
          soi.site_id IN %s 
          AND soi.state = '2'
          AND soi.end_time BETWEEN %s AND %s
        GROUP BY soi.site_id;
        """
        args_dis_profit = (site_list, begin_date, end_date)
        dis_profit = db.fetchall(sql_dis_profit, args_dis_profit)
        log.info(f'dis_profit: {dis_profit}')

        merged = defaultdict(dict)

        # 合并 order_info
        for order in order_info:
            site = order['site_id']
            merged[site].update({
                'site_id': site,
                'total_profit': order['total_profit'],
                'total_elec_cost': order['total_elec_cost'],
                'order_count': order['order_count']
            })

        # 合并 dis_profit
        for dp in dis_profit:
            site = dp['site_id']
            merged[site].update({
                'total_share_money': dp['total_share_money']
            })

        # 合并 eq_info
        for eq in eq_info:
            site = eq['site_id']
            merged[site].update({
                'eq_count': eq['eq_count'],
                'site_name': eq['site_name']
            })

        # 生成排序后的结果列表
        result = sorted(merged.values(), key=lambda x: x['site_id'])
        log.info(f'result: {result}')
        for item in result:
            item['mch_profit'] = round((item['total_profit'] - item['total_share_money'] - item['total_elec_cost']), 4)
            item['begin_date'] = begin_date
            item['end_date'] = end_date

        log.info(f'result: {result}')
        table_data = result

        form_var['table_data'] = table_data
        resp['form_var'] = form_var
        # resp['table_data'] = table_data

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise
    