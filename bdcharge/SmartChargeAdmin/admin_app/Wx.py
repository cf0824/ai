# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 17:56
# @Author  : dzy
# @File    : elevator.py
# @Software: PyCharm
import hashlib
import json
import time
from urllib import parse
from django.core.cache import cache
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from wechatpy import parse_message
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import TextReply
from wechatpy.utils import check_signature
import requests
from admin_app import models
from admin_app.am.models import FmUserReservation, FmIndApp
from admin_app.models import SysWxAccessToken
from admin_app.utils import MyLog, server, comm
from admin_app.utils import handle
from admin_app.utils import wx
from admin_app.utils import wx_pay
from admin_app.utils.comm import error_response, return_resp
from admin_app.utils.wx import get_sys_wx_access_token
from admin_cfg.settings import WX_TOKEN, ROOT_API, IS_MUST_FOLLOW, WX_APP_ID, WEB_API, WX_APP_NAME

from django.contrib.sessions.backends.db import SessionStore

from urllib.parse import unquote

log = MyLog.log

# 创建一个SessionStore实例
session = SessionStore()


# 微信支付成功回调通知
def wx_pay_success_notice(request):
    print('header=', request.META)
    print('get=', request.GET)
    print('post=', request.POST)
    print('body=', request.body)

    headers = {}
    headers.update({'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE')})
    headers.update({'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP')})
    headers.update({'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE')})
    headers.update({'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL')})
    wxpay = wx_pay.get_wx_pay()
    result = wxpay.callback(headers=headers, body=request.body)
    if result:
        if result.get('event_type') == 'TRANSACTION.SUCCESS':
            resp = result.get('resource')
            appid = resp.get('appid')
            mchid = resp.get('mchid')
            out_trade_no = resp.get('out_trade_no')
            transaction_id = resp.get('transaction_id')
            trade_type = resp.get('trade_type')
            trade_state = resp.get('trade_state')
            trade_state_desc = resp.get('trade_state_desc')
            bank_type = resp.get('bank_type')
            attach = resp.get('attach')
            success_time = resp.get('success_time')
            payer = resp.get('payer')
            amount = resp.get('amount').get('total')
            # 根据返回参数进行必要的业务处理，处理完后返回200或204
            print('locals=', locals())
            handle.wx_pay_success_handle(out_trade_no, success_time, transaction_id)
            print('支付回调处理成功')
            return HttpResponse('success')
        elif result.get('event_type') == 'REFUND.SUCCESS':
            # 退款成功
            resp = result.get('resource')

            log.info(f"resp={resp}")
            out_refund_no = resp.get('out_refund_no')
            success_time = resp.get('success_time')
            handle.wx_refund_success_handle(out_refund_no)
            print('退款回调处理成功')
            res = {
                "code": "SUCCESS",
                "message": "成功"
            }
            return HttpResponse(json.dumps(res))
        else:
            print('处理失败')
            return HttpResponse('error')
    else:
        print('处理失败')
        return HttpResponse('error')


def wx_check(request):
    return render(request, 'MP_verify_9z382GOcnODPEbq1.txt')


def wx_check1(request):
    return render(request, 'MP_verify_HNQVq1j223OSOfvI.txt')


# 关注页面
def follow(request):
    return render(request, 'follow.html', {'img': f'{ROOT_API}/static/follow.jpg'})


# 现场预约 二维码
def validate_qrcode(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        log.info(f"real_url={real_url}")
        return HttpResponseRedirect(toGrantUrl(real_url))

    timestamp = request.GET.get("timestamp")  # 从请求参数中获取时间戳
    log.info(f"timestamp={timestamp}")
    current_time = int(time.time())  # 获取当前时间戳
    log.info(f"current_time={current_time}")
    default_url = f'{WEB_API}/#/person'
    log.info(f"default_url={default_url}")
    if current_time > int(timestamp):
        return HttpResponse('二维码已失效，请重新操作')
    else:
        return redirect(default_url)


# 扫码核销详情
def wx_scan(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))

    # 判断权限
    # 判断是否具有审核权限
    flag = handle.check_user_admin_auth(user_id, '2')
    if not flag:
        not_auth_url = f'{WEB_API}/#/noaccess'
        return HttpResponseRedirect(not_auth_url)
    appoint_id = request.GET.get('appoint_id')
    if appoint_id:
        p = server.get_process_detail(appoint_id)
        if not p:
            return HttpResponse('no found')
        real_url = f'{WEB_API}/#/writecheck?no=%s' % appoint_id
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


# 预约审核详情
def send_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))

    # 判断权限
    # 判断是否具有审核权限
    flag = handle.check_user_admin_auth(user_id, '1')
    if not flag:
        not_auth_url = f'{WEB_API}/#/noaccess'
        return HttpResponseRedirect(not_auth_url)
    appoint_id = request.GET.get('appoint_id')
    if appoint_id:
        p = server.get_process_detail(appoint_id)
        if not p:
            return HttpResponse('no found')
        real_url = f'{WEB_API}/#/appointcheck?no=%s' % appoint_id
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


# 预约结果通知
def get_send_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))

    appoint_id = request.GET.get('appoint_id')

    if appoint_id:
        p = server.get_process_detail(appoint_id)
        log.info(p)
        if not p:
            return HttpResponse('no found')
        if p['user_id'] != user_id:
            not_auth_url = f'{WEB_API}/#/noaccess'
            return HttpResponseRedirect(not_auth_url)
        real_url = f'{WEB_API}/#/appointrecordinfo?appointId=%s' % appoint_id
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


# 审核退款详情
def return_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))

    # 判断权限
    # 判断是否具有审核权限
    flag = handle.check_user_admin_auth(user_id, '3')
    if not flag:
        not_auth_url = f'{WEB_API}/#/noaccess'
        return HttpResponseRedirect(not_auth_url)
    order_number = request.GET.get('order_number')
    if order_number:
        p = server.order_return__detail(order_number)
        if not p:
            return HttpResponse('no found')
        real_url = f'{WEB_API}/#/refundcheck?no=%s' % order_number
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


def get_return_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))

    order_number = request.GET.get('order_number')
    if order_number:
        p = server.order_return__detail(order_number)
        if not p:
            return HttpResponse('no found')
        if p['user_id'] != user_id:
            not_auth_url = f'{WEB_API}/#/noaccess'
            return HttpResponseRedirect(not_auth_url)
        real_url = f'{WEB_API}/#/refundrecordinfo?no=%s' % order_number
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


def get_pre_app_detail(request):
    user_id = request.session.get('user_id')
    log.info(f"user_id={user_id}")
    if not user_id:
        real_url = request.build_absolute_uri()
        return HttpResponseRedirect(toGrantUrl(real_url))
    appoint_id = request.GET.get('appoint_id')
    log.info(appoint_id)
    if appoint_id:
        p = FmIndApp.objects.filter(ind_no=appoint_id).first()
        log.info(p)
        if not p:
            return HttpResponse('no found')
        # flag = handle.check_user_admin_auth(user_id, '2')
        if p.user_id != user_id:
            not_auth_url = f'{WEB_API}/#/noaccess'
            return HttpResponseRedirect(not_auth_url)
        real_url = f'{WEB_API}/#/peapoinfo?appointId=%s' % appoint_id
        log.info(real_url)
        return HttpResponseRedirect(real_url)
    return HttpResponse('获取信息失败，请重新操作')


def check_code(request):
    real_url = f'{WEB_API}/#/home'
    # request.session.flush()
    user_id = request.session.get('user_id')

    log.info("check_code:[%s]" % request.path)
    log.info("check_code:[%s]" % request.method)
    log.info("check_code:[%s]" % request.GET)
    log.info("check_code:[%s]" % request.session)

    log.info(f'check_code检查是否授权={user_id}')

    log.info("check_code请求检查是否授权path:[%s]" % request.path)

    if user_id:
        have_his = FmUserReservation.objects.filter(user_id=user_id).exists()
        # 有记录直接跳转到历史记录页
        if have_his:
            real_url = f'{WEB_API}/#/appointmentrecord'

    # if user_id:
    #     return HttpResponseRedirect(real_url)

    real_url = parse.quote(real_url, safe='')

    log.info(real_url)
    log.info("check_code跳转真实地址:[%s]" % real_url)
    redirect_uri = f'{ROOT_API}/wx_login'
    log.info("check_code请求授权redirect_uri:[%s]" % redirect_uri)
    wechat_oauth_url = wx.get_wechat_auth_url(real_url, redirect_uri)

    log.info("check_code请求授权path:[%s]" % wechat_oauth_url)
    return HttpResponseRedirect(wechat_oauth_url)


# 去授权
def toGrantUrl(real_url):
    real_url = parse.quote(real_url, safe='')
    redirect_uri = f'{ROOT_API}/wx_login'
    wechat_oauth_url = wx.get_wechat_auth_url(real_url, redirect_uri)
    return wechat_oauth_url


def to_home(request):
    user_id = request.session.get('user_id')
    # area = request.GET.get('area')
    # real_url = f'{API_URL}/#/home?area={area}'
    real_url = f'{WEB_API}/#/home'
    # 没有授权先授权
    if not user_id:
        return HttpResponseRedirect(toGrantUrl(real_url))
    return HttpResponseRedirect(real_url)


# 登录
def wx_login(request):
    # 获取code参数
    code = request.GET.get('code')
    # state = request.GET.get('state') or '123'
    if not code:
        return HttpResponse('网络错误！')
    else:

        log.info("wx_login请求path:[%s]" % request.path)
        log.info("wx_login请求method:[%s]" % request.method)
        log.info("wx_login请求GET:[%s]" % request.GET)
        log.info("wx_login请求SESSION:[%s]" % request.session)

        log.info(f'wx_login授权code={code}')
        # 通过授权码获取access_token和openid
        user_grant = wx.get_wechat_access_token(code)

        if not user_grant:
            return error_response(message="网络错误,API接口无法调用", error_code=233001)

        log.info(f'user_grant={user_grant}')

        access_token = user_grant.get('access_token')
        open_id = user_grant.get('openid')
        if not open_id or not access_token:
            return error_response(message="网络错误", error_code=233002)
        log.info(f'access_token={access_token}')
        log.info(f'open_id={open_id}')

        # 检验授权凭证（access_token）是否有效
        flag = wx.is_check_access_token(access_token, open_id)
        if not flag:
            return error_response(message="网络错误", error_code=233002)

        # 判断用户是否已关注公众号
        if IS_MUST_FOLLOW:
            fw = wx.is_user_subscribed(open_id)
        else:
            fw = True
        if not fw:
            # 如果没有关注公众号，重定向到关注页面
            log.info('未关注,openid=%s' % open_id)
            return HttpResponseRedirect(f'{WEB_API}/#/follow')
        else:

            wx_app_name = WX_APP_NAME
            # 通过公众号获取用户的信息
            wx_user_info = wx.get_wechat_user_info(access_token, open_id)
            union_id = wx_user_info.get('unionid')

            consumer_info = models.IrsServerConsumer.objects.filter(wx_open_id=open_id, wx_gzh=wx_app_name)
            if not consumer_info:
                # 用户未绑定，跳转绑定页面
                # 先查询一次（没查到再用create+索引解决并发问题），减少create触发索引报错导致id不连续的出现频率（减少id浪费）
                try:
                    user = models.IrsServerConsumer.objects.create(
                        wx_open_id=open_id,
                        wx_gzh=wx_app_name,
                        head_imgurl=wx_user_info.get('headimgurl'),
                        nick_name=wx_user_info.get('nickname'),
                        user_sex=wx_user_info.get('sex'),
                        user_address=wx_user_info.get('city'),
                    )
                except IntegrityError:
                    # 新用户第一次没查到，但同一用户若同时请求两次会触发两次create导致索引报错，一次执行create，另一次执行下边第二次查询
                    user = models.IrsServerConsumer.objects.filter(wx_open_id=open_id).first()
                    # 解决没有增加union_id之前遗留的数据问题，后续不会出现这种清空
                    if not user:
                        user = models.IrsServerConsumer.objects.filter(wx_open_id=open_id).first()
                        user.wx_open_id = open_id
                        user.save()
            else:
                models.IrsServerConsumer.objects.filter(wx_open_id=open_id).update(
                    head_imgurl=wx_user_info.get('headimgurl'),
                    nick_name=wx_user_info.get('nickname'),
                    user_sex=wx_user_info.get('sex'),
                    user_address=wx_user_info.get('city'),
                )
            # 保存用户信息到数据库
            user = models.IrsServerConsumer.objects.filter(wx_open_id=open_id).first()
            if not user.nick_name and not user.head_imgurl:
                user.nick_name = f'用户{handle.create_invite_code(user.id, 6)}'
                user.head_imgurl = 'https://mmbiz.qpic.cn/mmbiz' \
                                   '/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'
            if not user.wx_open_id:
                user.wx_open_id = open_id
            if not user.union_id and union_id:
                user.union_id = union_id
                log.info(f'默认用户名：{user.nick_name}')

            user.save()

            user_id = user.id
            state = request.GET.get('state')

            request.session['user_id'] = user_id
            # request.session.save()
            log.info(f"wx_login 缓存SESSION信息={request.session['user_id']}")
            session_key = request.session.session_key
            log.info(f'wx_login 缓存SESSION信息session_key={session_key}')

            # session暂时测试不了先用params代替

            log.info(f'state={state}')
            state = unquote(state)
            if '?' not in state:
                state += '?grant=1'
            else:
                state += '&grant=1'

            # state += '?&session_key=%s' % session_key

            if not state:
                return HttpResponse('网络错误！')
            log.info(f'wx_login跳转url地址={state}')

            return HttpResponseRedirect(state)


# 刷新token
def get_wx_access_token(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({
            'code': -1,
            'msg': 'Method Error'
        }))
    resp = {}
    at = SysWxAccessToken.objects.filter(app_id=WX_APP_ID).first()
    if at:
        resp['access_token'] = at.access_token
        resp['expire_in'] = at.expire_in
    return HttpResponse(json.dumps(resp, cls=comm.MyJSONEncoder))


def _handle_event(msg):
    print('event=', msg.event)
    print('from=', msg.source)

    if msg.event == 'subscribe':
        print('关注事件')
        handle.update_wx_user_info(msg.source)
        reply_text = '感谢您关注xxxx公众号！'
        reply = TextReply(content=reply_text, message=msg)
        xml = reply.render()
        return HttpResponse(xml)
        # return wx_follow_handle(msg)
    elif msg.event == 'unsubscribe':
        print('取消关注事件')
        handle.quit_follow_handle(msg.source)

    return None


def _handle_text(msg):
    print('content=', msg.content)
    # reply_text = f'收到：{msg.content}'
    print('from=', msg.source)
    if msg.content == '绑定小程序':
        handle.update_wx_user_info(msg.source)
        reply_text = '已绑定！'
        reply = TextReply(content=reply_text, message=msg)
        xml = reply.render()
        return HttpResponse(xml)
    # reply = TextReply(content=reply_text, message=msg)
    # xml = reply.render()
    # return HttpResponse(xml)

    return None


def wx_event(request):
    print('get=', request.GET)
    print('body=', request.body)

    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')
    try:
        check_signature(WX_TOKEN, signature, timestamp, nonce)
        print('验证成功')
    except InvalidSignatureException:
        print('验证失败')
        return HttpResponse('验证失败')

    xml = request.body
    msg = parse_message(xml)
    if not msg:
        return HttpResponse(echostr)

    print('msg=', msg)
    print('msg_type=', msg.type)

    resp = None

    if msg.type == 'event':
        resp = _handle_event(msg)
    elif msg.type == 'text':
        resp = _handle_text(msg)

    if not resp:
        if echostr:
            print('回复', echostr)
            return HttpResponse(echostr)
        print('回复success')
        return HttpResponse('success')
    return HttpResponse(resp)
