#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：index.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/7/22 16:03 
@Description :
'''
import json
import os

import requests
from admin_app.sys import public
import datetime
from admin_app.tools import handle

from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils.appCom import generate_download_file
from admin_app.utils.excelTool import ExcelTools


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


def get_region_info(request, data, resp):
    log = public.logger
    # 获取行政区域
    region_id = data.get('region_id')
    # form_var = data.get('form_var')
    # region_id = form_var.get('region_id')

    db = MySQLDB()
    region_info = []
    if not region_id:  # 没有区域id，获取省
        log.info(f'获取省')
        # 查询所有设备的区域
        sql_for_eq = """select distinct region_id_1 as region_id from s_eq_info where region_id_1 is not null """
        region_info = db.fetchall(sql_for_eq)
        log.info(f'省份：{region_info}')
    else:  # 有区域id，获取下一级
        sql_for_level = """select level from hup_region where id=%s"""
        level_info = db.fetchone(sql_for_level, (region_id,))
        level = level_info.get('level')
        if level == 1:  # 传的是省级，获取市级
            log.info(f'获取市')
            sql_for_eq = """select distinct region_id_2 as region_id from s_eq_info where region_id_1=%s and region_id_2 is not null """
            region_info = db.fetchall(sql_for_eq, (region_id,))
            log.info(f'市：{region_info}')

        elif level == 2:  #传的是市级，获取区县
            log.info(f'获取区县')
            sql_for_eq = """select distinct region_id_3 as region_id from s_eq_info where region_id_2=%s and region_id_3 is not null """
            region_info = db.fetchall(sql_for_eq, (region_id,))
            log.info(f'区县：{region_info}')
        elif level == 3:
            log.info(f'传入的是区县，达到最下级，无法获取下一级')

    # 匹配中文名
    region_list = []
    for item in region_info:
        region_id = item['region_id']
        sql_for_cn_name = """select name from hup_region where id=%s"""
        cn_name = db.fetchone(sql_for_cn_name, (region_id,))
        data = {
            'value': region_id,
            'label': cn_name.get('name')
        }
        region_list.append(data)

    log.info(f'行政区域信息：{region_list}')

    resp['region_list'] = region_list
    return resp


def get_large_screen_info(request, data, resp):
    log = public.logger
    # 获取大屏信息
    region_id = data.get('region_id', None)
    if not region_id:
        region_id = None
    log.info(f'区域信息：{region_id}')
    db = MySQLDB()
    # 1）查近七天订单数量
    sql_for_order_count = """
        SELECT
            dates.date AS order_date,
            COUNT(view_order_link_region.order_id) AS order_count  -- 不需要 IFNULL，COUNT 会自动处理 NULL
        FROM (
            SELECT CURDATE() - INTERVAL 0 DAY AS date
            UNION SELECT CURDATE() - INTERVAL 1 DAY
            UNION SELECT CURDATE() - INTERVAL 2 DAY
            UNION SELECT CURDATE() - INTERVAL 3 DAY
            UNION SELECT CURDATE() - INTERVAL 4 DAY
            UNION SELECT CURDATE() - INTERVAL 5 DAY
            UNION SELECT CURDATE() - INTERVAL 6 DAY
        ) AS dates
        LEFT JOIN view_order_link_region 
            ON DATE(view_order_link_region.create_time) = dates.date
            -- 关键部分：使用条件区域筛选
            AND (view_order_link_region.region_id_3 = %s OR %s IS NULL)  -- ? 是传入的参数占位符
        GROUP BY
            dates.date
        ORDER BY
            dates.date ASC;
    """
    order_count_info = db.fetchall(sql_for_order_count, (region_id, region_id,))
    log.info(f'近七天订单数量：{order_count_info}')


    # 2) 查离线设备数据
    sql_for_offline_eq = """
        select eq_id as deviceNo,
        site_name as area,
        admin_name as manager,
        admin_phone as phone
        from view_eq_link_admin_info
        where conn_state='0'
        and identify_id=1
        and (region_id_3=%s or %s is NULL)
    """
    offline_eq_info = db.fetchall(sql_for_offline_eq, (region_id, region_id,))
    log.info(f'离线设备：{offline_eq_info}')


    # 3） 异常订单

    sql_for_abnormal_order = """
    select a.order_id as orderNo,
    a.eq_id as deviceNo,
    b.wx_nickname as username,
    b.phone_number as phone
    from s_order_info a 
    left join s_user_info b 
    on a.user_id=b.user_id
    left join s_eq_info c
    on a.eq_id=c.eq_id
    where (a.remark like '%%超时%%'
    or a.remark like '%%异常%%'
    or a.remark like '%%错误%%')
    and (c.region_id_3=%s or %s is NULL)    
    """
    abnormal_order_info = db.fetchall(sql_for_abnormal_order, (region_id, region_id,))
    log.info(f'异常订单：{abnormal_order_info}')


    # 4）近七天订单收益
    sql_for_order_profit = """
        SELECT
            dates.date AS order_date,
            COALESCE(SUM(view_order_link_region.use_money), 0) AS profit_money,  -- 不需要 IFNULL，COUNT 会自动处理 NULL
            COALESCE(SUM(view_order_link_region.elec_cost), 0) AS elec_cost
        FROM (
            SELECT CURDATE() - INTERVAL 0 DAY AS date
            UNION SELECT CURDATE() - INTERVAL 1 DAY
            UNION SELECT CURDATE() - INTERVAL 2 DAY
            UNION SELECT CURDATE() - INTERVAL 3 DAY
            UNION SELECT CURDATE() - INTERVAL 4 DAY
            UNION SELECT CURDATE() - INTERVAL 5 DAY
            UNION SELECT CURDATE() - INTERVAL 6 DAY
        ) AS dates
        LEFT JOIN view_order_link_region 
            ON DATE(view_order_link_region.create_time) = dates.date
            -- 关键部分：使用条件区域筛选
            AND (view_order_link_region.region_id_3 = %s OR %s IS NULL)  
        GROUP BY
            dates.date
        ORDER BY
            dates.date ASC;
    
    """
    order_profit_info = db.fetchall(sql_for_order_profit, (region_id, region_id,))
    log.info(f'近七天订单收益-用电成本：{order_profit_info}')

    # 5）近七天用电成本
    # 数据与4）一起查
    # 格式化图形数据
    xdata = []
    ydata1 = []
    ydata2 = []
    for item in order_profit_info:
        date = item.get('order_date')
        profit = item.get('profit_money')
        elec_cost = item.get('elec_cost')
        xdata.append(date.strftime('%m/%d'))
        ydata1.append(profit)
        ydata2.append(elec_cost)
    log.info(f'折线图数据：x:{xdata}, y1:{ydata1}, y2:{ydata2}')


    # 6)查设备数量、在线数量、离线数量
    sql_for_eq_count = """
        SELECT
            COUNT(*) AS total_count,                          -- 设备总数量
            COUNT(CASE WHEN conn_state = '1' THEN 1 END) AS online_count,
            COUNT(CASE WHEN conn_state = '0' THEN 1 END) AS offline_count
        FROM s_eq_info
        where region_id_3=%s or %s is NULL
    """
    eq_count_info = db.fetchone(sql_for_eq_count, (region_id,region_id,))
    log.info(f'设备数量：{eq_count_info}')


    # 7)查用户数量
    sql_for_user_count = """
        select count(*) AS user_count
        from s_user_info
    """
    user_count_info = db.fetchone(sql_for_user_count)
    log.info(f'用户数量：{user_count_info}')

    # 8）今日充值金额
    sql_for_today_recharge = """
    SELECT COALESCE(SUM(change_money), 0) AS today_recharge_total
    FROM s_wx_tran_detail
    WHERE 
        -- 确保覆盖全天范围 (00:00:00 到 23:59:59)
        create_time >= CURDATE()
        AND create_time < CURDATE() + INTERVAL 1 DAY
        and change_type='in' 
        and state='2'
    """
    today_recharge_total = db.fetchone(sql_for_today_recharge)
    log.info(f'今日钱包充值：{today_recharge_total}')

    # 8）今日电卡充值金额
    sql_for_today_card_recharge = """
        SELECT COALESCE(SUM(change_money), 0) AS today_card_recharge_total
        FROM s_wx_tran_card_detail
        WHERE 
            -- 确保覆盖全天范围 (00:00:00 到 23:59:59)
            create_time >= CURDATE()
            AND create_time < CURDATE() + INTERVAL 1 DAY
            and change_type='in' 
            and state='2'
        """
    today_card_recharge_total = db.fetchone(sql_for_today_card_recharge)
    log.info(f'今日电卡充值：{today_card_recharge_total}')

    # 9）今日订单数
    sql_for_today_order_count = """
        SELECT count(*) AS today_order_count
        FROM s_order_info a
        left join s_eq_info b
        on a.eq_id = b.eq_id
        WHERE 
            -- 确保覆盖全天范围 (00:00:00 到 23:59:59)
            a.create_time >= CURDATE()
        AND a.create_time < CURDATE() + INTERVAL 1 DAY
        and (b.region_id_3=%s or %s is NULL)
    """
    today_order_count = db.fetchone(sql_for_today_order_count, (region_id, region_id,))
    log.info(f'今日订单数量：{today_order_count}')
    # 10）当前订单数
    sql_for_now_order_count = """
        SELECT count(*) AS now_order_count
        FROM s_order_info a
        left join s_eq_info b
        on a.eq_id = b.eq_id
        WHERE 
            -- 确保覆盖全天范围 (00:00:00 到 23:59:59)
            a.create_time >= CURDATE()
        AND a.create_time < CURDATE() + INTERVAL 1 DAY
        and a.state='1'
        and (b.region_id_3=%s or %s is NULL)
    """
    now_order_count = db.fetchone(sql_for_now_order_count, (region_id, region_id,))
    log.info(f'当前订单数量：{now_order_count}')

    # 11）当前功率
    sql_for_now_power = """
        SELECT COALESCE(SUM(power), 0) AS now_power
        FROM s_eq_port a 
        left join s_eq_info b
        on a.eq_id = b.eq_id
        WHERE b.region_id_3=%s or %s is NULL
    """
    now_power = db.fetchone(sql_for_now_power, (region_id,region_id,))
    log.info(f'当前总功率：{now_power}')

    screenData = {
    'terminal_count': eq_count_info.get('total_count'),
    'online_count': eq_count_info.get('online_count'),
    'no_online_count': eq_count_info.get('offline_count'),
    'member_count': user_count_info.get('user_count'),
    'today_recharge_amount': today_recharge_total.get('today_recharge_total') + today_card_recharge_total.get('today_card_recharge_total'),
    'today_order_amount': today_order_count.get('today_order_count'),
    'current_order_num': now_order_count.get('now_order_count'),
    'scale_p': 500, # 刻度比例
    'ave_p': now_power.get('now_power'), # 当前功率
    'unit': "W", # 功率单位
    }

    resp['order_count_info'] = order_count_info
    resp['offline_eq_info'] = offline_eq_info
    resp['abnormal_order_info'] = abnormal_order_info
    resp['profit_and_cost'] = {
        'xdata': xdata,  # 日期
        'ydata1': ydata1, # 收益
        'ydata2': ydata2  # 用电成本
    }
    resp['screen_data'] = screenData

    return resp

