#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：order_check.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/30 10:41 
@Description :  每xx秒查一下插座状态，并更新到订单表中
'''
import os
import sys
import time
import datetime

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

# os.environ['DJANGO_SETTINGS_MODULE'] = 'SmartChargeBD.settings'
from app.models import *
from app.command.hardware_api import HardwareApi

hardwareapi = HardwareApi()



def get_orders():
    dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
    orders = SOrderInfo.objects.filter(state__in=[1], create_time__gte=dt)  # 只检查充电中的订单。后续可以加上未开始的订单，处理逻辑要改变
    return orders

def get_ports():
    ports = SEqPort.objects.filter(use_state__in=[1])  # 正在使用中的插座
    return ports

def handle_order(order):
    # 获取order使用的终端地址、插座编号
    term_address = order.term_address
    log.info(f'检查订单：{order.order_id}, 充电桩地址：{term_address}, 插座编号：{order.eq_port}')
    # 给终端发送查询命令，查询插座状态
    hardwareapi.get_socket_status(term_address)
    # 处理返回的结果，在handle_args的统一参数入口中，这里只用给充电桩发送查询命令

def handle_port(port):
    eq_id = port.eq_id
    eq_port = port.eq_port
    term_address = port.terminal_address
    log.info(f'检查插座：{eq_id}-{eq_port}, 充电桩地址：{term_address}')
    order_info = SOrderInfo.objects.filter(eq_id=eq_id, eq_port=eq_port, state__in=[1])
    if order_info:
        log.info(f'订单：{order_info[0].order_id} 正在使用该插座')
    else:
        log.info(f'该插座没有订单占用，解除使用状态')
        SEqPort.objects.filter(eq_id=eq_id, eq_port=eq_port).update(
            use_state='0',
            update_time=datetime.datetime.now()
        )




def main():
    while True:
        time.sleep(180)  # 20s检查一次，生产环境可以延长到3分钟检查一次
        orders = get_orders()  # 1) 获取需要进行检查的订单
        ports = get_ports()

        for order in orders:
            log.info(order)
            time.sleep(0.1)
            handle_order(order)

        for port in ports:
            # log.info(port)
            time.sleep(0.1)
            handle_port(port)

if __name__ == '__main__':
    main()
