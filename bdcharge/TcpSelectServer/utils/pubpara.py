#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：LightedShelf 
@File    ：pubpara.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/8/25 18:41 
'''

listen_port = 6999  # 监听端口
listen_maxnum = 100  # 最大监听数， # 并发数
recvbuff_size = 10240   # socket接收最大字节数

log_name = 'Term_Main'   # 日志文件名
log_name_Message_Api = 'Message_Api'   # 日志文件名
log_name_Api_Func = 'Api_Func'   # 日志文件名
log_name_Redis = 'Redis_Func'
# 注册的连接字典：
regist_connect = {
    'sock_client': '',  # socket句柄
    'term_no': '',  # 终端编号
    'last_time': '',  # 最后通讯时间
}
regist_connect_sock = {}   #通过socket句柄找字典
regist_connect_term = {}   #通过终端找字典

client_quittime = 60  # 终端最大未通讯时间，超时则子进程退出。一般是大于两个心跳包的时间， 单位秒
last_clear_time = None  # socket链接上次清理时间
div_clear_time = 120  # 每XX秒清理一次

http_post_timeout = 30  # httppos 超时时间
# serurl = 'https://manage-admin.pinmait.com/termapi/leanpower/handle'
serurl = 'https://smartcharge.pinmait.com/api/hardware/T2S'

Function_Name = {
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
