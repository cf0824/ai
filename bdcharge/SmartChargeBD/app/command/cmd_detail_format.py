#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：cmd_detail_format.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/24 16:43 
@Description :
'''

# 1.通信参数
cmd_detail_format1 = {
    'heart_cycle': '',  # 心跳周期
    'uplink_interval': '',  # 上送间隔
    'delay_time': ''
}
# 2.域名端口
cmd_detail_format2 = {
    'domain_len': '',  # 域名长度
    'domain_data': '',  # 域名信息
    'port': ''  # 端口号
}
# 3.功率阈值
cmd_detail_format3 = {
    'min_power': '',  # 最小功率
    'max_power': '',  # 最大功率
}
# 4.结算配置
cmd_detail_format4 = {
    'Hourly_price': '',  # 小时电价
    'Rate_duration': '',  # 费率时长
}
# 5.充电桩启停
cmd_detail_format5 = {
    'status': ''  # 启停状态
}
# 6.二维码下发
cmd_detail_format6 = {
    'QR_len': '',  # 二维码长度
    'QR_data': ''  # 二维码内容
}
# 7.插座远程启停
cmd_detail_format7 = {
    'SocketNumber': '',  # 插座序号
    'OrderNumber': '',  # 订单号
    'electrovalence': '',  # 电价
    'type': '',  # 00：金额，01：时间
    'DurationOrAmount': ''  # 充电时长或金额
}

class CmdDetailFormat:
    def __init__(self):
        pass

    # 获取通信参数模板
    def getCommuPara(self):
        return cmd_detail_format1

    # 获取域名端口模板
    def getDomainPort(self):
        return cmd_detail_format2

    # 获取功率阈值模板
    def getPowerThreshold(self):
        return cmd_detail_format3

    # 获取结算配置模板
    def getSettleAllocation(self):
        return cmd_detail_format4

    # 获取充电桩启停模板
    def getPileStartStop(self):
        return cmd_detail_format5

    # 获取二维码下发模板
    def getQRcodeDown(self):
        return cmd_detail_format6

    # 获取插座远程启停模板
    def getSocketStartStop(self):
        return cmd_detail_format7