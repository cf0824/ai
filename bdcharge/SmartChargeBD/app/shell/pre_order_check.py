#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：pre_order_check.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/2/18 15:53 
@Description :  该脚本是检查用户已提交，但硬件还未上送、未开启的订单
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
    dt1 = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
    dt2 = datetime.datetime.now() - datetime.timedelta(seconds=30)  # 订单创建时间要在30秒外，创建30秒后，订单状态未改变，即超时
    orders = SOrderInfo.objects.filter(state__in=[0], create_time__gte=dt1, create_time__lt=dt2)  # 只检查未开启的订单。
    return orders

def refund_money_online(charge_order, refund_amount):
    log.info(f'处理在线支付订单退款: {charge_order}，{refund_amount}')
    from app.utils.get_seq import Get_SeqNo
    from app.utils.wx_pay import order_refund
    refund_no = Get_SeqNo("REFUND_CHARGE_ORDER")
    # 查找充值订单号
    sub_order_info = SOrderNumMap.objects.filter(charge_order=charge_order).first()
    log.info(f'sub_order_info: {sub_order_info}')
    if sub_order_info:
        # transaction_id, order_id, out_trade_no, amount
        sub_order = sub_order_info.sub_order
        transaction_id = sub_order_info.transaction_id
        refund_amount_ = int(refund_amount * 100)
        user_id = sub_order_info.user_id

        #创建退款订单
        # 创建充电订单微信交易记录
        SWxTranOrderDetail.objects.create(
            change_type='out',
            change_money=float(refund_amount),
            user_id=user_id,
            order_id=refund_no,
            verify_state='1',
            verify_time=datetime.datetime.now(),
            create_time=datetime.datetime.now(),
            state='1'
        )
        log.info(f'开始退款')
        res = order_refund(transaction_id, refund_no, sub_order, refund_amount_)
        log.info(f'退款结果：{res}')


def refund_money_account():
    pass


def handle_order(order):
    # 获取order使用的终端地址、插座编号
    term_address = order.term_address
    SocketNumber = order.eq_port
    OrderNumber = order.order_id
    log.info(f'超时订单：{OrderNumber}, 充电桩地址：{term_address}, 插座编号：{SocketNumber}')
    # 给终端发送关闭命令，防止过一会充电桩又开启了
    special_data = {
        'SocketNumber': SocketNumber,
        'OrderNumber': OrderNumber,
        'electrovalence': '0050',  # 这个电价没用，写死
        'type': '01',  # 00：金额，01：时间
        'DurationOrAmount': '0000'  # 为0，表示停止充电
    }
    hardwareapi.set_socket_status(term_address, special_data)

    # 更新订单状态
    # dt1 = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
    # SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt1).update(
    #     state='-1',
    #     remark='订单超时'
    # )
    order.state = '-1'
    order.remark = '订单超时'
    order.save()
    # 查询订单类型
    # orders = SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt1)
    charge_type = order.charge_type
    pay_way = order.pay_way
    # 执行退款程序
    if charge_type == 'money':  # 只有按金额充电才有退款
        order.return_money = order.charge_money  # 超时，把所有前都退了
        order.save()
        if pay_way == 'online':
            refund_money_online(OrderNumber, order.charge_money)
        elif pay_way == 'account':
            refund_money_account()

    # 释放端口
    SEqPort.objects.filter(terminal_address=term_address, eq_port=SocketNumber).update(
        use_state='0'
    )
    # 处理返回的结果，在handle_args的统一参数入口中，这里只用给充电桩发送查询命令

def main():
    while True:
        time.sleep(5)  # 5秒检查一次
        orders = get_orders()  # 1) 获取需要进行检查的订单
        for order in orders:
            # log.info(f'超时的订单:{order.order_id}')
            time.sleep(0.1)
            handle_order(order)

if __name__ == '__main__':
    main()
