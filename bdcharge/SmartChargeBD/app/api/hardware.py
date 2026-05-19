#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：hardware.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/18 15:48 
@Description : 硬件通讯相关接口   ...废弃
'''
import asyncio
import json
import time

from app.utils.comm import api_handle
from app.utils import Error
from app.models import *
from app.utils.tools import haversine
from django.db import transaction
from django.db.models import F
import datetime
from django.core.paginator import Paginator
import random
import decimal
from SmartChargeBD.settings import BASE_DIR
from django.shortcuts import HttpResponse
from app.utils.eq_api import tieta_handle2
from app.utils.get_seq import Get_SeqNo
from app.utils.handle import charge_open, charge_stop
from django.db import connection
# from ..utils import MyLog
from app.tcp_socket import TCPHandler
from app.command.hardware_api import HardwareApi
from app.shell import req_term
from app.utils import MyLog

log = MyLog.MyLog(__file__, 'hardware.log', BASE_DIR).logger
hardwareapi = HardwareApi()

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        super(MyJSONEncoder, self).default(o)

def return_resp(resp):
    s = json.dumps(resp, cls=MyJSONEncoder)
    log.info(f'resp:{s}')
    return HttpResponse(s)

# 接收充电桩主动发送，解包后的数据
# def get_T2S(request):
#     try:
#         log.info(f'{request.method} ,{request}')
#         log.info(f'{request.body}')
#         data = request.body.decode()  # 接收到的数据是字节的，要转码成字符串
#         data_body = data[4+8:]  # 去掉头  'TERM%s%s' % ('00000000', dict_data)
#         data_body = json.loads(data_body)  # 再转码成json
#         log.info(f'充电桩终端->通讯机->服务端:{data_body}，type:{type(data_body)}')
#
#         terminal_address = data_body['address_region'].get('address_term_r')
#         AFN = data_body['app_region'].get('app_region_function_code')
#         Fn = data_body['app_region']['Data_unit_identification'].get('Fn')
#         log.info(f'终端编号：{terminal_address}')
#
#         return return_resp('aa')
#
#
#     except Exception as e:
#         log.error(f'{e}', exc_info=True)
#         return return_resp(Error.SYSTEM_ERROR)

def S_commu_para(terminal_address, para):
    try:
        heart_cycle = para.get('heart_cycle')
        up_cycle = para.get('up_cycle')
        delay_time = para.get('delay_time')
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    Special_data = {
        'heart_cycle': heart_cycle,
        'up_cycle': up_cycle,
        'delay_time': delay_time
    }
    hardwareapi.set_comm_paras(terminal_address, Special_data)

def S_domain_port(terminal_address, para):
    try:
        domian = para.get('domian')
        port = para.get('port')
        length = len(domian)
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    Special_data = {
        'length': length,
        'domian': domian,
        'port': port
    }
    hardwareapi.set_domain(terminal_address, Special_data)

def S_power_threshold(terminal_address, para):
    try:
        min_power = para.get('min_power')
        max_power = para.get('max_power')
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    Special_data = {
        'min_power': min_power,
        'max_power': max_power
    }
    hardwareapi.set_power_range(terminal_address, Special_data)

def S_settle_allocation(terminal_address, para):
    try:
        Hourly_price = para.get('Hourly_price')
        Rate_duration = para.get('Rate_duration')
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    Special_data = {
        'Hourly_price': Hourly_price,
        'Rate_duration': Rate_duration
    }
    hardwareapi.set_settle_config(terminal_address, Special_data)

def S_socket_status(terminal_address, para):
    try:
        SocketNumber = para.get('SocketNumber')
        OrderNumber = para.get('OrderNumber')
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    Special_data = {
        'SocketNumber': SocketNumber,
        'OrderNumber': OrderNumber,
        'electrovalence': '0050',  # 这个电价没用，写死
        'type': '01',  # 00：金额，01：时间
        'DurationOrAmount': '0200'
    }
    hardwareapi.set_socket_status(terminal_address, Special_data)

def S_QRcode(terminal_address, para):
    try:
        QR_data = para.get('QR_data')
    except Exception as e:
        log.error(f'参数缺失,{e}')
        return return_resp(Error.REQ_PARAMS_ERROR)
    QR_len = len(QR_data)
    Special_data = {
        'QR_len': QR_len,
        'QR_data': QR_data
    }
    hardwareapi.set_QRCode(terminal_address, Special_data)

def Q_commu_para(terminal_address):
    hardwareapi.get_comm_paras(terminal_address)

def Q_domain_port(terminal_address):
    hardwareapi.get_domain(terminal_address)

def Q_signal_strength(terminal_address):
    hardwareapi.get_signal_strength(terminal_address)

def Q_power_threshold(terminal_address):
    hardwareapi.get_power_range(terminal_address)

def Q_settle_allocation(terminal_address):
    hardwareapi.get_settle_config(terminal_address)

def Q_QRcode(terminal_address):
    hardwareapi.get_QRCode(terminal_address)

def Q_socket_status(terminal_address):
    hardwareapi.get_socket_status(terminal_address)

def Q_total_electricity(terminal_address):
    hardwareapi.get_total_electricity(terminal_address)

# 这里写一个匹配函数
# 管理台传进来操作类型和参数，在这里进行匹配
def get_func_A(AFN, Fn):
    """
    匹配接口
    :param dict_data: 解包后的数据
    :return: 对应的接口
    对于服务器为主动站的情况，终端发过来的数据，还用原来的方式，通过api_func来返回
    这里只用来解析终端主动上报的数据
    """
    Function_mapping = {
        '04': {
            '01': S_commu_para,
            '02': S_domain_port,
            '17': S_power_threshold,
            '18': S_settle_allocation,
            # '19': S_pile_status,   # 硬件接口缺失
            '20': S_socket_status,
            '21': S_QRcode
        },
        '0A': {
            '01': Q_commu_para,
            '02': Q_domain_port,
            '03': Q_signal_strength,
            '17': Q_power_threshold,
            '18': Q_settle_allocation,
            # '19': Q_pile_status,  # 没有这个接口
            '20': Q_socket_status,  # 在其他地方实现
            '21': Q_QRcode,
            '41': Q_total_electricity
        }
    }

    func = Function_mapping[AFN].get(Fn)
    if func:
        log.info(f"接口匹配成功！")
        return func
    elif func is None:
        log.error(f"接口匹配失败，找不到接口！")
        return None

def test(request):
    return HttpResponse('a')

# 负责接收管理台发给充电桩的信息，公众号做个中转
def get_A2T(request):
    try:
        log.info(f'{request.method} ,{request}')
        log.info(f'{request.body}')
        data = request.body.decode()  # 接收到的数据是字节的，要转码成字符串
        data_body = json.loads(data)  # 再转码成json
        log.info(f'管理台->公众号->通讯机->充电桩终端:{data_body}，type:{type(data_body)}')
        operator_type = data_body.get('operator_type')
        terminal_address = data_body.get('terminal_address')
        try:
            eq_info = SEqInfo.objects.get(terminal_address=terminal_address)
        except:
            return return_resp(Error.CONTENT_NOT_FOUND)
        paras = data_body.get('paras')
        log.info(f'操作类型：{operator_type}, 参数：{paras}')
        AFN = operator_type[0:2]
        Fn = operator_type[2:4]
        # 匹配函数
        func = get_func_A(AFN, Fn)
        if func is None:
            return return_resp(Error.FUNC_CODE_ERROR)
        if AFN == '04':
            func(terminal_address, paras)
        elif AFN == '0A':
            func(terminal_address)
        resp = {
            'statusCode': 200,
            'msg': '提交成功'
        }




        return return_resp(resp)


    except Exception as e:
        log.error(f'{e}', exc_info=True)
        return return_resp(Error.SYSTEM_ERROR)
