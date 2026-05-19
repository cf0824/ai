#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：hand_card_order_stop.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/7/26 9:51
@Description :
'''
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
from app.shell import req_term
from app.command.tools.ApiTool import ApiTool

handleorder = HandleOrder(log)
apitool = ApiTool(log)


def get_card_order_stop_task():
    """
    获取订单停止任务
    :return:
    """
    tasks = SOrderCardStop.objects.filter(state='0')
    return tasks

def handle_card_order_stop(order):
    id = order.id
    terminal_address = order.terminal_address
    eq_port = order.eq_port
    card_num = order.card_num
    order_id = order.order_id

    SOrderCardStop.objects.filter(id=id).update(
        state='1',
        handle_time=datetime.datetime.now()
    )

    json_data = {
        'number': '0420',
        'terminal_address': terminal_address,
        'Special_data': {
            'SocketNumber': eq_port,
            'OrderNumber': order_id,
            'electrovalence': '0050',
            'type': '01',  # 00：金额，01：时间
            'DurationOrAmount': '0000'
        }
    }

    req_term(json_data)



def main():
    log.info('处理开启刷卡订单停止程序启动')
    while True:
        time.sleep(3)  # 20s检查一次，生产环境可以延长到3分钟检查一次
        orders = get_card_order_stop_task()  # 1) 获取需要进行检查的订单
        if orders:
            for order in orders:
                log.info(order)
                time.sleep(0.1)
                handle_card_order_stop(order)


if __name__ == '__main__':
    main()