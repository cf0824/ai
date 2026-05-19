import datetime
import decimal
import hashlib
import json
import string
import random
import os
from django.http import HttpResponse

import django
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
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger



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
    user_info = wx_handle.get_wx_user_info(open_id)
    union_id = user_info.get('unionid')
    open_id = user_info.get('openid')
    handle.create_or_update_user(union_id, wx_open_id=open_id)
    return _send_text('欢迎关注！', msg)


def _send_text(reply_text, msg):
    reply = TextReply(content=reply_text, message=msg)
    xml = reply.render()
    return HttpResponse(xml)


def _handle_event(msg):
    if msg.event == 'subscribe':
        print('关注事件')
        return wx_follow_handle(msg)
    elif msg.event == 'unsubscribe':
        print('取消关注事件')

    return None



def _handle_text(msg):
    print('content=', msg.content)
    reply_text = f'收到：{msg.content}'
    # reply = TextReply(content=reply_text, message=msg)
    # xml = reply.render()
    # return HttpResponse(xml)

    return None

def test(request):
    log.info(request)
    return return_resp('a')

def wx(request):
    log.info(f'{request}')

    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')
    try:
        check_signature(WX_TOKEN, signature, timestamp, nonce)
        # print('验证成功')
    except InvalidSignatureException:
        # print('验证失败')
        return HttpResponse('验证失败')

    xml = request.body
    msg = parse_message(xml)
    if not msg:
        return HttpResponse(echostr)

    resp = None

    if msg.type == 'event':
        resp = _handle_event(msg)
    elif msg.type == 'text':
        resp = _handle_text(msg)

    if not resp:
        if echostr:
            return HttpResponse(echostr)
        return HttpResponse('success')
    return HttpResponse(resp)


def get_random_str(_len):
    _str = ''.join(random.sample(string.ascii_letters + string.digits, _len))
    return _str




