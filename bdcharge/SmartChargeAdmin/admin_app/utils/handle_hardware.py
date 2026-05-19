#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：handle_hardware.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/3/31 10:36 
@Description :
'''
import json
import os
from admin_cfg.settings import HARDWARE_API
import requests
from admin_app.utils import MyLog

url = HARDWARE_API

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)

log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger


def get_comm_para(terminal_address):
    log.info(f'查询通讯参数：{terminal_address}')
    data = {
        'operator_type': '0A01',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_domain_port(terminal_address):
    log.info(f'查询域名端口：{terminal_address}')
    data = {
        'operator_type': '0A02',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_signal_strength(terminal_address):
    log.info(f'查询信号强度：{terminal_address}')
    data = {
        'operator_type': '0A03',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_power_threshold(terminal_address):
    log.info(f'查询功率阈值：{terminal_address}')
    data = {
        'operator_type': '0A17',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_settle_allocation(terminal_address):
    log.info(f'查询结算配置：{terminal_address}')
    data = {
        'operator_type': '0A18',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_socket_status(terminal_address):
    log.info(f'查询插座状态：{terminal_address}')
    data = {
        'operator_type': '0A20',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_QRcode(terminal_address):
    log.info(f'查询二维码：{terminal_address}')
    data = {
        'operator_type': '0A21',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def get_total_electricity(terminal_address):
    log.info(f'查询二维码：{terminal_address}')
    data = {
        'operator_type': '0A41',
        'terminal_address': terminal_address
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_comm_paras(terminal_address, paras):
    log.info(f'设置通信参数：{terminal_address}')
    data = {
        'operator_type': '0401',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_domain(terminal_address, paras):
    log.info(f'设置域名端口：{terminal_address}')
    data = {
        'operator_type': '0402',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_power_range(terminal_address, paras):
    log.info(f'设置功率阈值：{terminal_address}')
    data = {
        'operator_type': '0417',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_settle_config(terminal_address, paras):
    log.info(f'设置结算配置：{terminal_address}')
    data = {
        'operator_type': '0418',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_pile_status(terminal_address, paras):
    log.info(f'设置充电桩状态：{terminal_address}')
    data = {
        'operator_type': '0419',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_socket_status(terminal_address, paras):
    log.info(f'设置插座状态：{terminal_address}')
    data = {
        'operator_type': '0420',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()

def set_QRCode(terminal_address, paras):
    log.info(f'设置二维码：{terminal_address}')
    data = {
        'operator_type': '0421',
        'terminal_address': terminal_address,
        'paras': paras
    }
    data_ = json.dumps(data)
    res = requests.post(url, data=data_)
    log.info(f'{res}')
    log.info(f'{res.json()}')
    return res.json()


"""
paras = [
    'operator_type': {
        'type': '',
        'args': {
            'arg1': '',
            'arg2': ''
        }
    },    
]
"""

def handle_hardware_cmd_get(terminal_address, paras):
    log.info(f'处理：`{terminal_address}`的命令, paras: {paras}')
    try:
        for item in paras:
            func_type = item['type']
            function = globals().get(func_type)
            if function and callable(function):
                function(terminal_address)
            else:
                log.info(f"错误：未找到函数 {func_type} 或不可调用")


    except Exception as e:
        log.error(f'命令处理失败：{e}', exc_info=True)


def handle_hardware_cmd_set(terminal_address, paras):
    log.info(f'处理：`{terminal_address}`的命令, paras: {paras}')
    try:
        for item in paras:
            func_type = item['type']
            args = item['args']
            function = globals().get(func_type)
            if function and callable(function):
                function(terminal_address, args)
            else:
                log.info(f"错误：未找到函数 {func_type} 或不可调用")


    except Exception as e:
        log.error(f'命令处理失败：{e}', exc_info=True)


def call_function(func_name):
    """接收函数名的字符串，动态调用对应函数"""
    # 获取当前模块的全局函数字典
    function = globals().get(func_name)

    if function and callable(function):
        function()  # 执行函数
    else:
        print(f"错误：未找到函数 {func_name} 或不可调用")


# 可选：带参数的版本
def func_with_args(msg):
    print(f"带参数的函数被调用，参数是：{msg}")


def call_function_with_args(func_name, *args):
    """支持传参的版本"""
    function = globals().get(func_name)
    if function and callable(function):
        function(*args)
    else:
        print(f"错误：未找到函数 {func_name} 或不可调用")