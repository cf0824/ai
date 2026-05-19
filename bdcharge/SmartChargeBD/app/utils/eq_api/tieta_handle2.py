import json
import re
import sys
import os
import time

import django
import datetime

# # 添加当前路径到环境变量中
# pwd = os.path.dirname(os.path.realpath(__file__))
# pwd = pwd.replace('\charge\shell', '').replace('/charge/shell', '')
# # pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCharge.settings')  # VueSt是自己的项目名称
# django.setup()  # 更新配置

# from django.db import transaction
from app.models import *
from .tieta_api import TietaApi
from app.utils import handle


class TietaHandle:
    # 通讯超时时间（秒）
    _requestTimeOut = 10

    def __init__(self, SCmdDetail):
        self._SCmdDetail = SCmdDetail
        self.api = TietaApi()

    # 添加到待发送报文
    def _add_cmd(self, cmd, devId, txnNo):
        handle.add_cmd(devId, cmd, txnNo)
        # eq_id = handle.devid2eqid(devId)
        # self._SCmdDetail.objects.create(
        #     cmd=cmd,
        #     seq_no=txnNo,
        #     eq_id=eq_id,
        #     eq_code=devId,
        #     send_type='1',
        #     create_time=datetime.datetime.now(),
        #     state='0'
        # )

    # 获取回复报文
    def _get_reply_cmd(self, devId, txnNo, times=0):
        cmd = self._SCmdDetail.objects.filter(eq_code=devId, seq_no=txnNo, send_type='2').first()
        if not cmd:
            if times < self._requestTimeOut:
                time.sleep(1)
                return self._get_reply_cmd(devId, txnNo, times + 1)
            return None
        return cmd.cmd

    # 通用操作处理
    def _ctrl_handle(self, devId, k, v, addParamList=None):
        cmd = self.api.ctrl_post_one(devId, k, v, addParamList)
        txnNo = self.api.get_txn_no_from_cmd(cmd)
        self._add_cmd(cmd, devId, txnNo)
        return txnNo
        # reply_cmd = self._get_reply_cmd(devId, txnNo)
        # if not reply_cmd:
        #     return False
        # result = self.api.unpack_ctrl_post_one(reply_cmd)
        # return result

    # 充电桩设备重启
    def eq_restart(self, devId):
        k = '05202001'
        v = 0
        return self._ctrl_handle(devId, k, v)

    # 充电桩设备开关
    def eq_open(self, devId, open=True):
        k = '05202001'
        if open:
            v = 2
        else:
            v = 1
        return self._ctrl_handle(devId, k, v)

    # 充电桩充电开关
    def eq_charge_open(self, devId, open=True, account_money=None, set_elect=None, set_time=None, set_money=None):
        k = '05201001'
        if open:
            v = 0
        else:
            v = 1
        addParamList = []
        if account_money:
            addParamList.append({
                'id': '05201002',
                'value': account_money
            })
        if set_elect:
            addParamList.append({
                'id': '05201003',
                'value': set_elect
            })
        if set_time:
            addParamList.append({
                'id': '05201004',
                'value': set_time
            })
        if set_money:
            addParamList.append({
                'id': '05201005',
                'value': set_money
            })
        if len(addParamList) > 0:
            return self._ctrl_handle(devId, k, v, addParamList)
        return self._ctrl_handle(devId, k, v)

    # 设置计费模式（电动自行车）
    def set_price_mode_bicycle(self):
        pass

    # todo 设置计费模式（电动汽车）
    def set_price_mode_car(self, devId, priceMode, chargeType=1):
        k = '05401001'
        v = {
            'chargeType': chargeType,
            'priceMode': priceMode
        }
        return self._ctrl_handle(devId, k, v)





if __name__ == "__main__":
    th = TietaHandle(SCmdDetail)
    # devId = 'AAAA00000000'
    # res = th.eq_restart(devId)
    # print('res=', res)

    # res = th.eq_restart('YJDC12345600')
    # print('res=', res)

    # res = th.eq_open('YJDC12345600')
    # print('res=', res)

    # res = th.eq_open('YJDC12345600',False)
    # print('res=', res)

    # res = th.eq_charge_open('YJDC12345600')
    # print('res=', res)

    res = th.eq_charge_open('YJDC12345600', False)
    print('res=', res)
