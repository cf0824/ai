"""
todo 模板消息相关接口
"""
# 本地运行导入
# import re
# import sys
# import os

# 添加当前路径到环境变量中

# pwd = os.path.dirname(os.path.realpath(__file__))
# pwd = pwd.replace(r'\charge\utils', '').replace(r'/charge/utils', '')
# # pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')  # VueSt是自己的项目名称
# django.setup()  # 更新配置

# from SmartChargeBD.settings import WX_XCX_APP_ID
# from app.utils.wx import get_wechat_client
#
# from app.utils import MyLog
# file_name = os.path.basename(__file__)[:-3]
# file_path = os.path.dirname(__file__)
# print(file_path)
# print(file_name)
# log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger


import requests
import json
import os
from SmartChargeBD.settings import WX_XCX_APP_ID
from app.utils.wx import get_wechat_client
from app.utils import MyLog
from django.http import HttpResponseRedirect

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger




# 发送模板消息
def _send_temp_msg(user_id, template_id, data, url=None, mini_program=None, wechat_client=None):
    log.info(f'发送模板消息')
    log.info(f'{user_id}')
    if not wechat_client:
        wechat_client = get_wechat_client()
    try:
        res = wechat_client.message.send_template(user_id, template_id, data, url=url, mini_program=mini_program)
    except Exception as e:
        log.error(f'send_temp error:{e}', exc_info=True)
        res = {'errcode': -1}

    log.info(f'send res={res}')
    if res.get('errcode') == 0:
        return True
    return False


# 发送开始充电通知
def send_charge_start_notice_bak(open_id, **kwargs):
    TEMPLATE_ID = '9-4bn4koH9f6iK1CuQjsm1E-x_11ZWFcsM1dtuQZUZhn0'
    data = {
        'first': {
            'value': kwargs.get('first')
        },
        'keyword1': {
            'value': kwargs.get('keyword1')
        },
        # 'keyword2': {
        #     'value': kwargs.get('k3')
        # },
        # 'keyword3': {
        #     'value': kwargs.get('k4')
        # },
        # 'keyword4': {
        #     'value': kwargs.get('k5')
        # },
        'remark': {
            'value': kwargs.get('remark')
        }
    }
    url = kwargs.get('url')
    mini_program = kwargs.get('mini_program')
    res = _send_temp_msg(open_id, TEMPLATE_ID, data, url=url, mini_program=mini_program)
    log.info(f'res={res}')
    return res

def send_charge_start_notice(open_id, data, url=None, mini_program=None):
    log.info(f'模板消息：【充电开启】')
    TEMPLATE_ID = 'bUZyCNP3WV9dotFFJsfIfp2mioauEinXNqRFfZH4LkI'
    log.info(f'open_id={open_id},data={data}')
    data = {
        'character_string2': {
            'value':data.get('order_id')
        },
        'time4':{
            'value': data.get('begin_time')
        },
        'phrase11': {
            'value': data.get('charge_type')
        },
        'character_string20': {
            'value': data.get('eq_id')
        },
        'character_string14': {
            'value': data.get('eq_port')
        }
    }

    res = _send_temp_msg(open_id, TEMPLATE_ID, data, url=url, mini_program=mini_program)
    log.info(f'res={res}')
    return res


# 发送结束充电通知
# def send_charge_end_notice_bak(open_id, **kwargs):
#     TEMPLATE_ID = '4bn4koH9f6iK1CuQjsm1E-x_11ZWFcsM1dtuQZUZhn0'
#     data = {
#         'first': {
#             'value': kwargs.get('k1')
#         },
#         'keyword1': {
#             'value': kwargs.get('k2')
#         },
#         'keyword2': {
#             'value': kwargs.get('k3')
#         },
#         'keyword3': {
#             'value': kwargs.get('k4')
#         },
#         'keyword4': {
#             'value': kwargs.get('k5')
#         },
#         'keyword5': {
#             'value': kwargs.get('k6')
#         },
#         'remark': {
#             'value': kwargs.get('k7')
#         }
#     }
#     url = kwargs.get('url')
#     mini_program = kwargs.get('mini_program')
#     res = _send_temp_msg(open_id, TEMPLATE_ID, data, url=url, mini_program=mini_program)
#     log.info(f'res={res}')
#     return res

def send_charge_stop_notice(open_id, data, url=None, mini_program=None):
    log.info(f'模板消息：【充电结束】')
    TEMPLATE_ID = 'b6ccy-xZpn3TwbzCQUIryLCgpJgFFrUTH85adq4PZxk'
    log.info(f'open_id={open_id},data={data}')
    data = {
        'character_string2': {
            'value': data.get('order_id')
        },
        'short_thing14': {
            'value': data.get('use_time')
        },
        'time12': {
            'value': data.get('end_time')
        },
        'amount5': {
            'value': data.get('use_money')
        },
        'number15': {
            'value': data.get('use_electric')
        }
    }

    res = _send_temp_msg(open_id, TEMPLATE_ID, data, url=url, mini_program=mini_program)
    log.info(f'res={res}')
    return res





if __name__ == "__main__":
    user_id = 'ot--cxNch2ie5Ys7dr88x_OMNsNk'
    mini_program = {
        'appid': WX_XCX_APP_ID,
        'pagepath': 'pages/Orderdetail/index?orderNum="00000089"'
    }


    data_start = {
        'order_id': '11111111',
        'begin_time': '2025-01-01 00:00:00',
        'charge_type': '充满自停',
        'eq_id': '100002',
        'eq_port': '01'
    }

    # res = send_charge_start_notice(user_id, data_start, url='https://www.bilibili.com/video/BV1uT4y1P7CX?spm_id_from=333.788.recommend_more_video.-1&vd_source=4300d5e99cf849a47b3962133d7554da')
    # print('res=', res)

    data_stop = {
        'order_id': '11111111',
        'use_time': '2分钟',
        'end_time': '2022-12-01 23:59:59',
        'use_money': '66.00元',
        'use_electric': '1.2'
    }
    res = send_charge_stop_notice(user_id, data_stop)
    # print('res=', res)
    # res = send_charge_end_notice(user_id, k1='尊敬的用户，您好，您的爱车已经结束充电。', k2='800001', k3='2021-11-24 15:21:12', k4='20分钟', k5='1.35元', k6='充满自停', k7='感谢您的使用', mini_program=mini_program)
    # print('res=', res)
