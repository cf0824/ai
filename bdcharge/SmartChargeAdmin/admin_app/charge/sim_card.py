#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：sim_card.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/13 14:58 
@Description :
'''
import base64
import os
import sys
import tempfile
import zipfile

from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
import requests
from admin_app.sys import public
import datetime
from admin_app.tools import handle

from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils.handle_sim import query_card_info


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

def get_sim_card_info(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    select_data = form_var.get('select_data', {})

    log.info(f'传入的数据form_var: {form_var}')

    log.info(f'form_data: {form_data}')
    log.info(f'select_data:{select_data}')
    if len(select_data) == 0:
        return err_msg(msg=f'请选择sim卡')
    try:
        db = MySQLDB()
        i = 0
        for item in select_data:
            i = i + 1
            sim_card = item.get('sim_card')
            if not sim_card:
                return err_msg(msg=f'第{i}条没有卡号')
            card_info = query_card_info(sim_card)
            log.info(card_info)
            status = card_info.get('status')
            message = card_info.get('message')
            if status != 0:
                return err_msg(msg=f'第{i}张卡[{sim_card}]查询失败, 错误原因：[{status}-{message}]')
            data = card_info.get('data')
            msisdn = data.get('msisdn')
            cardType = data.get('cardType')
            cardStatus = data.get('cardStatus')
            operator = data.get('operator')
            packageName = data.get('packageName')
            cardFlow = data.get('cardFlow')
            lastActivateTime = data.get('lastActivateTime')
            activateTime = data.get('activateTime')
            packageTime = data.get('packageTime')
            realNameStatus = data.get('realNameStatus')
            remark = data.get('remark')
            channelId = data.get('channelId')
            packageId = data.get('packageId')
            imsi = data.get('imsi')
            networkType = data.get('networkType')
            imei = data.get('imei')
            packageTotalFlow = data.get('packageTotalFlow')

            data = {
                'msisdn': msisdn,
                'cardType': cardType,
                'cardStatus': cardStatus,
                'operator': operator,
                'packageName': packageName,
                'cardFlow': cardFlow,
                'lastActivateTime': lastActivateTime,
                'activateTime': activateTime,
                'packageTime': packageTime,
                'realNameStatus': realNameStatus,
                'remark': remark,
                'channelId': channelId,
                'packageId': packageId,
                'imsi': imsi,
                'networkType': networkType,
                'imei': imei,
                'packageTotalFlow': packageTotalFlow,
                'update_time': datetime.datetime.now()
            }
            db.update('s_eq_sim_card', data, {"sim_card": sim_card})

        return resp
    except Exception as e:
        log.info(f'获取sim卡信息失败', exc_info=True)
        raise

