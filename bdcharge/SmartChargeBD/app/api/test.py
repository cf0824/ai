"""
test
"""
import json

from app.utils.eq_api import tieta_handle2
from app.utils.comm import api_handle
from app.utils import Error
from app.utils import MyLog
from app.models import *
from app.utils import wx_pay
from app.utils import get_seq

log = MyLog.log


# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


def test_set_price_mode(request, data, resp):
    log.info('请求信息=%s' % data)
    th = tieta_handle2.TietaHandle(SCmdDetail)
    eq_code = data.get('eq_code')
    priceMode = data.get('set_attr')
    if not eq_code or not priceMode:
        return Error.REQ_PARAMS_ERROR
    priceMode = json.loads(priceMode)
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
    res = th.set_price_mode_car(eq_code, priceMode)
    resp['res'] = res
    return resp


def test_cash_out(request, data, resp):
    # wx_pay.wx_cash_out('test20220823002', '测试082302', 50, 'oQUYz5AOW6kJSialCLsW1b5XgnJo')
    order = get_seq.Get_SeqNo('WX_CASHOUT_ORDER')
    resp['order_id'] = order
    return resp


def test_cash_out_result(request, data, resp):
    wx_pay.get_wx_cash_out_result()
    return resp
