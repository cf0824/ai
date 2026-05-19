#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_eq_online.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/2/11 9:19 
@Description :
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

def get_all_eq():
    dt = datetime.datetime.now() - datetime.timedelta(minutes=10)
    eqs = SEqInfo.objects.filter(conn_state=1, last_conn_time__lte=dt)
    return eqs

def get_eq_order(eq_id):
    dt = datetime.datetime.now() - datetime.timedelta(minutes=10)
    orders = SOrderInfo.objects.filter(eq_id=eq_id, state='1', create_time__gte=dt)
    return orders

def main():
    from app.utils.handle_order import HandleOrder
    handleorder = HandleOrder(log)
    while True:
        time.sleep(300)  # 5分钟
        eqs = get_all_eq()
        for eq in eqs:
            log.info(f'超时的设备：{eq.terminal_address}')
            terminal_address = eq.terminal_address
            # 更新设备表为设备离线
            SEqInfo.objects.filter(terminal_address=terminal_address).update(
                conn_state='0'  # 设备离线
            )
            # 更新插座表
            SEqPort.objects.filter(terminal_address=terminal_address).update(
                conn_state='0'  # 插座离线
            )
            # 查找有没有该设备有没有相关订单
            eq_id = eq.eq_id
            orders = get_eq_order(eq_id)
            for order in orders:
                log.info(f'该设备超时订单, {order.order_id}, 用户：{order.user_id}')
                handleorder.handle_order_stop(order, '设备离线，订单停止')




if __name__ == '__main__':
    main()