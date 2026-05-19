#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_cmd2.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/21 17:17 
@Description :
'''
import time
import datetime

import os
import sys
pwd = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(pwd)
parent_dir_ = os.path.dirname(parent_dir)
#print(pwd)
#print(parent_dir)
#print(parent_dir_)
#print(sys.path)
sys.path.append(pwd)
sys.path.append(parent_dir)
sys.path.append(parent_dir_)
#print(sys.path)
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()

from app.models import *
from app.command.redis_package.redisFunc import RedisDb
from app.command.tools.MessageApi import Message
from app.command.tools.MessageReparseFunc import ReParseFunc
from app.command.tools.api_func import ApiFunc
from app.command.bd_api import BDAPI
from app.command import cmdFunc
import json
redis_db = RedisDb()
message = Message(log)
reparse = ReParseFunc(log)
bdapi = BDAPI(log)
apifunc = ApiFunc(log)


# 查找 充电桩-->服务器 的消息（不一定是命令，也可能是响应）
def get_cmd_T2S():

    keys = redis_db.get_keys('cmdT2S*')
    return keys   # 每个key，都是一个 充电桩-->服务器  的命令


def get_cmd_detail(cmd):
    cmd_detail = redis_db.get_value(cmd)
    cmd_detail = json.loads(cmd_detail)
    redis_db.del_value(cmd)
    return cmd_detail


# 响应充电桩终端,向redis中添加一条记录，充电桩主动发送，服务器响应
def resp_term(recv_data):  # 接收的是解包后的数据
    special_data = bdapi.get_special_data(recv_data)
    resp_data, byte_resp_data = message.message_pack1(recv_data, special_data)  # 根据充电桩发送的数据，生成响应数据
    key = {
        'head': 'cmdS2T'
    }
    value = {
        'term_no': recv_data['address_region'].get('address_term_r'),
        'cmd': resp_data
    }
    cmdFunc.add_command(key, value)
    log.info(f'---响应S2T命令已添加---')
    bdapi.handle_special_data(recv_data)  # 充电桩主动发送的数据进行处理，登录、数据上报。。。


def handle_term_data(recv_data):  # 二次解析后的数据
    bdapi.handle_special_data(recv_data)  # 处理数据


def handle_cmd_main(cmd_detail):
    try:
        # term_no = cmd_detail['term_no']
        cmd = cmd_detail['cmd']
        # 解包
        parse1 = message.Message_parsing(cmd)
        terminal_address, parse2 = reparse.Message_Reparsing(parse1)
        parse1['app_region']['Specific_data_detail'] = parse2
        AFN = parse1['app_region'].get('app_region_function_code')
        Fn = parse1['app_region']['Data_unit_identification'].get('Fn')
        PRM = parse1['control_region'].get('PRM')
        terminal_address = parse1['address_region'].get('address_term_r')
        # 判断设备是否注册
        device_exists = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
        if device_exists:
            if ((AFN == '02' or AFN == '0E') and PRM == '0') or ((AFN == '04' or AFN == '0A') and PRM == '1'):
                log.error(f'报文错误')
            if AFN == '02' or AFN == '0E':  # 充电桩主动发送，需要组包响应
                try:
                    resp_term(parse1)
                except Exception as e:
                    log.error(f'响应充电桩失败！{e}', exc_info=True)
            if AFN == '04' or AFN == '0A':  #  服务器主动发送，充电桩响应，需要把响应的数据更新到数据库
                try:
                    handle_term_data(parse1)  #
                except Exception as e:
                    log.error(f'处理充电桩数据失败{e}', exc_info=True)
        else:
            log.error(f'设备{terminal_address}未注册，交易失败，交易类型：{AFN}{Fn}', exc_info=True)

    except Exception as e:
        log.error(e, exc_info=True)


def main():
    log.info(f'handle_cmd!')
    while True:
        time.sleep(0.1)
        cmds = get_cmd_T2S()
        if len(cmds) != 0:
            log.info(f'【命令列表：{cmds}】,【counts:{len(cmds)}】')
        for cmd in cmds:  # 这里的cmd是键
            time.sleep(0.05)
            cmd_detail = get_cmd_detail(cmd)
            log.info(f'指令详情：{cmd_detail}, 类型：{type(cmd_detail)}')
            log.info(f'@@@@@@@@@@@@@@@@@@@@@@@@@@@处理充电桩报文@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            handle_cmd_main(cmd_detail)
            log.info(f'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@处理结束@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')


if __name__ == '__main__':
    main()
