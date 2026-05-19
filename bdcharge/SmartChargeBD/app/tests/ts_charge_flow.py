# 模拟充电流程

import re
import sys
import os
import time

import django
import datetime

# 添加当前路径到环境变量中
pwd = os.path.dirname(os.path.realpath(__file__))
pwd = pwd.replace('\charge\shell', '').replace('/charge/shell', '')
# pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings_dev')  # VueSt是自己的项目名称
django.setup()  # 更新配置

import json
import datetime
from app.models import *
from app.utils import handle
from app.utils.eq_api import tieta_handle2




# 模拟设备充电回复命令
def charge_reply_cmd(seq_no):
    cmd = SCmdDetail.objects.filter(seq_no=seq_no).first()
    devId = cmd.eq_code
    txnNo = seq_no

    cmd.state = '1'
    cmd.handle_time = datetime.datetime.now()
    cmd.save()
    print('模拟发送充电命令完成 延时10秒')
    time.sleep(10)

    # 模拟返回命令
    # 开启成功
    tmp = {"msgType": 501, "devId": devId, "txnNo": txnNo, "paramList": [{"id": "05201001", "devId": devId, "result": 1}]}
    # 开启失败
    # tmp = {"msgType": 501, "devId": devId, "txnNo": txnNo,
    #        "paramList": [{"id": "05201001", "devId": devId, "result": 0}]}

    SCmdDetail.objects.create(
        cmd=json.dumps(tmp),
        seq_no=seq_no,
        eq_code=devId,
        send_type='2',
        create_time=datetime.datetime.now(),
        state='0'
    )
    print('模拟充电回复完成')


# 模拟开始充电
def start_charge():
    print('开始模拟充电')
    order_id = str(int(time.time() * 1000))
    eq_id = 1
    user_id = 1
    charge_type = 'auto'
    SOrderInfo.objects.create(
        order_id=order_id,
        eq_id=eq_id,
        user_id=user_id,
        charge_type=charge_type,
        create_time=datetime.datetime.now(),
        state='0'
    )
    print('已创建订单 延时10秒')
    time.sleep(10)

    print('开始异步开启充电')
    opera = handle.charge_open(eq_id, order_id)
    print('已异步开启充电 延时10秒')
    time.sleep(10)

    opera2 = SOperaDetail.objects.filter(id=opera.id).first()
    seq_no = opera2.seq_no
    print('seq_no=', seq_no)
    # 模拟硬件回复
    charge_reply_cmd(seq_no)


# 模拟充电停止
def charge_stop():
    tmp = {"msgType": 320, "devId": "12348900", "txnNo": "123111", "attrList": [{"id": "05101001", "value": "1;163730811100;163730837400;233.30;4.36;0.01;0.09;15"}]}
    seq_no = '123111'
    devId = '12348900'
    SCmdDetail.objects.create(
        cmd=json.dumps(tmp),
        seq_no=seq_no,
        eq_code=devId,
        send_type='2',
        create_time=datetime.datetime.now(),
        state='0'
    )
    print('模拟充电回复完成')


# 设置计费模型
def set_price_mode():
    th = tieta_handle2.TietaHandle(SCmdDetail)
    priceMode = [{
        "price": 0.7151,
        "time": "07:00-08:00"
    }, {
        "price": 1.1446,
        "time": "08:00-11:00"
    }, {
        "price": 0.7151,
        "time": "11:00-15:00"
    }, {
        "price": 1.1446,
        "time": "15:00-19:00"
    }, {
        "price": 1.21567,
        "time": "19:00-22:00"
    }, {
        "price": 0.7151,
        "time": "22:00-23:00"
    }, {
        "price": 0.28604,
        "time": "23:00-07:00"
    }]
    # priceMode = [{
    #     "price": 1.21567,
    #     "time": "19:00-22:00"
    # }, {
    #     "price": 0.7151,
    #     "time": "22:00-23:00"
    # }, {
    #     "price": 0.28604,
    #     "time": "23:00-07:00"
    # }]
    res = th.set_price_mode_car('YJDC12345600', priceMode)
    print('res=', res)


if __name__ == '__main__':
    # start_charge()
    # set_price_mode()

    # charge_stop()
    # handle.charge_start_notice('2021112300000153')
    handle.charge_end_notice('2021112300000153')
