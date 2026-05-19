import re
import sys
import os
import time
import pymysql
import django
import datetime



import json
import datetime
from app.models import *
from app.utils.eq_api.tieta_api import TietaApi

api = TietaApi()




# 添加命令
def add_cmd(eq_code, cmd, seq_no=None):
    SCmdDetail.objects.create(
        cmd=cmd,
        eq_code=eq_code,
        send_type='1',
        seq_no=seq_no,
        create_time=datetime.datetime.now(),
        state='0'
    )


# 完成命令
def end_cmd(cmd):
    cmd.state = '1'
    cmd.handle_time = datetime.datetime.now()
    cmd.save()


# 处理注册
def handle_register(devId, txnNo, cmd):
    reply_cmd = api.reply_register(devId, txnNo, True)
    add_cmd(devId, reply_cmd, txnNo)
    end_cmd(cmd)


# 处理属性上报
def handle_attr_up(devId, txnNo, cmd):
    reply_cmd = api.reply_attr_up(devId, txnNo, True)
    add_cmd(devId, reply_cmd, txnNo)
    end_cmd(cmd)


# 处理主函数
def handle_main(cmd):
    print('handle_main', cmd.cmd)
    data = json.loads(cmd.cmd)
    msgType = data.get('msgType')
    devId = data.get('devId')
    txnNo = data.get('txnNo')
    if not msgType:
        return
    if msgType == 110:
        handle_register(devId, txnNo, cmd)
    elif msgType == 310:
        handle_attr_up(devId, txnNo, cmd)
    else:
        end_cmd(cmd)


if __name__ == "__main__":
    while True:
        dt = datetime.datetime.now() - datetime.timedelta(hours=1)
        cmds = SCmdDetail.objects.filter(send_type='2', state='0', create_time__gte=dt)
        for cmd in cmds:
            handle_main(cmd)
        time.sleep(1)
