#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
import datetime
import sys

from tools.MessageApi import Message  # 解析、响应组包
from tools.MessageReparseFunc import ReParseFunc  # 二次解析，specific_data


# 日志初始化
def loger_init(logname):
    # 日志中添加自定义字段，平台流水号
    def ptlsh(record):
        try:
            if record.ptlsh:
                pass
            else:
                record.ptlsh = 'noserial'
        except:
            record.ptlsh = 'noserial'
        return True

    # -----------------------------------------------#
    # 日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    log_file_temp = logname + '_' + now_time + '.log'
    fh = logging.handlers.RotatingFileHandler(log_file_temp, maxBytes=1024 * 1024 * 100, backupCount=30)
    fh.addFilter(ptlsh)
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter('[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] '
                                     '[%(process)-7d] [%(ptlsh)s] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    # print('public',logger)
    if not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
        logger.addHandler(fh)  # 将handler加入logger
    return logger


log = loger_init('test')
Function_mapping = {
    '02': {   # 链路接口检测
        '01': '登录',
        '02': '退出登录',
        '03': '心跳',
        '04': '登录验证',
        'FF': '链路接口检测'
    },
    '04': {  # 设置参数
        '01': '通信参数',
        '02': '域名端口',
        '17': '插座功率阀值',
        '18': '结算配置',
        '19': '充电桩启停',
        '20': '插座远程启停',
        '21': '二维码下发',
        'FF': '设置参数'
    },
    '0A': {  # 查询参数
        '01': '通信参数',
        '02': '域名端口',
        '03': '信号强度',
        '17': '插座功率阀值',
        '18': '结算配置',
        '19': '充电桩启停',
        '20': '插座远程启停',
        '21': '二维码',
        '41': '充电桩累计电量',
        'FF': '查询参数'
    },
    '0E': {  # 数据上报
        '01': 'SIM卡信息',
        '02': '地理位置',
        '03': '插座实时状态',
        '04': '刷卡用电记录',
        '05': '故障上报',
        'FF': '数据上报'
    }
}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        recv_data = sys.argv[1]
    else:
        recv_data = '681600686046080010010E60000300010702000003EB02008800CEAF16'
    print(f'recv_data=[{recv_data}]')

    from tools.MessageApi import Message
    # log1, fh = publog.loger_init(pubpara.log_name_Message_Api)
    message = Message(log)
    hexcmd = bytes.fromhex(recv_data)
    dict_data = message.Message_parsing(hexcmd)
    print(dict_data)
    if dict_data:
        terminal_address = dict_data['address_region'].get('address_term_r')

        AFN = dict_data['app_region'].get('app_region_function_code')
        Fn = dict_data['app_region']['Data_unit_identification'].get('Fn')
        pseq_rseq = dict_data['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')

        try:
            name1 = Function_mapping[AFN]['FF']
            name2 = Function_mapping[AFN][Fn]
            print(f'终端:{terminal_address}->服务器,{recv_data}==>{name1}-{name2},帧序号:{pseq_rseq}')
        except KeyError:
            print(f'终端:{terminal_address}->服务器,{recv_data}==>未匹配到接口名称, AFN:{AFN},Fn:{Fn},帧序号:{pseq_rseq}')
    else:
        print(f'解包错误')
