"""
循环发送微信模板消息
"""
import json
import os
import sys
import time
import datetime

import django

pwd = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(pwd)
parent_dir_ = os.path.dirname(parent_dir)
print(pwd)
print(parent_dir)
print(parent_dir_)
print(sys.path)
sys.path.append(pwd)
sys.path.append(parent_dir)
sys.path.append(parent_dir_)
print(sys.path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()


from app.models import SWxTempMsg
from app.utils import wx_temp_msg
from SmartChargeBD.settings import WX_XCX_APP_ID

from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger



def handle_main():
    msgs = SWxTempMsg.objects.filter(state='0')
    for msg in msgs:
        try:
            log.info(f'发送模板消息')
            send_result = False
            data = msg.send_data
            data = json.loads(data)
            open_id = msg.wx_open_id
            # 充电开始通知
            if msg.msg_type == 'charge_open':
                log.info(f'充电开启')
                orderNum = data.get('order_id')
                mini_program = {
                    'appid': WX_XCX_APP_ID,
                    'pagepath': f'/pages/Charge/Orderdetail?orderNum={orderNum}'
                }
                send_result = wx_temp_msg.send_charge_start_notice(
                    open_id=open_id,
                    data=data,
                    mini_program=mini_program
                )
                log.info(f'发送结果：{send_result}')
            # 充电结束通知
            elif msg.msg_type == 'charge_end':
                log.info(f'充电结束')
                orderNum = data.get('order_id')
                mini_program = {
                    'appid': WX_XCX_APP_ID,
                    'pagepath': f'/pages/Charge/Orderdetail?orderNum={orderNum}'
                }
                send_result = wx_temp_msg.send_charge_stop_notice(
                    open_id=open_id,
                    data=data,
                    mini_program=mini_program
                )
                log.info(f'发送结果：{send_result}')
            else:
                pass
            log.info(f'id={msg.id},send_result={send_result}')
            msg.handle_time = datetime.datetime.now()
            msg.state = '1' if send_result else '-1'
            msg.save()
        except Exception as e:
            log.error(f'模板消息发送失败：{e}', exc_info=True)


def main():
    log.info('do_send_wx_temp_msg main start')
    while True:
        try:
            handle_main()
        except:
            log.error('send_wx_temp_msg error', exc_info=True)
        time.sleep(3)


if __name__ == '__main__':
    main()