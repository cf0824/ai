import datetime
import decimal
import hashlib
import json
import string
import random
import os
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

import django
from django.shortcuts import redirect

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()

from wechatpy import parse_message
from wechatpy.replies import TextReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from SmartChargeBD.settings import WX_TOKEN
from app.utils import wx as wx_handle
from app.utils import handle
from app.models import SUserInfo
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
from SmartChargeBD.settings import BASE_DIR
# log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger
log = MyLog.MyLog(__file__, 'wx.log', BASE_DIR).logger


# appID      wx60f8c5b894003268
# appsecret  1aeca1fbd592dec057f44f0fedaf850c


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        super(MyJSONEncoder, self).default(o)

def return_resp(resp):
    s = json.dumps(resp, cls=MyJSONEncoder)
    log.info(f'resp:{s}')
    return HttpResponse(s)


# 公众号关注处理
def wx_follow_handle(msg):
    open_id = msg.source
    log.info(f'open_id:{open_id}')
    try:
        user_info = wx_handle.get_wx_user_info(open_id)
    except Exception as e:
        log.error(f'获取用户信息出现错误：{e}', exc_info=True)
    log.info(f'user_info: {user_info}')
    union_id = user_info.get('unionid')
    open_id = user_info.get('openid')
    log.info(f'union_id={union_id},open_id={open_id}')
    handle.create_or_update_user(union_id, wx_open_id=open_id)
    return _send_text('欢迎关注！', msg)


def _send_text(reply_text, msg):
    reply = TextReply(content=reply_text, message=msg)
    xml = reply.render()
    return HttpResponse(xml)


def _handle_event(msg):
    log.info(f'event={msg.event}')
    log.info(f'from={msg.source}')
    if msg.event == 'subscribe':
        log.info('关注事件')
        return wx_follow_handle(msg)
    elif msg.event == 'unsubscribe':
        log.info('取消关注事件')

    return None



def _handle_text(msg):
    content = msg.content
    log.info(f'content: {content}')
    reply_text = f'收到：{msg.content}'
    # reply = TextReply(content=reply_text, message=msg)
    # xml = reply.render()
    # return HttpResponse(xml)

    return reply_text



def test_temp(request):
    from app.utils.wx_temp_msg import send_charge_start_notice
    user_id = 'okML07DrIuhpO6CnFxy4u_dS0Prw'
    data_start = {
        'first': '充电开始',
        'begin_time': '2025-01-01 00:00:00',
        'charge_type': '充满自停',
        'eq_id': '100002',
        'eq_port': '01',
        'remark': '注意用电安全'
    }
    log.info(request)
    if request.method != 'POST':
        return HttpResponseBadRequest('error')
    try:
        res = send_charge_start_notice(user_id, data_start)
    except Exception as e:
        log.error(e, exc_info=True)
    log.info(res)
    return HttpResponse(res)

def wx(request):
    log.info(f'{request}')
    get = request.GET
    # body = request.body.decode('utf-8')
    # log.info(f'body: {body}, type:{type(body)}')
    # log.info(f'get: {get}, type: {type(get)}')

    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    openid = request.GET.get('openid')
    echostr = request.GET.get('echostr')
    log.info(f'signature: {signature}, timestamp: {timestamp}, nonce: {nonce}, openid: {openid}, echostr: {echostr}')
    try:
        check_signature(WX_TOKEN, signature, timestamp, nonce)
        log.info('验证成功')
    except InvalidSignatureException:
        log.info('验证失败')
        return HttpResponse('验证失败')

    xml = request.body
    msg = parse_message(xml)
    if not msg:
        return HttpResponse(echostr)

    log.info(f'msg: {msg}, type: {type(msg)}')

    resp = None
    log.info(f'msg_type: {msg.type}')

    if msg.type == 'event':
        resp = _handle_event(msg)
    elif msg.type == 'text':
        resp = _handle_text(msg)

    if not resp:
        if echostr:
            log.info('回复', echostr)
            return HttpResponse(echostr)
        log.info('回复success')
        return HttpResponse('success')
    return HttpResponse(resp)


def get_random_str(_len):
    _str = ''.join(random.sample(string.ascii_letters + string.digits, _len))
    return _str



def redirect_miniprogram(request):
    log.info(f'{request}')
    return HttpResponseRedirect('#小程序://一路活动/0SoMp1kIdfhzdYx')


# log.info(get_random_str(32))


