"""
循环发送微信模板消息
"""
import os
import sys
sys.path.append("/app")

# 1. 设置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_cfg.settings')  # 修改为你的项目名

# 2. 将项目根目录添加到 Python 路径
sys.path.append('/app')  # 或者使用 os.path 动态获取

# 3. 初始化 Django
# import django
# django.setup()

import time
import datetime
from SmartChargeBD.settings import BASE_DIR
from app.models import SWxTempMsg
from app.utils import wx_temp_msg
from app.utils import MyLog


# log = MyLog.getLogger(__file__)
log = MyLog.MyLog(__file__, 'crontab.log', BASE_DIR).logger


def _get_kv(msg):
    kv = {'k1': msg.k1, 'k2': msg.k2, 'k3': msg.k3, 'k4': msg.k4, 'k5': msg.k5, 'k6': msg.k6, 'k7': msg.k7,
          'k8': msg.k8, 'url': msg.url}
    if msg.xcx_app_id and msg.xcx_path:
        mini_program = {
            'appid': msg.xcx_app_id,
            'pagepath': msg.xcx_path
        }
        kv['mini_program'] = mini_program
    return kv


def handle_main():
    msgs = SWxTempMsg.objects.filter(state='0')
    print('hahaha', msgs)
    for msg in msgs:
        log.info(f'start handle msg.id={msg.id}')
        send_result = False
        _kv = _get_kv(msg)
        # 充电开始通知
        if msg.temp_type == 'charge_start':
            send_result = wx_temp_msg.send_charge_start_notice(
                open_id=msg.open_id,
                **_kv
            )
        # 充电结束通知
        elif msg.temp_type == 'charge_end':
            send_result = wx_temp_msg.send_charge_end_notice(
                open_id=msg.open_id,
                **_kv
            )
        else:
            pass
        log.info(f'id={msg.id},send_result={send_result}')
        msg.handle_time = datetime.datetime.now()
        msg.state = '1' if send_result else '9'
        msg.save()


def main():
    print('start')
    log.info('do_send_wx_temp_msg main start')
    while True:
        try:
            handle_main()
        except:
            log.error('send_wx_temp_msg error', exc_info=True)
        time.sleep(5)
