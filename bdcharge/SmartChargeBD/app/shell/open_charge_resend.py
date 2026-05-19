#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：open_charge_resend.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/7/22 10:29 
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

from app.command import cmdFunc
import json




def get_opencharge_resend_task():
    """
    获取xx分钟内没有响应的cmd
    :return:
    """
    dt = datetime.datetime.now() - datetime.timedelta(seconds=10)
    tasks = SCmdInfo.objects.filter(resp_status='0', api_code='0420', resend_time__lte=dt, resend_times__lt=3)  # 重发三次
    return tasks


def handle_opencharge_resend(task):
    log.info(f'重发命令：{task.id}')
    try:
        id = task.id
        terminal_address = task.term_address
        req_cmd = task.req_cmd
        resend_times = task.resend_times

        req_cmd = json.loads(req_cmd)
        part1 = req_cmd['head_str'].get('head_str_')
        part2 = req_cmd.get('user_data_region')
        part3 = req_cmd.get('crc_str')
        part4 = req_cmd.get('tail_str')

        req_data = part1 + part2 + part3 + part4

        log.info(f'组装后的命令：{req_data}')

        key = {
            'head': 'cmdS2T'
        }
        value = {
            'term_no': terminal_address,
            'cmd': req_data
        }
        cmdFunc.add_command(key, value)
        log.info('命令重新发送成功')
        SCmdInfo.objects.filter(id=id).update(
            resend_times=resend_times + 1,
            resend_time=datetime.datetime.now()
        )
    except Exception as e:
        log.error(f'命令重发失败：{e}', exc_info=True)


def main():
    log.info('充电命令重发程序启动')
    while True:
        time.sleep(3)  # 20s检查一次，生产环境可以延长到3分钟检查一次
        tasks = get_opencharge_resend_task()  # 1) 获取需要进行检查的订单
        if tasks:
            for task in tasks:
                log.info(task)
                time.sleep(0.1)
                handle_opencharge_resend(task)


if __name__ == '__main__':
    main()
