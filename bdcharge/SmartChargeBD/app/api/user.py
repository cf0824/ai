"""
用户相关接口
"""
import json
import time
import re

from django.db import transaction
from django.db.models import F

from app.models import SUserInfo, SWxTranDetail
from app.models_view import ViewUserAccountOk
from app.utils.comm import api_handle
from app.utils import token_handle, Error
from SmartChargeBD.settings import WX_XCX_TOKEN_EXP_TIME
from app.models import *
import datetime
from django.core.paginator import Paginator
from django.db.models import Sum
from decimal import Decimal
from app.utils import wx
from app.utils import get_seq
from app.utils import wx_pay
from app.utils import handle

from app.utils import MyLog

log = MyLog.log

# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


def test(request, data, resp):
    print('test')
    return resp


@transaction.atomic()
def create_sub_order(request, data, resp):
    # 参数
    user_id = data.get('user_id')
    eq_id = data.get('eq_id') # 充电桩id
    charge_type = data.get('charge_type')  # 充电类型
    order_source = data.get('order_source')
    pay_way = data.get('pay_way')
    charge_electric = data.get('charge_electric', 0)  # 定电量充电
    charge_money = data.get('charge_money', 0)  # 定金额充电金额
    charge_time = data.get('charge_time', 0)  # 定时充电时长
    SocketNumber = data.get('SocketNumber')  # 插座号
    eq_id = int(eq_id)

    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    # if not user.phone_number or not user.wx_nickname:
    #     resp['success'] = False
    #     resp['tip'] = '请完善个人信息，以便确认您的身份'
    #     return resp

    # 1）查询充电桩状态
    try:
        eq_info = SEqInfo.objects.get(eq_id=eq_id)
        port_info = SEqPort.objects.get(eq_id=eq_id, eq_port=SocketNumber)
    except:
        return Error.CONTENT_NOT_FOUND

    site_id = eq_info.site_id
    site_info = SSiteInfo.objects.filter(site_id=site_id)
    if site_info.exists():
        site_state = site_info[0].state
        if site_state == '0':
            resp['success'] = False
            resp['tip'] = '该站点为禁用状态'
            return resp

    else:
        resp['success'] = False
        resp['tip'] = '站点不存在'
        return resp

    terminal_address = eq_info.terminal_address  # 充电桩地址
    log.info(f'eq_info: {eq_info}')
    conn_state = eq_info.conn_state
    log.info(f'conn_state: {conn_state}')
    # eq_state = eq_info.eq_state
    # log.info(f'eq_state: {eq_state}')
    port_state = port_info.state
    port_use_state = port_info.use_state
    port_conn_state = port_info.conn_state
    if conn_state != '1':
        return Error.TERMINAL_ERROR
    # if eq_state == '1':
    #     return Error.TERMINAL_OCCUPY
    if port_use_state == '1':
        return Error.TERMINAL_OCCUPY
    if port_conn_state == '0':
        return Error.TERMINAL_ERROR
    if port_state == '-1':
        return Error.TERMINAL_ERROR
    # 分钟转换为秒
    # charge_time = float(charge_time) * 60
    if not all([eq_id, user_id, charge_type]):
        return Error.REQ_PARAMS_ERROR
    if charge_type == 'elec':
        resp["success"] = False
        resp["tip"] = "按电量不可在线支付"
        return resp
    elif charge_type == 'money' and float(charge_money) <= 0:
        resp["success"] = False
        resp["tip"] = "金额需大于0"
        return resp
    elif charge_type == 'time':
        resp["success"] = False
        resp["tip"] = "按时间不可在线支付"
        return resp
    order_id = get_seq.Get_SeqNo("PAY_CHARGE_ORDER")

    # 乐观锁，防止同一台设备并发下单情况
    # res = SEqInfo.objects.filter(eq_id=eq_id, state='1', eq_state='0').update(eq_state='1')
    res = SEqPort.objects.filter(terminal_address=terminal_address, use_state='0', eq_port=SocketNumber).update(use_state='1')
    if res == 0:
        resp['success'] = False
        resp['tip'] = '充电口非空闲状态，请重新选择'
        return resp
    # 设备计价规则
    eq_fee_type = eq_info.fee_type
    eq_fee_no = eq_info.fee_no
    # create order
    SOrderNumMap.objects.create(
        site_id=site_id,
        eq_id=eq_id,
        eq_port=SocketNumber,
        term_address=terminal_address,
        charge_money=charge_money,
        fee_type=eq_fee_type,
        fee_no=eq_fee_no,
        user_id=user_id,
        sub_order=order_id,
        create_time=datetime.datetime.now(),
        order_source=order_source
    )
    resp['order_id'] = order_id
    resp['info'] = '提交成功'
    resp['success'] = True
    return resp

@transaction.atomic()
def error_charge_payment(request, data, resp):
    user_id = data.get('user_id')
    payment_result = data.get('payment_result')
    order_id = data.get('order_id')
    if not all([user_id, payment_result, order_id]):
        return Error.REQ_PARAMS_ERROR

    # 查询订单相关信息
    sub_order_info = SOrderNumMap.objects.filter(sub_order=order_id)
    if not sub_order_info:
        return Error.CONTENT_NOT_FOUND

    eq_id = sub_order_info[0].eq_id
    eq_port = sub_order_info[0].eq_port
    terminal_address = sub_order_info[0].term_address
    # 释放端口
    log.info(f'释放端口')
    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=eq_port).update(
        use_state='0'
    )
    # 更新微信支付信息
    SWxTranOrderDetail.objects.filter(order_id=order_id).update(
        state='-1',
        remark=payment_result
    )
    resp['success'] = True
    return resp



def charge_online_pay(request, data, resp):
    """
    充电在线支付
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    charge_money = data.get('recharge_amount')
    order_id = data.get('order_id')
    recharge_amount = charge_money  # 充值金额
    if not all([user_id, recharge_amount]):
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND

    open_id = user.xcx_open_id

    amount = int(float(recharge_amount) * 100)
    desc = "订单在线支付"
    # 这一步是真正充钱的操作）
    success, detail = wx_pay.create_order(open_id, order_id, amount, desc)
    if not success:
        resp['success'] = False
        resp['tip'] = detail
        return resp
    resp['success'] = True
    resp['tip'] = '创建成功'
    resp['order_id'] = order_id
    resp['detail'] = detail
    # 创建充电订单微信交易记录
    SWxTranOrderDetail.objects.create(
        change_type='in',
        change_money=float(recharge_amount),
        user_id=user_id,
        order_id=order_id,
        verify_state='1',
        verify_time=datetime.datetime.now(),
        create_time=datetime.datetime.now(),
        state='1'
    )
    return resp


def charge_online_pay1(request, data, resp):
    """
    充电在线支付
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    order_id = data.get('order_id')
    charge_money = data.get('charge_money')
    recharge_amount = charge_money  # 充值金额
    if not all([user_id, recharge_amount]):
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    
    open_id = user.xcx_open_id

    order_id = "CHARGE_PAY" + order_id
    amount = int(float(recharge_amount) * 100)
    desc = "订单在线支付"
    # 这一步是真正充钱的操作）
    success, detail = wx_pay.create_order(open_id, order_id, amount, desc)
    if not success:
        resp['success'] = False
        resp['tip'] = detail
        return resp
    resp['success'] = True
    resp['tip'] = '创建成功'
    resp['order_id'] = order_id
    resp['detail'] = detail
    # 创建充电订单微信交易记录
    SWxTranCardDetail.objects.create(
        change_type='in',
        change_money=float(recharge_amount),
        user_id=user_id,
        order_id=order_id,
        verify_state='1',
        verify_time=datetime.datetime.now(),
        create_time=datetime.datetime.now(),
        state='1'
    )
    return resp


@transaction.atomic
def card_bind(request, data, resp):
    """
    电卡绑定
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    card_num = data.get('card_num')
    user_name = data.get('user_name')
    tel = data.get('tel')
    if not user_id or not card_num or not user_name:
        return Error.REQ_PARAMS_ERROR
    # 检查用户是否绑定过卡
    user_info = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    user_card_info = SCardsInfo.objects.filter(user_id=user_id).first()
    if user_info.card_num or user_card_info:
        resp['tips'] = f'该用户已绑定卡:{user_info.card_num}'
        resp['success'] = False
        return resp
    # 检查卡库
    card_info = SCardLibrary.objects.filter(card_no=card_num)[0]
    if not card_info:
        resp['tips'] = '卡号无效'
        resp['success'] = False
        return resp
    if card_info.bind_state == '1':
        resp['tips'] = '此卡已被绑定'
        resp['success'] = False
        return resp
    if card_info.is_enable == '0':
        resp['tips'] = '此卡未启用'
        resp['success'] = False
        return resp

    # 查用户信息
    user_info = SUserInfo.objects.filter(user_id=user_id)[0]
    if not user_info.phone_number:
        resp['tips'] = '请完善个人信息'
        resp['success'] = False
        return resp
    # phone_number = user_info.phone_number
    # if tel != phone_number:
    #     resp['tips'] = '手机号错误'
    #     resp['success'] = False
    #     return resp
    # card_info = SCardsInfo.objects.filter(card_num=card_num).first()
    # if not card_info:
    #     resp['tips'] = '卡号无效'
    #     resp['success'] = False
    #     return resp
    # if card_info.user_id:
    #     resp['success'] = False
    #     resp['tips'] = '此卡已被绑定'
    #     return resp
    # if card_info.tel != tel:
    #     resp['success'] = False
    #     resp['tips'] = '手机号错误'
    #     return resp
    # 绑定电卡
    SUserInfo.objects.filter(user_id=user_id).update(
        card_num=card_num
    )
    SCardLibrary.objects.filter(card_no=card_num).update(
        bind_state='1',
        bind_time=datetime.datetime.now()
    )
    SCardsInfo.objects.create(
        card_sn=card_info.card_sn,
        card_num=card_num,
        user_id=user_id,
        user_name=user_name,
        tel=tel,
        money=0,
        gift_money=0,
        use_state='0',
        state='1'
    )
    resp['success'] = True
    resp['tips'] = '绑定成功'
    return resp

@transaction.atomic
def card_unbind(request, data, resp):
    """
    电卡解绑
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    card_num = data.get('card_num')
    # 检查电卡
    card_info = SCardsInfo.objects.filter(card_num=card_num).first()
    if not card_info:
        resp['tips'] = '卡号无效'
        resp['success'] = False
        return resp
    if card_info.user_id != user_id:
        resp['success'] = False
        resp['tips'] = '此卡不属于当前用户'
        return resp

    if card_info.money > 0:
        resp['success'] = False
        resp['tips'] = '此卡还有余额'
        return resp

    # 绑定电卡
    SUserInfo.objects.filter(user_id=user_id).update(
        card_num=None
    )
    SCardsInfo.objects.filter(card_num=card_num).delete()
    SCardLibrary.objects.filter(card_no=card_num).update(
        bind_state='0'
    )
    resp['success'] = True
    resp['tips'] = '解绑成功'
    return resp

def get_feedback_list(request, data, resp):
    """
    获取反馈列表
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    # 获取反馈内容
    feedback_info = SFeedbackDetail.objects.filter(user_id=user_id, feed_type='opinion')
    feedback_list = []
    for feedback in feedback_info:
        id = feedback.id
        create_time = feedback.create_time
        state = feedback.state
        feedback_content = feedback.feedback_content
        reply_text = ''
        if state == '0':
            reply_text = '待回复'
        if state == '1':
            reply_text = '已回复'
        detail = {
            'id': id,
            'create_time': create_time,
            'reply_text': reply_text,
            'feedback_content': feedback_content
        }
        feedback_list.append(detail)
    resp['feedback_list'] = feedback_list
    return resp

def get_feedback_detail(request, data, resp):
    """
    获取反馈详情
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    if not user_id or not feedback_id:
        return Error.REQ_PARAMS_ERROR
    # 获取反馈详情
    feedback_info = SFeedbackDetail.objects.filter(user_id=user_id, id=feedback_id).first()
    create_time = feedback_info.create_time
    state = feedback_info.state
    feedback_content = feedback_info.feedback_content
    reply_text = ''
    if state == '0':
        reply_text = '待回复'
    if state == '1':
        reply_text = '已回复'
    image_list = []
    images = feedback_info.feedback_img
    # import json
    image_list = json.loads(images.replace("'", '"'))

    log.info(f'图片信息：{image_list}, 长度{len(image_list)}')
    # if images:
    #     for image in images:
    #         image_list.append(image)
    reply_content = feedback_info.reply
    resp['create_time'] = create_time
    resp['feedback_content'] = feedback_content
    resp['image_list'] = image_list
    resp['reply_text'] = reply_text
    resp['reply_content'] = reply_content
    return resp

def get_feedback_order_list(request, data, resp):
    """
    获取反馈列表
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    # 获取反馈内容
    feedback_info = SFeedbackDetail.objects.filter(user_id=user_id, feed_type='complain')
    feedback_list = []
    for feedback in feedback_info:
        id = feedback.id
        create_time = feedback.create_time
        state = feedback.state
        order_id = feedback.order_id
        feedback_content = feedback.feedback_content
        reply_text = ''
        if state == '0':
            reply_text = '待回复'
        if state == '1':
            reply_text = '已回复'
        detail = {
            'id': id,
            'create_time': create_time,
            'reply_text': reply_text,
            'order_id': order_id,
            'feedback_content': feedback_content
        }
        feedback_list.append(detail)
    resp['feedback_list'] = feedback_list
    return resp

def get_feedback_order_detail(request, data, resp):
    """
    获取反馈详情
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    if not user_id or not feedback_id:
        return Error.REQ_PARAMS_ERROR
    # 获取反馈详情
    feedback_info = SFeedbackDetail.objects.filter(user_id=user_id, id=feedback_id).first()
    create_time = feedback_info.create_time
    state = feedback_info.state
    order_id = feedback_info.order_id
    feedback_content = feedback_info.feedback_content
    reply_text = ''
    if state == '0':
        reply_text = '待回复'
    if state == '1':
        reply_text = '已回复'
    image_list = []
    images = feedback_info.feedback_img
    # import json
    if images:
        image_list = json.loads(images.replace("'", '"'))
    ImgUrls = feedback_info.reply_img
    ImgUrls_list = []
    if ImgUrls:
        ImgUrls_list = json.loads(ImgUrls.replace("'", '"'))

    log.info(f'图片信息：{image_list}, 长度{len(image_list)}')
    # if images:
    #     for image in images:
    #         image_list.append(image)
    reply_content = feedback_info.reply
    resp['create_time'] = create_time
    resp['order_id'] = order_id
    resp['feedback_content'] = feedback_content
    resp['image_list'] = image_list
    resp['reply_text'] = reply_text
    resp['reply_content'] = reply_content
    resp['ImgUrls'] = ImgUrls_list
    return resp



def get_cards_list(request, data, resp):
    """ 2025年2月21日10点43分
    获取用户卡信息
    :param request:
    :param data:
    :param resp:
    :return:
    """
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    # uid = str(user.user_id).rjust(6, '0')
    card_num = user.card_num
    cards_list = []

    log.info(f'用户卡号：{card_num}')
    card_info = SCardsInfo.objects.filter(card_num=card_num, user_id=user_id).first()
    if card_info:
        money = card_info.money
        gift_money = card_info.gift_money
        tel = card_info.tel

        card_info = {
            'card_num': card_num,
            'tel': tel,
            'ok_money': money,
            'gift_money': gift_money
        }
        cards_list.append(card_info)


    resp['cards_list'] = cards_list
    return resp


# 获取电卡充值记录
def get_card_recharge_list(request, data, resp):
    card_num = data.get('card_num')
    user_id = data.get('user_id')
    if not all([user_id, card_num]):
        return Error.REQ_PARAMS_ERROR
    card_recharge_info = SCardRechargeDetail.objects.filter(card_num=card_num, user_id=user_id)
    onlineList = []
    offlineList = []
    if card_recharge_info:
        for item in card_recharge_info:
            recharge_type = item.recharge_type
            card_num = item.card_num
            create_time = item.create_time
            money = item.recharge_money
            detail = {
                'card_num': card_num,
                'create_time': create_time,
                'money': money
            }
            if recharge_type == 'online':
                onlineList.append(detail)
            elif recharge_type == 'offline':
                offlineList.append(detail)
    resp['onlineList'] = onlineList
    resp['offlineList'] = offlineList
    return resp


# 获取卡线上充值记录
def get_card_online_recharge_list(request, data, resp):

    # card_num = data.get('card_num')
    user_id = data.get('user_id')
    page = data.get('page', 1)
    s_year = data.get('s_year')
    s_month = data.get('s_month')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    # 获取用户卡号
    user_info = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user_info:
        return Error.USER_NOT_FOUND
    card_num = user_info.card_num

    if s_year and s_month:
        card_recharge_info = SCardRechargeDetail.objects.filter(recharge_type='online', card_num=card_num, user_id=user_id, create_time__year=s_year, create_time__month=s_month).order_by('-id')
    else:
        card_recharge_info = SCardRechargeDetail.objects.filter(card_num=card_num, recharge_type='online', user_id=user_id).order_by('-id')
    list_all = []
    for item in card_recharge_info:
        card_num = item.card_num
        create_time = item.create_time
        money = item.recharge_money
        transaction_id=item.transaction_id
        detail = {
            'card_num': card_num,
            'create_time': create_time,
            'money': money,
            'transaction_id': transaction_id
        }
        list_all.append(detail)
    paginator = Paginator(list_all, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_all)
    resp['list'] = list_page_data
    return resp

# 获取卡线下充值记录
def get_card_offline_recharge_list(request, data, resp):

    # card_num = data.get('card_num')
    user_id = data.get('user_id')
    page = data.get('page', 1)
    s_year = data.get('s_year')
    s_month = data.get('s_month')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    # 获取用户卡号
    user_info = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user_info:
        return Error.USER_NOT_FOUND
    card_num = user_info.card_num

    if s_year and s_month:
        card_recharge_info = SCardRechargeDetail.objects.filter(recharge_type='offline', card_num=card_num, user_id=user_id, create_time__year=s_year, create_time__month=s_month).order_by('-id')
    else:
        card_recharge_info = SCardRechargeDetail.objects.filter(card_num=card_num, recharge_type='offline', user_id=user_id).order_by('-id')
    list_all = []
    for item in card_recharge_info:
        card_num = item.card_num
        create_time = item.create_time
        money = item.recharge_money
        detail = {
            'card_num': card_num,
            'create_time': create_time,
            'money': money
        }
        list_all.append(detail)
    paginator = Paginator(list_all, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_all)
    resp['list'] = list_page_data
    return resp


# 电卡充值
def card_recharge(request, data, resp):
    user_id = data.get('user_id')
    card_num = data.get('card_num')
    recharge_amount = data.get('recharge_amount')  # 充值金额
    if not all([user_id, recharge_amount]):
        return Error.REQ_PARAMS_ERROR

    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    if not user.phone_number or not user.wx_nickname:
        resp['success'] = False
        resp['tip'] = '请完善个人信息，以便确认您的身份'
        return resp
    card_info = SCardsInfo.objects.filter(user_id=user_id, card_num=card_num).first()
    if not card_info:
        return Error.CARD_NOT_FOUND
    open_id = user.xcx_open_id
    card_sn = card_info.card_sn

    order_id = get_seq.Get_SeqNo("PAY_CARD_ORDER")
    amount = int(float(recharge_amount) * 100)
    desc = "电卡充值"
    # 这一步是真正充钱的操作）
    success, detail = wx_pay.create_order(open_id, order_id, amount, desc)
    if not success:
        resp['success'] = False
        resp['tip'] = detail
        return resp
    resp['success'] = True
    resp['tip'] = '创建成功'
    resp['order_id'] = order_id
    resp['detail'] = detail
    # 创建微信交易记录
    SWxTranCardDetail.objects.create(
        card_sn=card_sn,
        card_num=card_num,
        change_type='in',
        change_money=float(recharge_amount),
        user_id=user_id,
        order_id=order_id,
        verify_state='1',
        verify_time=datetime.datetime.now(),
        create_time=datetime.datetime.now(),
        state='1'
    )
    return resp

def user_collection_verify(request, data, resp):
    """
    用户确认收款
    :param request:
    :param data:
    :param resp:
    :return:
    """
    from SmartChargeBD.settings import WX_PAY_MCH_ID,WX_XCX_APP_ID
    user_id = data.get('user_id')
    order_id = data.get('order_id')
    cashout_order = SWxCashoutDetail.objects.filter(order_id=order_id, user_id=user_id).first()
    if not cashout_order:
        return Error.CONTENT_NOT_FOUND
    # todo 如果是异步的，这里要调起微信查询转账状态
    log.info(f'提现订单信息：微信状态码-{cashout_order.wx_state_str}')
    if cashout_order.wx_state_str == 'WAIT_USER_CONFIRM':
        resp['success'] = True
        resp['mchId'] = WX_PAY_MCH_ID
        resp['appId'] = WX_XCX_APP_ID
        resp['package'] = cashout_order.package_info
        resp['wx_state'] = cashout_order.wx_state
    elif cashout_order.wx_state_str == 'PROCESSING':
        resp['success'] = False
        resp['wx_state_str'] = cashout_order.wx_state_str
        resp['wx_state'] = cashout_order.wx_state
        resp['tips'] = '商户账户余额不足'
    else:
        resp['success'] = False
        resp['wx_state'] = cashout_order.wx_state
        fail_reason = cashout_order.fail_reason

        start = fail_reason.find('{')
        end = fail_reason.rfind('}') + 1
        json_str = fail_reason[start:end].replace("'", "")
        data = json.loads(json_str)
        code = data['code']
        message = data['message']
        if code == 'NOT_ENOUGH' and '商户运营账户资金不足' in message:
            message = '商户账户余额不足,请联系商户'
        resp['tips'] = message
    return resp



#------------------------------------------------------------------------------------------------


# 登录
def login(request, data, resp):
    """

    :param request: tran_type,code,
    :param data: tran_type,code,
    :param resp:{'code': 0, 'msg': 'success', 'tran_type': tran_type}
    :return:
    """

    code = data.get('code')
    if not code:
        return Error.REQ_PARAMS_ERROR

    # 根据code获取openid等信息并转换成user_id
    res = wx.get_user_grant(code)
    if not res:
        return Error.NETWORK_ERROR
    log.info(f'res={res}')
    user = SUserInfo.objects.filter(xcx_open_id=res['open_id']).first()
    log.info(f'user={user}')
    # 第一次进入小程序
    if not user:
        user = handle.create_or_update_user(union_id=res['union_id'], xcx_open_id=res['open_id'],
                                            wx_session_key=res['session_key'])
        # todo 创建钱包信息
        ViewUserAccountOk.objects.create(
            user_id=user.user_id,
            real_money=0,
            ok_money=0,
            ice_money=0,
            gift_money=0
        )
    else:
        user.wx_session_key = res['session_key']
        # todo 前期没有union_id的适配下 后期去掉
        user.union_id = res['union_id']
        user.save()

    # 生成认证信息
    # user_id = 1
    user_id = user.user_id
    phone_number = user.phone_number
    log.info(f'user_id={user_id}')
    token = token_handle.create_token({
        'user_id': user_id,
        'grant_api': ['charge', 'user', 'information']
    }, WX_XCX_TOKEN_EXP_TIME)

    log.info(f'token={token}, type={type(token)}')

    # token过期时间戳
    exp_time = int(time.time()) + int(WX_XCX_TOKEN_EXP_TIME)

    # 2024.10.16 修改
    # resp['token'] = str(token, encoding='utf-8')
    resp['token'] = token.decode('utf-8')
    resp['exp_time'] = exp_time
    resp['phone_number'] = phone_number
    return resp


def get_phone_number(request, data, resp):
    """
    res = {
            errcode: 0,
            errmsg: "ok",
            phone_info: {
                phoneNumber: "18337433785",
                purePhoneNumber: "18337433785",
                countryCode: "86",
                watermark: {
                    timestamp: 1740467530,
                    appid: "wxc0b42dc374c5b90b",
                },
            },

        }
    :param request:
    :param data:
    :param resp:
    :return:
    """
    code = data.get('code')
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    if not code:
        return Error.REQ_PARAMS_ERROR

    log.info(f'code: {code}')

    # 获取access_token
    res = wx.get_access_token()
    if not res:
        return Error.NETWORK_ERROR
    log.info(f'res={res}')
    access_token = res['access_token']
    expires_in = res['expires_in']
    # 获取手机号
    phone_info = wx.get_user_phone_number(code, access_token)
    log.info(f'phone_info: {phone_info}')
    if not phone_info:
        resp['success'] = False
    phone_number = phone_info['phone_info'].get('phoneNumber')
    # 更新用户信息
    SUserInfo.objects.filter(user_id=user_id).update(phone_number=phone_number)

    resp['success'] = True
    resp['phone_number'] = phone_number
    return resp





# 获取账户信息.
def get_account_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    ok_account = ViewUserAccountOk.objects.filter(user_id=user_id).first()
    if not ok_account:
        money = 0
        ice_money = 0
    else:
        money = ok_account.ok_money
        ice_money = ok_account.ice_money
    # ice_amount_money = 0
    # ice_amount = SAccountIce.objects.filter(link_id=user_id, state='1')
    # if ice_amount.exists():
    #     for i in ice_amount:
    #         ice_amount_money += i.ice_amount
    # money = '%.2f' % list_data.account
    resp['money'] = '%.2f' % money
    resp['ice_money'] = '%.2f' % ice_money
    return resp


# 账户充值
def account_recharge(request, data, resp):
    user_id = data.get('user_id')
    recharge_amount = data.get('recharge_amount')  # 充值金额
    if not all([user_id, recharge_amount]):
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    if not user.phone_number or not user.wx_nickname:
        resp['success'] = False
        resp['tip'] = '请完善个人信息，以便确认您的身份'
        return resp
    open_id = user.xcx_open_id
    order_id = get_seq.Get_SeqNo("PAY_ORDER")
    amount = int(float(recharge_amount) * 100)
    desc = "账户充值"
    # 这一步是真正充钱的操作）
    success, detail = wx_pay.create_order(open_id, order_id, amount, desc)
    if not success:
        resp['success'] = False
        resp['tip'] = detail
        return resp
    resp['success'] = True
    resp['tip'] = '创建成功'
    resp['order_id'] = order_id
    resp['detail'] = detail
    # 创建微信交易记录
    SWxTranDetail.objects.create(
        change_type='in',
        change_money=float(recharge_amount),
        user_id=user_id,
        order_id=order_id,
        verify_state='1',
        verify_time=datetime.datetime.now(),
        create_time=datetime.datetime.now(),
        state='1'
    )
    return resp


# 获取充值结果
def get_recharge_result(request, data, resp):
    order_id = data.get('order_id')
    if not order_id:
        return Error.REQ_PARAMS_ERROR

    recharge_type = order_id[0:6]
    if recharge_type == 'WF_CAR':
        wx_order = SWxTranCardDetail.objects.filter(order_id=order_id).first()
    elif recharge_type == 'WF_PAY':
        wx_order = SWxTranDetail.objects.filter(order_id=order_id).first()
    else:
        resp['success'] = False
        resp['tip'] = '支付订单号格式有误'
        return resp
    if not wx_order:
        return Error.CONTENT_NOT_FOUND
    resp['state'] = wx_order.state
    resp['order_id'] = wx_order.order_id
    resp['transaction_id'] = wx_order.transaction_id
    resp['create_time'] = wx_order.create_time
    resp['finish_time'] = wx_order.finish_time
    return resp


# 获取消费记录
def get_cost_list(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    s_year = data.get('s_year')
    s_month = data.get('s_month')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    if s_year and s_month:
        list_data = SAccountDetail.objects.filter(user_id=user_id, change_type='out', create_time__year=s_year, create_time__month=s_month).order_by('-id')
    else:
        list_data = SAccountDetail.objects.filter(user_id=user_id, change_type='out').order_by('-id')
    list_all = []
    for i in list_data:
        list_all.append({
            'tabs': i.remark,
            'create_time': i.create_time,
            'change_money': -i.change_money
        })
    paginator = Paginator(list_all, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_all)
    resp['list'] = list_page_data
    return resp


# 获取充值记录
def get_recharge_list(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    s_year = data.get('s_year')
    s_month = data.get('s_month')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    # if s_year and s_month:
    #     list_data = SWxTranDetail.objects.filter(user_id=user_id, change_type='in', state='2', finish_time__year=s_year, finish_time__month=s_month).order_by('-id')
    # else:
    #     list_data = SWxTranDetail.objects.filter(user_id=user_id, change_type='in', state='2').order_by('-id')
    if s_year and s_month:
        list_data = SAccountDetail.objects.filter(user_id=user_id, change_type='in', create_time__year=s_year,
                                                  create_time__month=s_month).order_by('-id')
    else:
        list_data = SAccountDetail.objects.filter(user_id=user_id, change_type='in').order_by('-id')
    list_all = []
    for i in list_data:
        list_all.append({
            'tabs': i.remark,
            'transaction_id': i.transaction_id,
            'create_time': i.create_time,
            'change_money': i.change_money
        })
    paginator = Paginator(list_all, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_all)
    resp['list'] = list_page_data
    return resp


# 获取提现记录
def get_cash_list(request, data, resp):
    numList = [{'name': '申请中'},
               {'name': '审核中'},
               {'name': '已完成'}
               ]
    withdrawList = [
        {
            'change_monye': '100.00',
            'detail': [{'time': '2021-11-26 08:00'},
                       {'time': '2021-11-26 11:00','state': '1'},
                       {'time': '2021-11-26 11:01','state': '1'}
                       ]
        },
        {
            'change_monye': '100.00',
            'detail': [{'time': '2021-11-26 08:00'},
                       {'time': '2021-11-26 11:00','state': '1'},
                       {'time': '2021-11-26 11:01','state': '2','reason': '订单未完成'}
            ]
        }
    ]
    user_id = data.get('user_id')
    s_year = data.get('s_year')
    s_month = data.get('s_month')
    # page = data.get('page', 1)
    # size = data.get('size', 10)
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    objs = SWxCashoutDetail.objects.filter(user_id=user_id)
    if s_year and s_month:
        objs = objs.filter(create_time__year=s_year, create_time__month=s_month)
    objs = objs.order_by('-create_time')
    # paginator = Paginator(objs, size)
    # resp['num_pages'] = paginator.num_pages
    # resp['list_len'] = paginator.count
    # list_data = paginator.page(page).object_list
    list_all = []
    for item in objs:
        verify_state = item.verify_state  # 审核状态
        state = item.state  # 提现状态
        amount = item.amount  # 提现金额
        detail = {}
        state_detail = []
        detail['amount'] = amount
        # 提现发起时间
        state_detail.append({
            "time": item.create_time,
            "check_state": "0"
        })
        fail_reason = item.fail_reason
        if fail_reason:
            if '资金不足' in fail_reason:
                fail_reason = '商家资金不足，请请联系商家'
            elif 'OVERDUE_CLOSE' in fail_reason:
                fail_reason = '超时关闭'

        # 审核状态
        if verify_state == '1': # 审核成功
            state_detail.append({
                "time": item.verify_time,
                "verify_state": "1"
            })
            if state == '2': # 提现成功
                state_detail.append({
                    "time": item.pay_start_time,
                    "state": "1"
                })
            elif state == '9': # 提现失败
                state_detail.append({
                    "time": item.pay_start_time,
                    "state": "9",
                    "fail_reason": '未填写' if not fail_reason else fail_reason
                })
        elif verify_state == '9':   # 审核失败
            state_detail.append({
                "time": item.verify_time,
                "verify_state": "9",
                "fail_reason":'未填写' if not fail_reason else fail_reason
            })
        detail['state_detail'] = state_detail

        list_all.append(detail)
    resp['list'] = list_all
    return resp


# 账户提现
@transaction.atomic
def account_cash(request, data, resp):
    from app.utils.handle_order import HandleOrder
    handleorder = HandleOrder(log)
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    if not user.phone_number or not user.wx_nickname:
        resp['success'] = False
        resp['tip'] = '请完善个人信息，以便确认您的身份'
        return resp

    # 提取金额
    retail_out = float(data.get('change_out_money'))
    if retail_out < 0:
        return Error.REQ_PARAMS_ERROR
    if retail_out < 0.3:
        resp['success'] = False
        resp['tip'] = '提现最少不能低于0.3元'
        return resp
    if retail_out > 100:
        resp['success'] = False
        resp['tip'] = '单次提现不能超过100元'
        return resp
    # 设置回滚点
    # todo 存在事务嵌套
    sid = transaction.savepoint()
    # 先查询
    account = ViewUserAccountOk.objects.filter(user_id=user_id).first()
    if not account:
        resp['success'] = False
        resp['tip'] = '账户不存在'
        return resp
    old = float(account.ok_money)
    if old < retail_out:
        transaction.savepoint_rollback(sid)
        resp['success'] = False
        resp['tip'] = '可用余额不足'
        return resp
    # 插入待审核记录
    order_id = get_seq.Get_SeqNo("WX_CASHOUT_ORDER")
    SWxCashoutDetail.objects.create(
        order_id=order_id,
        amount=retail_out,
        user_id=user_id,
        open_id=user.xcx_open_id,
        create_time=datetime.datetime.now(),
        verify_time=datetime.datetime.now(),
        verify_state='1',
        state='0',
        user_varify_state='0'
    )
    SAccountIce.objects.create(
        ice_amount=retail_out,
        link_type='cashout',
        link_id=order_id,
        user_id=user_id,
        create_time=datetime.datetime.now(),
        update_time=datetime.datetime.now(),
        state='1'
    )
    # 冻结金额
    ice_result = handleorder.freezing_money(user_id, retail_out)
    if not ice_result:
        resp["success"] = False
        resp["tip"] = "冻结金额失败"
        return resp
    transaction.savepoint_commit(sid)
    resp['success'] = True
    resp['order_id'] = order_id
    resp['tip'] = '提交成功'
    return resp


# 获取我的车辆列表
def get_my_car_list(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    list_data = SUserCar.objects.filter(user_id=user_id)
    list_all = []
    for i in list_data:
        list_all.append(
            {
                'car_number': i.car_number,
                'car_brand': i.car_brand
            }
        )

    resp['list'] = list_all
    return resp


# 添加我的车辆信息
def add_my_car_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    insertone = SUserCar(
        user_id=data.get('user_id'),
        car_number=data.get('car_number'),
        car_brand=data.get('car_brand'),
        car_model=data.get('car_model'),
        create_time=datetime.datetime.now()
    )
    insertone.save()
    resp['success'] = True
    resp['tip'] = '添加成功'
    return resp


# 删除我的车辆信息
def delete_my_car_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    insertone = SUserCar.objects.filter(
        car_number=data.get('car_number')
    )
    insertone.delete()

    resp['success'] = True
    resp['tip'] = '删除成功'
    return resp


# 提交加盟信息
def add_join_info(request, data, resp):
    if not data.get('user_id') or not data.get('name'):
        return Error.REQ_PARAMS_ERROR
    if not data.get('name'):
        resp['success'] = False
        resp['tip'] = '请填写姓名'
        return resp
    if not data.get('tel'):
        resp['success'] = False
        resp['tip'] = '请填写电话'
        return resp
    #     添加信息
    insert = SJoinApply(
        user_id=data.get('user_id'),
        name=data.get('name'),
        tel=data.get('tel'),
        leave_msg=data.get('leave_msg'),
        sub_type=data.get('sub_type'),
        comp_name=data.get('comp_name'),
        email=data.get('email'),
        create_time=datetime.datetime.now(),
        state=0
    )
    insert.save()
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp


# 提交意见反馈
def add_feedback_info(request, data, resp):
    if not data.get('user_id'):
        return Error.REQ_PARAMS_ERROR
    if not data.get('user_tel'):
        resp['success'] = False
        resp['tip'] = '请填写电话'
        return resp
    if not data.get('feedback_content'):
        resp['success'] = False
        resp['tip'] = '请填写意见'
        return resp
    insert = SFeedbackDetail(
        feed_type='opinion',
        user_tel=data.get('user_tel'),
        order_id=data.get('order_id'),
        eq_id=data.get('eq_id'),
        feedback_content=data.get('feedback_content'),
        feedback_img=data.get('feedback_img'),
        user_id=data.get('user_id'),
        create_time=datetime.datetime.now(),
        state='0'
    )
    insert.save()
    resp['success'] = True
    resp['tip'] = '提交成功,感谢你的建议！'
    return resp


# 获取用户信息
def get_user_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id, state='0').first()
    if not user:
        return Error.USER_NOT_FOUND
    uid = str(user.user_id).rjust(6,'0')
    resp['detail'] = {
        'uid': uid,
        'user_no': user.user_no,
        'wx_nickname': user.wx_nickname,
        'wx_headimgurl': user.wx_headimgurl,
        'wx_sex': user.wx_sex,
        'area': user.area,
        'is_wx_login': True if user.is_fetch_wx_info == '1' else False,
        'phone_number': user.phone_number,
        'service_tel': '13503741509',
        'identity': user.identity
    }
    return resp


# 更新用户微信信息
def update_user_wx_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    user = SUserInfo.objects.filter(user_id=user_id).first()
    if not user:
        return Error.USER_NOT_FOUND
    # ata = {'tran_type': 'update_user_wx_info',
    #        'fileUrl': 'https://kfrural-1257596698.cos.ap-shanghai.myqcloud.com/tencent_oss/20250219/7ee1f5fb36c241208adae673ff193d5f.jpeg',
    #        'user_name': '墨染'}

    # user_data = data.get('user_data', {})
    user.wx_nickname = data.get('user_name')
    user.area = data.get('area')
    user.wx_sex = data.get('gender')
    user.wx_language = data.get('language')
    user.wx_city = data.get('city')
    user.wx_province = data.get('province')
    user.wx_country = data.get('country')
    user.wx_headimgurl = data.get('fileUrl')
    user.wx_update_time = datetime.datetime.now()
    user.is_fetch_wx_info = '1'
    user.save()
    resp['success'] = True
    resp['tip'] = '修改成功'
    return resp


