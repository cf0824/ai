#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_deduction_money.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/6/3 15:46 
@Description :
'''
import time
import datetime

import os
import sys

from django.db import transaction
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DateTimeField
from django.db.models.functions import Now

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


def Obtain_deduction_task():
    log.info('获取扣款配置')
    records = SDeductionCfg.objects.filter(state='1')
    log.info(f'扣款配置: {records}')
    now = timezone.now()
    result = []

    for record in records:
        if record.last_deduct_time is None:
            result.append(record)
            continue

        next_deduct_time = record.last_deduct_time + datetime.timedelta(days=record.time_interval)

        if now >= next_deduct_time:
            result.append(record)
    log.info(f'当前需要扣款的数据：{result}')

    return result


@transaction.atomic()
def deduct_money(task):
    user_id = task.user_id
    money = task.money
    type_id = task.type_id
    remark = task.remark
    SDeductionDetail.objects.create(
        user_id=user_id,
        money=money,
        type_id=type_id,
        remark=remark,
        create_time=datetime.datetime.now(),
        state='0'
    )
    SDeductionCfg.objects.update(
        last_deduct_time=datetime.datetime.now()
    )


def main():
    log.info(f'扣款程序启动')
    while True:
        time.sleep(120)  # 5分钟
        deduction_tasks = Obtain_deduction_task()
        for task in deduction_tasks:
            log.info(f'需要扣款的配置[用户：{task.user_id}，类型：{task.type_id}，间隔：{task.time_interval}，上次：{task.last_deduct_time}]')
            deduct_money(task)
            log.info(f'扣款记录创建完成')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(f'扣费异常：{e}', exc_info=True)
