#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_card_order.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/7/21 14:24 
@Description : 处理刷卡订单开启
'''
import time
import datetime

import os
import sys
pwd = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(pwd)
parent_dir_ = os.path.dirname(parent_dir)
print(pwd)
print(parent_dir)
print(parent_dir_)
print(sys.path)
sys.path.append(pwd)
sys.path.append(parent_dir)
sys.path.append(parent_dir_)
print(sys.path)
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()

from app.models import *

from app.utils.handle_order import HandleOrder
from app.utils.get_seq import Get_SeqNo
from app.shell import req_term
from app.command.tools.ApiTool import ApiTool
import json

handleorder = HandleOrder(log)
apitool = ApiTool(log)

# def split_string(s, length):
#     """
#     按照指定的长度拆分字符串。
#
#     :param s: 要拆分的字符串
#     :param length: 每个子字符串的长度
#     :return: 拆分后的字符串列表
#     """
#     # 使用列表推导式和切片操作来拆分字符串
#     return [s[i:i + length] for i in range(0, len(s), length)]
#
# def str_reverse(str, num=2):
#     """
#     字符串倒置
#     :param str:
#     :param num:
#     :return:
#     """
#     str_list = split_string(str, num)
#     reversed_list = str_list[::-1]
#     reversed_str = ''.join(reversed_list)
#     return reversed_str

def get_order_start_task():
    """
    获取订单开启任务
    :return:
    """
    tasks = SOrderCardPre.objects.filter(state='0')
    return tasks

def handle_card_order_start(order):
    id = order.id
    terminal_address = order.terminal_address
    eq_port = order.eq_port
    card_num = order.card_num

    eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
    card_info = SCardsInfo.objects.filter(card_num=card_num)
    OrderNumber_ = Get_SeqNo("CHARGE_ORDER")[-10:]
    if int(OrderNumber_) >= 4294967295:
        log.info(f'订单号超限')
        SOrderCardPre.objects.filter(id=id).update(
            state='-1',
            handle_time=datetime.datetime.now(),
            remark='订单号超限'
        )
    else:
        SOrderCardPre.objects.filter(id=id).update(
            state='1',
            handle_time=datetime.datetime.now()
        )
        order_no = hex(int(OrderNumber_)).lstrip('0x').zfill(8).upper()

        # 设备计价规则
        eq_fee_type = eq_info[0].fee_type
        eq_fee_no = eq_info[0].fee_no

        # 创建订单需要的信息
        site_id = eq_info[0].site_id
        eq_id = eq_info[0].eq_id
        user_id = card_info[0].user_id

        # 创建订单
        SOrderInfo.objects.create(
            site_id=site_id,
            eq_id=eq_id,
            eq_port=eq_port,
            term_address=terminal_address,
            card_num=card_num,
            charge_type='card',
            pay_way='card',
            charge_time=0,
            charge_electric=0,
            charge_money=0,
            fee_type=eq_fee_type,
            fee_no=eq_fee_no,
            user_id=user_id,
            order_id=order_no,
            state='1',
            error_times=0,
            create_time=datetime.datetime.now(),
            begin_time=datetime.datetime.now(),
            use_electric=0,
            use_money=0,
            use_time=0,
            order_source='用户刷卡'
        )

        # 创建计费
        handleorder.create_fee_detail(site_id, order_no, eq_fee_type, eq_fee_no)


        # 创建费用结构
        SOrderUseMoney.objects.create(
            order_id=order_no,
            create_time=datetime.datetime.now()
        )

        DurationOrAmount_ = 600
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)

        json_data = {
            'number': '0420',
            'terminal_address': terminal_address,
            'Special_data': {
                'SocketNumber': eq_port,
                'OrderNumber': order_no,
                'electrovalence': '0050',  # 这个电价没用，写死
                'type': '01',  # 00：金额，01：时间
                'DurationOrAmount': DurationOrAmount_h
            }
        }

        req_term(json_data)



def main():
    log.info('处理开启刷卡订单程序启动')
    while True:
        time.sleep(3)  # 20s检查一次，生产环境可以延长到3分钟检查一次
        orders = get_order_start_task()  # 1) 获取需要进行检查的订单
        if orders:
            for order in orders:
                log.info(order)
                time.sleep(0.1)
                handle_card_order_start(order)


if __name__ == '__main__':
    main()