"""
充电相关接口
"""
import asyncio
import decimal
import json
import time

from app.utils.comm import api_handle
from app.utils import Error
from app.models import *
from app.utils.tools import haversine
from django.db import transaction
from django.db.models import F
import datetime
from django.core.paginator import Paginator
import random
from app.utils.eq_api import tieta_handle2
from app.utils.get_seq import Get_SeqNo
from app.utils.handle import charge_open, charge_stop
from django.db import connection
from ..utils import MyLog
from app.tcp_socket import TCPHandler
# from app.shell.handle_cmd2 import req_term
from app.shell import req_term
from app.utils.handle_order import HandleOrder
from app.command.tools.ApiTool import ApiTool

log = MyLog.log
apitool = ApiTool(log)

# 系统通用处理
def sys_handle(request):
    log.info(f'request:{request}')
    gb = globals()
    return api_handle(request, gb)


def test(request, data, resp):
    print('test2')
    log.info('test2')
    return resp

#-------------------------------2024.12.16--------------------------------

# 创建订单
@transaction.atomic()
def create_order(request, data, resp):
    # 参数
    user_id = data.get('user_id')
    eq_id = data.get('eq_id') # 充电桩id
    charge_type = data.get('charge_type')  # 充电类型
    order_source = data.get('order_source')
    pay_way = data.get('pay_way')
    charge_electric = data.get('charge_electric', 0)  # 定电量充电
    charge_money = data.get('charge_money', 0)  # 定金额充电金额
    charge_time = data.get('charge_time', 0)  # 定时充电时长
    # charge_time = '10'
    # charge_money = 0.1
    SocketNumber = data.get('SocketNumber')  # 插座号
    eq_id = int(eq_id)
    # 1）查询充电桩状态
    try:
        eq_info = SEqInfo.objects.get(eq_id=eq_id)
        port_info = SEqPort.objects.get(eq_id=eq_id, eq_port=SocketNumber)
    except:
        return Error.CONTENT_NOT_FOUND

    user_info = SUserInfo.objects.filter(user_id=user_id, state='0')
    if user_info.exists():
        account_or = float(user_info[0].account)  # 提取账户金额
    else:
        resp['success'] = False
        resp['tip'] = '请输入正确的账户'
        return resp

    # if not user_info[0].phone_number or not user_info[0].wx_nickname:
    #     resp['success'] = False
    #     resp['tip'] = '请完善个人信息，以便确认您的身份'
    #     return resp

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

    max_order_count = user_info[0].max_order_count
    order_counts = SOrderInfo.objects.filter(user_id=user_id, state='1').count()
    if order_counts >= max_order_count:
        resp['success'] = False
        resp['tip'] = f'同时进行的订单有{max_order_count}，已达到最大数量!'
        return resp

    # 检查用户账户余额
    account_info = ViewUserAccountOk.objects.filter(user_id=user_id)[0]
    ok_money = account_info.ok_money
    gift_money = account_info.gift_money
    pay_source = 'account'
    if account_or < 0 or ok_money < 0:
        # pay_source = 'giftmoney'
        # if gift_money <= 0:
        resp['success'] = False
        resp['tip'] = '账户欠费，无法使用充电业务！'
        return resp


    if charge_type == 'money' and float(charge_money) > ok_money:
        if float(charge_money) > (ok_money + gift_money):
            resp['success'] = False
            resp['tip'] = '账户可用余额不足'
            return resp



    terminal_address = eq_info.terminal_address  # 充电桩地址
    log.info(f'eq_info: {eq_info}')
    conn_state = eq_info.conn_state
    log.info(f'conn_state: {conn_state}')
    eq_state = eq_info.eq_state
    log.info(f'eq_state: {eq_state}')
    state = eq_info.state
    log.info(f'state: {state}')
    port_state = port_info.state
    port_use_state = port_info.use_state
    port_conn_state = port_info.conn_state
    if state != '1':
        return Error.TERMINAL_ERROR
    if conn_state != '1':
        return Error.TERMINAL_ERROR
    if eq_state == '-1':
        return Error.TERMINAL_ERROR
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
    if charge_type == 'elec' and float(charge_electric) <= 0:
        resp["success"] = False
        resp["tip"] = "充电量需大于0"
        return resp
    elif charge_type == 'money' and float(charge_money) <= 0:
        resp["success"] = False
        resp["tip"] = "金额需大于0"
        return resp
    elif charge_type == 'time' and float(charge_time) <= 0:
        resp["success"] = False
        resp["tip"] = "时间需大于0"
        return resp

    # 计算传给硬件的参数，每种充电方式不同
    # 1）获取电价

    OrderNumber_ = Get_SeqNo("CHARGE_ORDER")[-10:]
    if int(OrderNumber_) >= 4294967295:
        resp["success"] = False
        resp["tip"] = "订单号长度超限"
        return resp
    OrderNumber = hex(int(OrderNumber_)).lstrip('0x').zfill(8).upper()
    eq_id = eq_info.eq_id
    # electrovalence = eq_info.electrovalence  # 电价

    charge_type = data.get('charge_type')
    # DurationOrAmount = data.get('DurationOrAmount')  # 充电时长或金额
    DurationOrAmount_ = 600
    if charge_type == 'auto':  # 充满自停，实际传给硬件的是 按时间
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'time':  # 按时间
        hex_DurationOrAmount_ = hex(int(charge_time)).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'elec':  # 按电量，也转成按时间，给硬件一个固定值，把电量存起来
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'money':  # 按金额，也转成按时间，给硬件一个固定值，把金额存起来
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    else:
        resp["success"] = False
        resp["tip"] = "充电类型错误"
        return resp
    log.info(f'传给充电桩的时间参数：{DurationOrAmount_h}')
    json_data = {
        'number': '0420',
        'terminal_address': terminal_address,
        'Special_data': {
            'SocketNumber': SocketNumber,
            'OrderNumber': OrderNumber,
            'electrovalence': '0050',  # 这个电价没用，写死
            'type': '01',  # 00：金额，01：时间
            'DurationOrAmount': DurationOrAmount_h
        }
    }
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
    if not eq_fee_type or not eq_fee_no:
        resp['success'] = False
        resp['tip'] = '该设备没有计费规则，暂不可用，可联系管理员解决！'
        return resp

    # 冻结金额
    # ice_money = 0
    # if charge_type == 'elec' or charge_type == 'auto' or charge_type == 'time':
    #     ice_money = 1    # todo 这个有需要的话可以弄成在管理台配置
    # elif charge_type == 'money' and pay_way == 'account':
    #     ice_money = float(charge_money)

    handleorder = HandleOrder(log)
    # 冻结金额  2025.06.12 更新，取消冻结金额
    # ice_result = handleorder.freezing_money(user_id, ice_money, pay_source)
    # if not ice_result:
    #     resp["success"] = False
    #     resp["tip"] = "冻结金额失败"
    #     return resp

    SOrderUseMoney.objects.create(
        order_id=OrderNumber,
        create_time=datetime.datetime.now()
    )

    # create order
    SOrderInfo.objects.create(
        site_id=site_id,
        eq_id=eq_id,
        eq_port=SocketNumber,
        term_address=terminal_address,
        charge_type=charge_type,
        pay_way=pay_way,
        charge_time=charge_time,
        charge_electric=charge_electric,
        charge_money=charge_money,
        fee_type=eq_fee_type,
        fee_no=eq_fee_no,
        user_id=user_id,
        order_id=OrderNumber,
        state='0',
        error_times=0,
        create_time=datetime.datetime.now(),
        use_electric=0,
        use_money=0,
        use_time=0,
        order_source=order_source
    )

    # 创建费用详细信息
    handleorder.create_fee_detail(site_id, OrderNumber, eq_fee_type, eq_fee_no)
    if pay_way == 'account':
        log.info(f'余额支付，直接开启')
        try:
            req_term(json_data)
        except Exception as e:
            log.error(f'给终端发送开启失败：{e}', exc_info=True)

    # select status from order where orderid = 111
    # for _ in range(10):
    #     order_info = SEqInfo.objects.get(order_id=OrderNumber)
    #     order_state = order_info.state
    #     if order_state == '1':
    #         resp['info'] = '提交成功'
    resp['order_id'] = OrderNumber
    resp['info'] = '提交成功'
    resp['success'] = True
    return resp

# 创建订单
@transaction.atomic()
def create_order_dev(request, data, resp):
    # 参数
    user_id = data.get('user_id')
    eq_id = data.get('eq_id') # 充电桩id
    charge_type = data.get('charge_type')  # 充电类型
    pay_way = data.get('pay_way')
    charge_electric = data.get('charge_electric', 0)  # 定电量充电
    charge_money = data.get('charge_money', 0)  # 定金额充电金额
    charge_time = data.get('charge_time', 0)  # 定时充电时长
    SocketNumber = data.get('SocketNumber')  # 插座号
    eq_id = int(eq_id)
    # 1）查询充电桩状态
    try:
        eq_info = SEqInfo.objects.get(eq_id=eq_id)
        port_info = SEqPort.objects.get(eq_id=eq_id, eq_port=SocketNumber)
    except:
        return Error.CONTENT_NOT_FOUND

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
    if charge_type == 'elec' and float(charge_electric) <= 0:
        resp["success"] = False
        resp["tip"] = "充电量需大于0"
        return resp
    elif charge_type == 'money' and float(charge_money) <= 0:
        resp["success"] = False
        resp["tip"] = "金额需大于0"
        return resp
    elif charge_type == 'time' and float(charge_time) <= 0:
        resp["success"] = False
        resp["tip"] = "时间需大于0"
        return resp

    # 计算传给硬件的参数，每种充电方式不同
    # 1）获取电价

    OrderNumber_ = Get_SeqNo("CHARGE_ORDER")[-10:]
    if int(OrderNumber_) >= 4294967295:
        resp["success"] = False
        resp["tip"] = "订单号长度超限"
        return resp
    OrderNumber = hex(int(OrderNumber_)).lstrip('0x').zfill(8)
    eq_id = eq_info.eq_id
    # electrovalence = eq_info.electrovalence  # 电价

    charge_type = data.get('charge_type')
    # DurationOrAmount = data.get('DurationOrAmount')  # 充电时长或金额
    DurationOrAmount_ = 600
    if charge_type == 'auto':  # 充满自停，实际传给硬件的是 按时间
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'time':  # 按时间
        hex_DurationOrAmount_ = hex(charge_time).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'elec':  # 按电量，也转成按时间，给硬件一个固定值，把电量存起来
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    elif charge_type == 'money':  # 按金额，也转成按时间，给硬件一个固定值，把金额存起来
        # 转成十六进制
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
    else:
        resp["success"] = False
        resp["tip"] = "充电类型错误"
        return resp
    log.info(f'传给充电桩的时间参数：{DurationOrAmount_h}')
    json_data = {
        'number': '0420',
        'terminal_address': terminal_address,
        'Special_data': {
            'SocketNumber': SocketNumber,
            'OrderNumber': OrderNumber,
            'electrovalence': '0050',  # 这个电价没用，写死
            'type': '01',  # 00：金额，01：时间
            'DurationOrAmount': DurationOrAmount_h
        }
    }
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
    site_id = eq_info.site_id
    # create order
    SOrderInfo.objects.create(
        eq_id=eq_id,
        eq_port=SocketNumber,
        term_address=terminal_address,
        charge_type=charge_type,
        charge_time=charge_time,
        charge_electric=charge_electric,
        charge_money=charge_money,
        fee_type=eq_fee_type,
        fee_no=eq_fee_no,
        user_id=user_id,
        order_id=OrderNumber,
        state='0',
        error_times=0,
        create_time=datetime.datetime.now()
    )
    handleorder = HandleOrder(log)
    # 创建费用详细信息
    handleorder.create_fee_detail(site_id,OrderNumber, eq_fee_type, eq_fee_no)
    if pay_way == 'account':
        req_term(json_data)

    # select status from order where orderid = 111
    # for _ in range(10):
    #     order_info = SEqInfo.objects.get(order_id=OrderNumber)
    #     order_state = order_info.state
    #     if order_state == '1':
    #         resp['info'] = '提交成功'
    resp['order_id'] = OrderNumber
    resp['info'] = '提交成功'
    resp['success'] = True
    return resp


# 停止充电
def stop_charge(request, data, resp):
    log.info(f'关闭订单')
    # 参数
    user_id_ = data.get('user_id')
    eq_id = data.get('eq_id')  # 充电桩id
    # terminal_address = data['terminal_address']  # 充电桩地址
    SocketNumber = data.get('SocketNumber')
    OrderNumber = data.get('OrderNumber')


    # 1）查询订单状态
    try:
        dt = datetime.datetime.now() - datetime.timedelta(days=30)
        order_info = SOrderInfo.objects.get(order_id=OrderNumber, create_time__gte=dt)
    except:
        return Error.CONTENT_NOT_FOUND
    log.info(f'order_info: {order_info}')
    order_state = order_info.state
    log.info(f'order_state: {order_state}')
    if order_info:
        terminal_address = order_info.term_address
        user_id = order_info.user_id
        charge_time = order_info.charge_time
        begin_time = order_info.begin_time
        charge_type = order_info.charge_type
    else:
        return Error.CONTENT_NOT_FOUND

    if user_id_ != user_id:
        return Error.PERMISSION_DENIED

    if order_state != '1':
        return Error.ORDER_STATUS_ERROR

    if not all([eq_id, user_id, SocketNumber, OrderNumber]):
        return Error.REQ_PARAMS_ERROR



    json_data = {
        'number': '0420',
        'terminal_address': terminal_address,
        'Special_data': {
            'SocketNumber': SocketNumber,
            'OrderNumber': OrderNumber,
            'electrovalence': '0050',
            'type': '01',  # 00：金额，01：时间
            'DurationOrAmount': '0000'
        }
    }

    # up order
    # SOrderInfo.objects.create(
    #     eq_id=eq_id,
    #     charge_type=charge_type,
    #     charge_time=charge_time,
    #     charge_electric=charge_electric,
    #     charge_money=charge_money,
    #     user_id=user_id,
    #     order_id=OrderNumber,
    #     state='0',
    #     error_times=0,
    #     create_time=datetime.datetime.now()
    # )

    req_term(json_data)
    # select status from order where orderid = 111
    # for _ in range(10):
    #     order_info = SEqInfo.objects.get(order_id=OrderNumber)
    #     order_state = order_info.state
    #     if order_state == '1':
    #         resp['info'] = '提交成功'

    resp['info'] = '提交成功'
    resp['success'] = True
    return resp


# 查询订单功率
def get_order_power(request, data, resp):
    order_num = data.get('order_num')
    if not order_num:
        return Error.REQ_PARAMS_ERROR
    dt = datetime.datetime.now() - datetime.timedelta(days=365)
    power_info = SOrderPower.objects.filter(order_id=order_num, create_time__gte=dt)
    if not power_info:
        resp['success'] = False
        resp['tip'] = '订单功率信息缺失'
        return resp

    power_list = []
    time_list = []
    for item in power_info:
        power_time = item.power_time.strftime('%H:%M')
        power = item.power
        power_list.append(power)
        time_list.append(power_time)


    series = [
        {
            "name": "功率",
            "data": power_list
        }
    ]
    resp['categories'] = time_list
    resp['series'] = series

    return resp

# 查询设备当前功率
def get_eq_power(request, data, resp):
    eq_id = data.get('eq_id')
    eq_port = data.get('eq_port')
    if not all([eq_id, eq_port]):
        return Error.REQ_PARAMS_ERROR
    port_info = SEqPort.objects.filter(eq_id=eq_id, eq_port=eq_port)[0]
    power = port_info.power
    power_time = port_info.power_time
    resp['power'] = power
    resp['power_time'] = power_time
    resp['success'] = True
    return resp


# 充电前详情页面
def charge_detail(request, data, resp):
    eq_id = data.get('eq_id')
    user_id = data.get('user_id')
    if not eq_id or not user_id:
        return Error.REQ_PARAMS_ERROR
    info_e = SEqInfo.objects.filter(eq_id=eq_id)
    if not info_e.exists():
        resp['success'] = False
        resp['tip'] = '充电桩编号不存在'
        return resp
    eq = info_e.first()
    conn_state = eq.conn_state
    eq_state = eq.eq_state
    terminal_address = eq.terminal_address
    site_id = info_e[0].site_id
    info_s = SSiteInfo.objects.filter(site_id=site_id)
    site_name = info_s[0].site_name

    # 插座信息
    port_list = []
    state = None
    state_text = None
    ports = SEqPort.objects.filter(terminal_address=terminal_address)
    for port in ports:
        log.info(f'使用状态：{port.use_state}')
        if conn_state == '1':
            if port.state == '-1':
                state = '-1'
                state_text = '异常'
            elif port.state == '1':
                if port.use_state == '0':
                    state = '0'
                    state_text = '空闲'
                elif port.use_state == '1':
                    state = '1'
                    state_text = '占用'
        elif conn_state == '0':
            state = '-1'
            state_text = '离线'
        port_info = {
            'id': port.id,
            'port_no': port.eq_port,
            'state': state,
            'state_text': state_text
        }
        port_list.append(port_info)

    # 充电类型信息
    charge_type_list = [
        {
            'text': '定金额充电',
            'value': 'money'
        },
        {
            'text': '定时间充电',
            'value': 'time'
        },
        {
            'text': '充满自停',
            'value': 'auto'
        },
        {
            'text': '定电量充电',
            'value': 'elec'
        }
    ]
    # 充电类型详情
    paymoneylist = []  # 金额详情
    timelist = [] # 时间详情
    eleclist = [] # 电量详情
    charge_type_detail = SChargeArgs.objects.filter(site_id=13).order_by('id')
    for charge_type in charge_type_detail:
        if charge_type.arg_type == 'time':
            time_ = {
                'text': f'{charge_type.value}分钟',
                'value': charge_type.value
            }
            timelist.append(time_)
        elif charge_type.arg_type == 'money':
            money_ = {
                'text': f'{charge_type.value}元',
                'value': charge_type.value
            }
            paymoneylist.append(money_)
        elif charge_type.arg_type == 'elec':
            elec_ = {
                'text': f'{charge_type.value}度',
                'value': charge_type.value
            }
            eleclist.append(elec_)

    payWays = [
        {'text': '在线支付', 'value': 'online'},
        {'text': '账户余额', 'value': 'account'}
    ]

    info_account = SUserInfo.objects.filter(user_id=user_id)
    if info_account.exists():
        accounta = float(info_account[0].account)
        account = format(accounta, '.2f')
    resp['site_name'] = site_name
    # resp['port_total'] = port_total
    # resp['list_po'] = list_po
    resp['port_list'] = port_list  # 插座信息
    resp['charge_type_list'] = charge_type_list  # 充电类型
    resp['paymoneylist'] = paymoneylist
    resp['timelist'] = timelist
    resp['eleclist'] = eleclist
    resp['payWays'] = payWays
    resp['account'] = account
    resp['success'] = True
    return resp


# 获取收费标准
def get_fee_standard(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    # 获取设备相关信息
    eq_info = SEqInfo.objects.filter(eq_id=eq_id)
    if not eq_info:
        return Error.CONTENT_NOT_FOUND
    site_id = eq_info[0].site_id  # 终端地址
    fee_type = eq_info[0].fee_type  # 收费类型
    fee_no = eq_info[0].fee_no  # 收费标准编号
    # 获取收费标准详情
    fee_type_list = []
    fee_detail_list = []
    if fee_type == '1':  # 按时间
        fee_type_list = fee_type_list + ['时段', '基础电价', '服务费']
        fee_detail = SFeeStandard1.objects.filter(site_id=site_id, fee_no=fee_no)
        for item in fee_detail:
            detail = {
                'times': f'{item.begin_time}-{item.end_time}',
                'base_price': item.electric_price,
                'service_price': item.service_fee
            }
            fee_detail_list.append(detail)
    elif fee_type == '2': # 按梯度
        fee_type_list = fee_type_list + ['梯度(度)', '基础电价', '服务费']
        fee_detail = SFeeStandard2.objects.filter(site_id=site_id, fee_no=fee_no)
        for item in fee_detail:
            detail = {
                'times': f'{item.electric_down}-{item.electric_up}',
                'base_price': item.electric_price,
                'service_price': item.service_fee
            }
            fee_detail_list.append(detail)

    resp['fee_type'] = fee_type
    resp['fee_type_list'] = fee_type_list
    resp['fee_detail_list'] = fee_detail_list
    return resp


#-------------------------------2024.12.16--------------------------------

# 获取电站列表。
def get_site_list(request, data, resp):
    page = data.get('page', 1)
    page_size = data.get('page_size', 5)
    site_name = data.get('site_name')
    if not page or not page_size:
        return Error.REQ_PARAMS_ERROR
    list_s = SSiteInfo.objects.filter(state='1')
    if site_name:
        list_s = SSiteInfo.objects.filter(site_name__contains=site_name)
    list_info = []
    for i in list_s:
        list_info.append(
            {
                'site_id': i.site_id,
                'site_gps': i.site_gps
            }
        )
    j = len(list_info)
    k = 0
    list_site = []
    while k < j:
        gps = list_info[k]['site_gps']
        site_gpslong = data.get('site_gpslong', '0')
        site_gpslati = data.get('site_gpslati', '0')
        leng = 0
        if site_gpslati == '' or site_gpslong == '':
            length = ''
        elif gps == None:
            length = ''
        else:
            gps = list_info[k]['site_gps'].split(',')
            gpslong = float(gps[0])
            gpslati = float(gps[1])
            site_gpslong = float(data.get('site_gpslong', '0'))
            site_gpslati = float(data.get('site_gpslati', '0'))
            a = haversine(gpslong, gpslati, site_gpslong, site_gpslati)
            leng = round(a, 1)
            if leng > 1000:
                length = str(round(a / 1000, 1)) + ' km'
            else:
                length = str(round(a, 1)) + ' m'
        eqs = SEqInfo.objects.filter(site_id=list_s[k].site_id, state='1')
        all_count = eqs.count()
        eqs = eqs.filter(conn_state='1', eq_state='0')
        usable_count = eqs.count()
        list_site.append(
            {
                'site_name': list_s[k].site_name,
                'site_desc': list_s[k].site_desc,
                'state': list_s[k].state,
                'site_id': list_s[k].site_id,
                'site_gps': list_s[k].site_gps,
                'site_address': list_s[k].site_address,
                'length': length,
                'leng': leng,
                'all_count': all_count,
                'usable_count': usable_count
            }
        )
        k = k + 1
    list_site = sorted(list_site, key=lambda x: x['leng'])
    p = Paginator(list_site, page_size)
    pagex = p.page(page)
    list_page = pagex.object_list
    resp['total'] = j
    resp['list_site'] = list_page
    return resp


# 获取电站信息
def get_site_info(request, data, resp):
    site_id = data.get('site_id')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    try:
        info_site = SSiteInfo.objects.get(site_id=site_id)
    except:
        return Error.CONTENT_NOT_FOUND

    detail_site = {}
    detail_site['site_id'] = info_site.site_id
    detail_site['site_name'] = info_site.site_name
    detail_site['state'] = info_site.state
    resp['detail_site'] = detail_site
    return resp


# # 根据名称获取电站信息
# def get_site_infoname(request, data, resp):
#     site_name = data.get('site_name')
#     if not site_name:
#         return Error.REQ_PARAMS_ERROR
#     info_site = SSiteInfo.objects.filter(site_name__contains=site_name)
#     if info_site.exists():
#         list_info = []
#         for i in info_site:
#             list_info.append(
#                 {
#                     'site_id': i.site_id,
#                     'site_gps': i.site_gps
#                 }
#             )
#         j = len(list_info)
#         k = 0
#         list_siteinfo = []
#         while k < j:
#             gps = list_info[k]['site_gps']
#             site_gpslong = data.get('site_gpslong', '0')
#             site_gpslati = data.get('site_gpslati', '0')
#             if site_gpslati == '' or site_gpslong == '':
#                 length = ''
#             elif gps == None:
#                 length = ''
#             else:
#                 gps = list_info[k]['site_gps'].split(',')
#                 gpslong = float(gps[0])
#                 gpslati = float(gps[1])
#                 site_gpslong = float(data.get('site_gpslong', '0'))
#                 site_gpslati = float(data.get('site_gpslati', '0'))
#                 a = haversine(gpslong, gpslati, site_gpslong, site_gpslati)
#                 leng = round(a, 1)
#                 if leng > 1000:
#                     length = str(round(a / 1000, 1)) + ' km'
#                 else:
#                     length = str(round(a, 1)) + ' m'
#             eqs = SEqInfo.objects.filter(site_id=info_site[k].site_id, state='1')
#             all_count = eqs.count()
#             eqs = eqs.filter(conn_state='1', eq_state='0')
#             usable_count = eqs.count()
#             list_siteinfo.append(
#                 {
#                     'site_name': info_site[k].site_name,
#                     'site_desc': info_site[k].site_desc,
#                     'state': info_site[k].state,
#                     'site_id': info_site[k].site_id,
#                     'site_gps': info_site[k].site_gps,
#                     'length': length,
#                     'all_count': all_count,
#                     'usable_count': usable_count
#                 }
#             )
#             k = k + 1
#         resp['success'] = True
#         resp['list_siteinfo'] = list_siteinfo
#         return resp
#     else:
#         resp['success'] = False
#         resp['tip'] = '未查询到相关结果'
#         return resp


# 根据电站名称获取设备列表
def get_eq_listname(request, data, resp):
    site_id = data.get('site_id')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    info_sit = SSiteInfo.objects.filter(site_id=site_id)
    site_address = info_sit[0].site_address
    site_name = info_sit[0].site_name
    list_e = SEqInfo.objects.filter(site_id=site_id, state='1')
    all_count = list_e.count()
    usable_count = list_e.filter(conn_state='1', eq_state='0').count()
    list_eq = []
    for i in list_e:
        if i.conn_state == '0':
            state = '离线'
            usable = False
        elif i.eq_state == '1':
            state = '使用中'
            usable = False
        else:
            state = '空闲'
            usable = True
        list_eq.append(
            {
                'eq_id': i.eq_id,
                'state': state,
                'usable': usable
            }
        )
    resp['site_desc'] = site_address
    resp['site_name'] = site_name
    resp['all_count'] = all_count
    resp['usable_count'] = usable_count
    resp['list_eq'] = list_eq
    return resp


# 获取设备列表
def get_eq_list(request, data, resp):
    site_id = data.get('site_id')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    list_e = SEqInfo.objects.filter(site_id=site_id, state='1')
    list_eq = []
    for i in list_e:
        list_eq.append(
            {
                'eq_id': i.eq_id,
                'state': i.state,
                'eq_state': i.eq_state
            }
        )
    resp['list_eq'] = list_eq
    return resp


# 获取设备信息
def get_eq_info(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    try:
        info_eq = SEqInfo.objects.get(eq_id=eq_id)
    except:
        return Error.CONTENT_NOT_FOUND
    detail_eq = {}
    detail_eq['eq_id'] = info_eq.eq_id
    detail_eq['rated_power'] = info_eq.rated_power
    detail_eq['state'] = info_eq.state
    detail_eq['eq_state'] = info_eq.eq_state
    detail_eq['soft_version'] = info_eq.soft_version
    detail_eq['agree_version'] = info_eq.agree_version
    resp['detail_eq'] = detail_eq
    return resp


# 充电下单
@transaction.atomic
def charge_post(request, data, resp):
    # save_id = transaction.savepoint()  # 设置保存点
    eq_id = data.get('eq_id')
    user_id = data.get('user_id')
    charge_type = data.get('charge_type')  # 充电类型
    charge_electric = data.get('charge_electric', 0)  # 定电量充电
    charge_money = data.get('charge_money', 0)  # 定金额充电金额
    charge_time = data.get('charge_time', 0)  # 定时充电时长
    if charge_money == "":
        charge_money = 0
    if charge_electric == "":
        charge_electric = 0
    if charge_time == "":
        charge_time = 0
    # 分钟转换为秒
    charge_time = float(charge_time) * 60
    if not all([eq_id, user_id, charge_type]):
        return Error.REQ_PARAMS_ERROR
    if charge_type == 'elec' and float(charge_electric) <= 0:
        resp["success"] = False
        resp["tip"] = "充电量需大于0"
        return resp
    elif charge_type == 'money' and float(charge_money) <= 0:
        resp["success"] = False
        resp["tip"] = "金额需大于0"
        return resp
    elif charge_type == 'time' and float(charge_time) <= 0:
        resp["success"] = False
        resp["tip"] = "时间需大于0"
        return resp

    eq = SEqInfo.objects.filter(eq_id=eq_id).first()
    if eq.state == '0':
        resp['success'] = False
        resp['tip'] = '设备未运营'
        return resp

    site = SSiteInfo.objects.filter(site_id=eq.site_id).first()
    if site.state == '0':
        resp['success'] = False
        resp['tip'] = '站点未运营'
        return resp

    if eq.eq_state == '1':
        resp['success'] = False
        resp['tip'] = '设备已被占用'
        return resp

    info_user = SUserInfo.objects.filter(user_id=user_id)
    if info_user.exists():
        account_or = float(info_user[0].account)  # 提取账户金额
    else:
        resp['success'] = False
        resp['tip'] = '请输入正确的账户'
        return resp

    ok_money = ViewUserAccountOk.objects.filter(user_id=user_id).first().ok_money
    if account_or == 0 or ok_money <= 0:
        resp['success'] = False
        resp['tip'] = '账户余额不足'
        return resp

    if charge_type == 'money' and float(charge_money) > account_or:
        resp['success'] = False
        resp['tip'] = '账户余额不足'
        return resp
    # count = ViewUserAccountOk.objects.filter(user_id=user_id, ok_money__gte=float(charge_money))
    # if count == []:
    #     resp['success'] = False
    #     resp['tip'] = '余额不足'
    #     return resp
    # order_id = int(round(time.time()*1000))
    order_id = Get_SeqNo("CHARGE_ORDER")
    # ok_money = ViewUserAccountOk.objects.filter(user_id=user_id).first().ok_money

    # eq_code = SEqInfo.objects.filter(eq_id=eq_id).first().eq_code

    # th = tieta_handle2.TietaHandle(SCmdDetail)
    # if charge_type == 'elec' and float(charge_electric)>0 :
    #     res = th.eq_charge_open(eq_code, account_money=float(ok_money),set_elect=float(charge_electric))
    # elif charge_type == 'money' and float(charge_money)>0 :
    #     res = th.eq_charge_open(eq_code, account_money=float(ok_money),set_time=float(charge_money))
    # elif charge_type == 'time' and float(charge_time)>0:
    #     res = th.eq_charge_open(eq_code, account_money=float(ok_money),set_money=float(charge_time))
    # else:
    #     res = th.eq_charge_open(eq_code, account_money=float(ok_money))
    num = SOrderInfo.objects.filter(eq_id=eq_id, state__in=['0', '1']).count()
    if num != 0:
        resp['success'] = False
        resp['tip'] = '设备有关联订单未结算，不允许再下单'
        return resp

    # 乐观锁，防止同一台设备并发下单情况
    res = SEqInfo.objects.filter(eq_id=eq_id, state='1', eq_state='0').update(eq_state='1')
    if res == 0:
        resp['success'] = False
        resp['tip'] = '充电口非空闲状态，请重新选择'
        return resp

    # 创建订单
    SOrderInfo.objects.create(
        eq_id=eq_id,
        charge_type=charge_type,
        charge_time=charge_time,
        charge_electric=charge_electric,
        charge_money=charge_money,
        user_id=user_id,
        order_id=order_id,
        state='0',
        error_times=0,
        create_time=datetime.datetime.now()
    )
    # 启动设备
    charge_open(eq_id, order_id)
    # resp['success'] = res
    # if not res:
    #     # transaction.savepoint_rollback(save_id)
    #     resp['msg'] = False
    #     resp['tip'] = '启动失败'
    #     return resp
    # transaction.savepoint_commit(save_id)
    resp['order_id'] = order_id
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp


# 获取订单列表
def get_order_list(request, data, resp):
    log.info(f'获取订单列表')
    user_id = data.get('user_id')
    order_state = data.get('order_state', 0)
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    if order_state == 0:
        list_o = SOrderInfo.objects.filter(user_id=user_id).order_by('-order_id')
    else:
        list_o = SOrderInfo.objects.filter(user_id=user_id, state=order_state).order_by('-order_id')
        log.info(f'list_o: {list_o}')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        list_o = list_o.filter(create_time__gte=begin_date, create_time__lt=end_date)
    list_order = []
    log.info(f'标记1')
    for i in list_o:
        # 查询站点名称
        eq_id = i.eq_id
        eq = SEqInfo.objects.filter(eq_id=eq_id).first()
        site_id = eq.site_id if eq else ''
        log.info(f'标记1-1')
        if site_id:
            site = SSiteInfo.objects.filter(site_id=site_id).first()
            site_name = site.site_name if site else ''
        else:
            site_name = ''
        log.info(f'标记1-2')
        # 状态转换
        if i.state == '1':
            state = '进行中'
        elif i.state == '0':
            state = '订单创建中'
        elif i.state == '2':
            state = '已结束'
        else:
            state = '订单超时关闭'
        # 充电模式转换
        if i.charge_type == 'auto':
            detail_order = '自动充电'
        elif i.charge_type == 'elec':
            detail_order = '定电量充电'
        elif i.charge_type == 'money':
            detail_order = '定金额充电'
        else:
            detail_order = '定时充电'
        list_order.append(
            {
                'site_name': site_name,
                'eq_id': i.eq_id,
                'eq_port': i.eq_port,
                'charge_type': detail_order,
                'use_money': '0' if not i.use_money else i.use_money,
                'user_id': i.user_id,
                'order_id': i.order_id,
                'state': state
            }
        )
    log.info(f'标记2')
    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp


# 获取订单详情
def get_order_info(request, data, resp):
    order_id = data.get('order_id')
    if not order_id:
        return Error.REQ_PARAMS_ERROR
    # 判断order_id类型
    if len(order_id) != 8 and order_id[0:6] == 'WF_SUB':
        sub_order_info = SOrderNumMap.objects.filter(sub_order=order_id)
        order_id = sub_order_info[0].charge_order



    info_order = SOrderInfo.objects.filter(order_id=order_id).first()
    if not info_order:
        return Error.CONTENT_NOT_FOUND
    eq = SEqInfo.objects.filter(eq_id=info_order.eq_id).first()
    if not eq:
        return Error.CONTENT_NOT_FOUND
    site_id = eq.site_id
    site = SSiteInfo.objects.filter(site_id=site_id).first()
    if not site:
        return Error.CONTENT_NOT_FOUND
    site_name = site.site_name
    # try:
    #     info_order = SOrderInfo.objects.get(order_id=order_id)
    #     site_id = SEqInfo.objects.get(eq_id=info_order.eq_id).site_id
    #     site_name = SSiteInfo.objects.get(site_id=site_id).site_name
    # except:
    #     return Error.USER_NOT_FOUND




    detail_order = {}
    state = info_order.state
    # state = '1'
    detail_order['state'] = state



    import datetime

    def format_timedelta(delta):
        total_seconds = int(delta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分")
        if seconds > 0 or not parts:  # 确保至少显示一个单位（如0秒）
            parts.append(f"{seconds}秒")

        return ''.join(parts)

    def format_minute(delta):
        total_seconds = delta * 60
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分")
        if seconds > 0 or not parts:  # 确保至少显示一个单位（如0秒）
            parts.append(f"{seconds}秒")

        return ''.join(parts)


    charge_type = info_order.charge_type
    detail_order['charge_type'] = charge_type
    if charge_type == 'auto':
        detail_order['charge_type_text'] = '充满自停'
    elif charge_type == 'elec':
        detail_order['charge_type_text'] = '定电量充电'
        detail_order['charge_electric'] = info_order.charge_electric
    elif charge_type == 'money':
        detail_order['charge_type_text'] = '定金额充电'
        detail_order['charge_money'] = info_order.charge_money
    else:
        detail_order['charge_type_text'] = '定时充电'
        detail_order['charge_time'] = str(round(info_order.charge_time / 60, 1))


    detail_order['charge_time'] = info_order.charge_time
    detail_order['charge_electric'] = info_order.charge_electric
    detail_order['charge_money'] = info_order.charge_money

    pay_way = info_order.pay_way
    if pay_way == 'account':
        detail_order['pay_way'] = '账户余额'  # 支付方式
    if pay_way == 'online':
        detail_order['pay_way'] = '在线支付'

    detail_order['order_id'] = info_order.order_id
    detail_order['eq_id'] = info_order.eq_id
    detail_order['eq_port'] = info_order.eq_port
    detail_order['site_name'] = site_name
    detail_order['create_time'] = info_order.create_time
    detail_order['begin_time'] = info_order.begin_time
    detail_order['end_time'] = '-' if not info_order.end_time else info_order.end_time
    detail_order['use_electric'] = info_order.use_electric  # 获取使用电量
    if state == '1':
        use_time = datetime.datetime.now() - info_order.begin_time

        detail_order['use_time'] = int(use_time.total_seconds() / 60)
        # 获取金额
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        fee_type = info_order.fee_type
        fee_no = info_order.fee_no
        use_money_all = decimal.Decimal(0.00)
        if fee_type == '1':
            order_fee_detail = SOrderFee1.objects.filter(order_id=order_id, fee_no=fee_no, create_time__gte=dt)
            for item in order_fee_detail:
                use_money_all = use_money_all + item.use_money
        elif fee_type == '2':
            order_fee_detail = SOrderFee2.objects.filter(order_id=order_id, fee_no=fee_no, create_time__gte=dt)
            for item in order_fee_detail:
                use_money_all = use_money_all + item.use_money
        detail_order['use_money'] = use_money_all
    else:
        detail_order['use_time'] = info_order.use_time
        detail_order['use_money'] = info_order.use_money

    def format_time(_time):
        _hour = int(_time / 3600)
        _minute = int(_time / 60) % 60
        # _second = _time % 60
        res = ''
        # if _second:
        #     res = f'{_second}秒'
        if _minute:
            res = f'{_minute}分钟' + res
        if _hour:
            res = f'{_hour}小时' + res
        if not res:
            res = '-'
        return res

    detail_order['end_type'] = info_order.end_type
    detail_order['end_reason'] = info_order.end_reason
    detail_order['remark'] = info_order.remark

    return_money = info_order.return_money
    refund_state = info_order.refund_state
    detail_order['return_money'] = return_money
    detail_order['refund_state'] = refund_state

    resp['detail_order'] = detail_order

    # 获取开票情况
    sid = SInvoiceDetail.objects.filter(order_id=order_id).first()
    resp['invoice_state'] = '-1'
    if sid:
        if sid.state == '0':
            resp['invoice_state'] = '0'
        elif sid.state == '1':
            resp['invoice_state'] = '1'

    return resp





@transaction.atomic
# 结束充电
def charge_end(request, data, resp):
    save_end = transaction.savepoint()
    usera_id = data.get('user_id')
    order_id = data.get('order_id')
    if not order_id:
        return Error.REQ_PARAMS_ERROR
    info_order = SOrderInfo.objects.filter(order_id=order_id)  # 查找订单信息
    # log.info(f'订单信息：{info_order}')
    # log.info(f'dir(订单信息)：{dir(info_order)}')
    # log.info(f'订单信息.__dict__：{info_order.__dict__}')
    # log.info(f'vars(订单信息)：{vars(info_order)}')
    # log.info(f'hasattr(订单信息)：{hasattr(info_order, "abc")}')
    # log.info(f'hasattr(订单信息)：{hasattr(info_order, "order_by")}')
    # log.info(f'订单信息[0]：{info_order[0]}')
    # log.info(f'dir(订单信息[0])：{dir(info_order[0])}')
    log.info(f'订单信息[0].__dict__：{info_order[0].__dict__}')
    log.info(f'vars(订单信息[0])：{vars(info_order[0])}')
    if info_order.exists():
        eq_id = info_order[0].eq_id
        user_id = info_order[0].user_id
        charge_time = info_order[0].charge_time
        begin_time = info_order[0].begin_time
        charge_type = info_order[0].charge_type
    else:
        return Error.CONTENT_NOT_FOUND
    if usera_id != user_id:
        return Error.PERMISSION_DENIED
    eq_code = SEqInfo.objects.filter(eq_id=eq_id).first().eq_code

    th = tieta_handle2.TietaHandle(SCmdDetail)
    res = th.eq_charge_open(eq_code, False)
    resp['success'] = str(res)
    if not res:
        transaction.savepoint_rollback(save_end)
        resp['success'] = False
        resp['tip'] = '关闭失败'
        return resp
    # 更新
    jud = SEqInfo.objects.filter(eq_id=eq_id, eq_state='1').update(eq_state='0')
    SOrderInfo.objects.filter(order_id=order_id,user_id=usera_id).update(state=1,end_time=datetime.datetime.now())
    # 关闭设备
    charge_stop(eq_id, order_id)
    if jud == 0:
        resp['success'] = False
        resp['tip'] = '充电已自动结束'
        return resp
    transaction.savepoint_commit(save_end)
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp


# 获取端口状态
# todo
def get_eq_port(request, data, resp):
    eq_port = data.get('eq_port')
    if not eq_port:
        return Error.REQ_PARAMS_ERROR
    try:
        # list_port = SEqInfo.objects.get(eq_port=eq_port) # 貌似数据表有错误
        # 2024.10.18 update by marverdol
        list_port = SEqPort.objects.get(eq_port=eq_port)
        log.info(f'list_port: {list_port}')
    except:
        return Error.USER_NOT_FOUND
    detail_port = {}
    detail_port['eq_id'] = list_port.eq_id
    detail_port['eq_port'] = list_port.eq_port
    detail_port['state'] = list_port.state
    resp['detail_eq'] = detail_port
    return resp

# 获取插孔列表（根据终端号）
def get_eq_port_list(request, data, resp):
    term_address = data.get('term_address')
    if not term_address:
        return Error.REQ_PARAMS_ERROR
    # 查询设备状态
    try:
        eq_info = SEqInfo.objects.get(terminal_address=term_address)
    except:
        return Error.TERMINAL_NOT_FOUND
    log.info(f'eq_info: {eq_info}')
    conn_state = eq_info.conn_state
    log.info(f'conn_state: {conn_state}')
    # eq_state = eq_info.eq_state
    # log.info(f'eq_state: {eq_state}')

    if conn_state != '1':
        return Error.TERMINAL_ERROR

    detail_port = SEqPort.objects.filter(terminal_address=term_address)
    ports = {}
    ports['term_address'] = term_address
    ports['counts'] = detail_port.count()

    for item in detail_port:
        ports[item.eq_port] = item.state

    resp['ports_detail'] = ports
    return resp

# 订单投诉
def order_complaint(request, data, resp):
    order_id = data.get('order_id')
    if not order_id:
        return Error.REQ_PARAMS_ERROR
    SFeedbackDetail.objects.create(
        feed_type='complain',
        order_id=data.get('order_id'),
        eq_id=data.get('eq_id'),
        eq_port=data.get('eq_port'),
        user_tel=data.get('user_tel'),
        feedback_content=data.get('feedback_content'),
        feedback_img=data.get('feedback_img'),
        user_id=data.get('user_id'),
        create_time=datetime.datetime.now(),
        state='0'
    )
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp


# 获取地图标点
def get_map_dot(request, data, resp):
    list_m = SSiteInfo.objects.all()
    list_map = []
    for i in list_m:
        try:
            site_gps_longitude, site_gps_dimension = i.site_gps.split(',')
        except:
            continue
        list_map.append(
            {
                'site_name': i.site_name,
                'site_id': i.site_id,
                'site_address': i.site_address,
                'site_gps_longitude': site_gps_longitude,
                'site_gps_dimension': site_gps_dimension
            }
        )
    resp['list_map'] = list_map
    return resp


# 通过电站id获取相关信息
def get_site_info_id(request, data, resp):
    site_id = data.get('site_id')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    site_info = SSiteInfo.objects.filter(site_id=site_id)
    if site_info.exists():
        site_info = site_info.first()
        gps = str(site_info.site_gps).split(',')
        site_longitude = float(gps[0])
        site_latitude = float(gps[1])
        resp['site_longitude'] = site_longitude
        resp['site_latitude'] = site_latitude
        if latitude and longitude:

            distance = haversine(float(longitude), float(latitude), site_longitude, site_latitude)

            if distance > 1000:
                resp['distance'] = str("%.1f" % (distance / 1000)) + "km"
            else:
                resp['distance'] = str("%.1f" % distance) + "m"
        else:
            resp['distance'] = ''

        eq_sum = SEqInfo.objects.filter(site_id=site_id, state='1').count()
        eq_free = SEqInfo.objects.filter(site_id=site_id, state='1', conn_state='1', eq_state='0').count()
        resp['site_id'] = site_id
        resp['site_name'] = site_info.site_name
        resp['site_address'] = site_info.site_address
        resp['eq_sum'] = eq_sum
        resp['eq_free'] = eq_free
        resp['success'] = True
    else:
        resp['success'] = False
        resp['tip'] = "没有此充电站"
    return resp


# 通过电站名称获取相关信息
# todo 充电桩状态
def get_site_info_name(request, data, resp):
    site_name = data.get('site_name')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    if not site_name:
        return Error.REQ_PARAMS_ERROR
    site_info = SSiteInfo.objects.filter(site_name=site_name)
    if site_info.exists():
        site_info = site_info.first()
        gps = str(site_info.site_gps).split(',')
        site_longitude = float(gps[0])
        site_latitude = float(gps[1])
        resp['site_longitude'] = site_longitude
        resp['site_latitude'] = site_latitude
        if latitude and longitude:

            distance = haversine(float(longitude), float(latitude), site_longitude, site_latitude)
            if distance > 1000:
                resp['distance'] = str("%.1f" % (distance / 1000)) + "km"
            else:
                resp['distance'] = str("%.1f" % distance) + "m"
        else:
            resp['distance'] = ''
        eq_sum = SEqInfo.objects.filter(site_id=site_info.site_id, state='1').count()
        eq_free = SEqInfo.objects.filter(site_id=site_info.site_id, state='1', conn_state='1', eq_state='0').count()
        resp['site_id'] = site_info.site_id
        resp['site_name'] = site_info.site_name
        resp['site_address'] = site_info.site_address
        resp['eq_sum'] = eq_sum
        resp['eq_free'] = eq_free
        resp['success'] = True
    else:
        resp['success'] = False
        resp['tip'] = "没有此充电站"
    return resp


# 获取计价规则
def get_price_rule(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    eq = SEqInfo.objects.filter(eq_id=eq_id).first()
    if not eq:
        return Error.CONTENT_NOT_FOUND
    if not eq.mode_id:
        mode_id = 1
    else:
        mode_id = eq.mode_id
    objs = SPriceModeDetail.objects.filter(mode_id=mode_id)
    detail = []
    for item in objs:
        detail.append(
            f"{item.begin_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}   {str(item.price).rstrip('0')}元/度")
    resp['detail'] = detail
    return resp


# 获取电站计价规则
def get_site_price_rule(request, data, resp):
    site_id = data.get('site_id')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    site = SSiteInfo.objects.filter(site_id=site_id).first()
    if not site:
        return Error.CONTENT_NOT_FOUND
    if not site.mode_id:
        mode_id = 1
    else:
        mode_id = site.mode_id
    objs = SPriceModeDetail.objects.filter(mode_id=mode_id)
    detail = []
    for item in objs:
        detail.append(
            f"{item.begin_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}   {str(item.price).rstrip('0')}元/度")
    resp['detail'] = detail
    return resp


# 获取进行中订单
def get_ing_order(request, data, resp):
    user_id = data.get('user_id')
    eq_id = data.get('eq_id')
    # if not eq_id:
    #     return Error.REQ_PARAMS_ERROR
    orders = SOrderInfo.objects.filter(user_id=user_id, state='1')
    count = orders.count()
    if count == 0:
        resp['to'] = ''
    elif count == 1:
        resp['to'] = 'detail'
        resp['order_id'] = orders.first().order_id
        if eq_id and orders.first().eq_id == eq_id:
            resp['need_ack'] = False
        else:
            resp['need_ack'] = True
            resp['tip'] = '您有一笔订单进行中，是否跳转到订单详情页？'
    else:
        resp['to'] = 'list'
        resp['tip'] = '您有多笔订单进行中，是否跳转到订单列表页？'
    # detail = []
    # for item in orders:
    #     detail.append(item.order_id)
    # resp['detail'] = detail
    # resp['count'] = len(detail)
    return resp


# 获取公告列表
def get_notice_list(request, data, resp):
    page = data.get('page', 1)
    size = data.get('size', 10)
    notices = SNoticeInfo.objects.filter(state='1').order_by('-id')
    log.info(f'notices:{notices}')
    p = Paginator(notices, size)
    notice_list = []
    for notice in p.page(page):
        notice_list.append({
            'notice_id': notice.id,
            'notice_name': notice.notice_name,
            'notice_desc': notice.notice_content,
            'look_num': notice.look_num,
            'notice_remark': notice.notice_remark,
            'create_time': notice.create_time
        })
    resp['num_pages'] = p.num_pages
    resp['list_len'] = p.count
    resp['notice_list'] = notice_list
    return resp


# 获取公告详情
def get_notice_detail(request, data, resp):
    notice_id = data.get('notice_id')
    if not notice_id:
        return Error.REQ_PARAMS_ERROR
    notice = SNoticeInfo.objects.filter(id=notice_id).first()
    if not notice:
        return Error.CONTENT_NOT_FOUND
    detail = {
        'notice_id': notice.id,
        'notice_name': notice.notice_name,
        'notice_desc': notice.notice_content,
        # 'notice_content': notice.notice_content,
        'look_num': notice.look_num,
        'create_time': notice.create_time
    }
    SNoticeInfo.objects.filter(id=notice_id).update(look_num=F('look_num') + 1)
    resp['detail'] = detail
    return resp


# 获取报修类型
def get_repair_type(request, data, resp):
    detail = []
    objs = SRepairKv.objects.filter(state='1')
    for obj in objs:
        detail.append({
            'name': obj.repair_key,
            'label': obj.repair_label
        })
    resp['detail'] = detail
    return resp


# 报修上报
@transaction.atomic()
def repair_post(request, data, resp):
    user_id = data.get('user_id')
    eq_id = data.get('eq_id')
    repair_type = data.get('repair_type')
    other_text = data.get('other_text')
    repair_tel = data.get('repair_tel')
    repair_img = data.get('repair_img')
    if repair_img:
        repair_img = str(repair_img)
    if not all([user_id, eq_id, repair_type]):
        return Error.REQ_PARAMS_ERROR
    res = SRepairInfo.objects.create(
        repair_type=repair_type,
        other_type_text=other_text,
        repair_tel=repair_tel,
        repair_img=repair_img,
        eq_id=eq_id,
        user_id=user_id,
        create_time=datetime.datetime.now(),
        state='0'
    )
    # 自动创建工单任务
    repair = SRepairKv.objects.filter(repair_key=repair_type).first()
    if repair and repair.auto_task == '1':
        eq = SEqInfo.objects.filter(eq_id=eq_id).first()
        if eq:
            SDevopsTaskInfo.objects.create(
                task_name=repair.repair_label,
                task_type='1',
                task_desc=repair.repair_label,
                repair_id=res.id,
                site_id=eq.site_id,
                eq_id=eq.eq_id,
                feedback_tel=repair_tel,
                create_type='sys',
                create_time=datetime.datetime.now(),
                state='0'
            )
    resp['success'] = True
    resp['tip'] = '上报成功'
    return resp


# 模糊查询设备id
def get_like_search_eq(request, data, resp):
    search = data.get('search')
    detail = []
    if not search or len(search) < 3:
        resp['detail'] = []
        return resp
    eqs = SEqInfo.objects.filter(eq_id__contains=search, state='1')
    log.info(f'eqs:{eqs}')
    for eq in eqs:
        detail.append(eq.eq_id)
    resp['detail'] = detail
    return resp

# 模糊查询设备id
def get_like_search_eq_by_eq_id(request, data, resp):
    search = data.get('search')
    page = data.get('page', 1)
    detail = []
    if not search or len(search) < 3:
        resp['detail'] = []
        return resp
    eqs = SEqInfo.objects.filter(eq_id__contains=search, state='1')
    log.info(f'eqs:{eqs}')
    for eq in eqs:
        site_id = eq.site_id
        site_info = SSiteInfo.objects.filter(site_id=site_id)
        site_name = site_info[0].site_name
        site_address = site_info[0].site_address
        eq_id = eq.eq_id
        port_info = SEqPort.objects.filter(eq_id=eq_id)
        port_count = port_info.count()
        data = {
            'eq_id': eq.eq_id,
            'site_id': eq.site_id,
            'site_name': site_name,
            'site_address': site_address,
            'port_count': port_count
        }
        detail.append(data)

    paginator = Paginator(detail, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(detail)
    resp['detail'] = list_page_data
    return resp


# 获取功率曲线
# def get_power_line(request, data, resp):
#     order_id = data.get('order_id')
#     if not order_id:
#         return Error.REQ_PARAMS_ERROR
#     cursor = connection.cursor()
#
#     def get_data_kv(order_id, data_k):
#         _data_kv = {}
#         sql = "select attr_value,DATE_FORMAT(create_time,'%%m/%%d %%H:%%i') from s_eq_attr_data where order_id=%s and attr_key=%s order by id"
#         cursor.execute(sql, (order_id, data_k))
#         rows = cursor.fetchall()
#         for v, time in rows:
#             _data_kv[time] = v
#         return _data_kv
#
#     def merge_set_list(*arglist):
#         _tmp = []
#         for item in arglist:
#             _tmp += item
#         return list(set(_tmp))
#
#     v_data_kv = get_data_kv(order_id, '_charge_v')
#     a_data_kv = get_data_kv(order_id, '_charge_a')
#     labels = merge_set_list(v_data_kv.keys(), a_data_kv.keys())
#     labels.sort()
#
#     p_data = []
#     for label in labels:
#         v = float(v_data_kv.get(label, 0))
#         a = float(a_data_kv.get(label, 0))
#         p_data.append(round(v * a, 2))
#     labels = [item.split(' ')[1] for item in labels]
#
#     # series = [
#     #     {
#     #         "name": "我的收益",
#     #         "data": my_list
#     #     },
#     #     {
#     #         "name": "总收益",
#     #         "data": total_list
#     #     }
#     # ]
#     # resp['categories'] = time_list
#     # resp['series'] = series
#
#
#     resp['detail'] = {
#         'categories': labels,
#         'series': [
#             {
#                 'name': '功率',
#                 'data': p_data
#             }
#         ]
#     }
#     return resp


# 申请开票
def apply_invoice(request, data, resp):
    sub_type = data.get('sub_type')
    sub_name = data.get('sub_name')
    sub_taxes_no = data.get('sub_taxes_no')
    email = data.get('email')
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    if not all([sub_type, sub_name, order_id, user_id]):
        return Error.REQ_PARAMS_ERROR
    SInvoiceDetail.objects.create(
        sub_type=sub_type,
        sub_name=sub_name,
        sub_taxes_no=sub_taxes_no,
        email=email,
        order_id=order_id,
        user_id=user_id,
        create_time=datetime.datetime.now(),
        state='0'
    )
    resp['success'] = True
    resp['tip'] = '申请成功'
    return resp


async def get_system_info(request, data, resp):
    print(f'system info: {resp}')
    info = await asyncio.sleep(10)
    return info
    # resp['custom_tel'] = '0374-8370056'
    # print(f'system info: {resp}')
    # return resp

