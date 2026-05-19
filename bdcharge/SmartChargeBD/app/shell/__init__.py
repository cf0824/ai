#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：__init__.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/1/24 14:45 
@Description :
'''
import os
import sys
from app.models import *
import json
import datetime
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger


def is_save_cmd_db(AFN, Fn):
    map_dict = {
        '0420': '插座启停',
        '0401': '设置通信参数',
        '0402': '设置域名端口',
        '0417': '设置功率阈值',
        '0418': '设置结算配置',
        '0419': '设置充电桩启停',
        '0421': '二维码下发',
        '0A01': '查询通信参数',
        '0A02': '查询域名端口',
        '0A03': '查询信号强度',
        '0A17': '查询功率阈值',
        '0A18': '查询结算配置',
        '0A19': '查询充电桩状态',
        # '0A20': '查询插座状态',
        '0A21': '查询二维码',
        '0A41': '查询充电桩累计电量',
    }
    AFN_Fn = AFN + Fn
    if AFN_Fn in map_dict:
        return True, map_dict[AFN_Fn]
    else:
        return False, None

def save_cmd_db(active_station, req_cmd, AFN, Fn, cmd_type):
    term_address = req_cmd['address_region'].get('address_term_r')
    PR_SEQ = req_cmd['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')
    api_code = AFN + Fn
    SCmdInfo.objects.create(
        term_address=term_address,
        PR_SEQ=PR_SEQ,
        active_station=active_station,
        api_code=api_code,
        cmd_type=cmd_type,
        req_cmd=json.dumps(req_cmd),
        resp_status='0',
        update_status='0',
        req_time=datetime.datetime.now(),
        resend_times=0,
        resend_time=datetime.datetime.now()
    )


# 'number': '0A02',
# 'terminal_address': '10000808',
# 'Special_data': {}
def req_term(paras):  # 这个方法前端接口调用
    try:
        from app.command.tools.MessageApi import Message
        from app.command import cmdFunc
        from app.command.tools.api_func import ApiFunc
        message = Message(log)
        apifunc = ApiFunc(log)
        log.info(f'给充电桩发消息')
        req_data, byte_req_data = apifunc.get_active_send_data(paras)
        parse1 = message.Message_parsing(req_data)
        # terminal_address, parse2 = reparse.Message_Reparsing(parse1)
        parse1['app_region']['Specific_data_detail'] = paras.get('Special_data')
        AFN = parse1['app_region'].get('app_region_function_code')
        Fn = parse1['app_region']['Data_unit_identification'].get('Fn')
        is_save, cmd_type = is_save_cmd_db(AFN, Fn)
        if is_save:
            save_cmd_db('S', parse1, AFN, Fn, cmd_type)
        term_no = paras.get('terminal_address')
        key = {
            'head': 'cmdS2T'
        }
        value = {
            'term_no': term_no,
            'cmd': req_data
        }
        log.info(value)
        cmdFunc.add_command(key, value)
        log.info(f'---主动S2T命令已添加---')
    except Exception as e:
        log.error(f'发送命令失败：{e}', exc_info=True)