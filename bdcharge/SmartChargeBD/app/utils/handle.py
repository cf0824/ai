"""
处理订单相关操作
"""
import datetime
import json
import os
import random
import time
import decimal

from app.models import *
from django.db import transaction
from django.db.models import F
from app.utils import MyLog
from SmartChargeBD.settings import BASE_DIR
from app.utils import get_seq
from app.utils import wx_pay
from SmartChargeBD.settings import WX_XCX_APP_ID
from SmartChargeBD.settings import ROOT_API


file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
# print(file_path)
# print(file_name)

log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

# log = MyLog.MyLog(__file__, 'handle.log', BASE_DIR).logger
# log.info('handle start!')


# eq_id转dev_id
def eqid2devid(eqid):
    eq = SEqInfo.objects.filter(eq_id=eqid).first()
    if not eq:
        return ''
    return eq.eq_code


# dev_id转eq_id
def devid2eqid(devid):
    eq = SEqInfo.objects.filter(eq_code=devid).first()
    if not eq:
        return 0
    return eq.eq_id


# 账户变更
def account_change(user_id, change_money, change_type, order_id=None, remark=''):
    """
    :param user_id: 用户id
    :param change_money: 变更金额（正数 float）
    :param change_type: 变更类型 in-收入（如充值） out-支出（如扣款）
    :param order_id: 订单号
    :param remark: 备注
    :return: 成功返回：True 失败返回：False
    """
    if change_type not in ['in', 'out']:
        raise Exception('参数有误')
    # 保证变更金额为正浮点数
    change_money = float(change_money)
    change_money = abs(change_money)
    with transaction.atomic():
        # 扣除余额
        if change_type == 'out':
            tmp_change_money = - change_money
        else:
            tmp_change_money = change_money
        res = SUserInfo.objects.filter(user_id=user_id, state='0').update(account=F('account') + tmp_change_money)
        res2 = ViewUserAccountOk.objects.filter(user_id=user_id).update(
            real_money=(F('real_money') + tmp_change_money), ok_money=(F('ok_money') + tmp_change_money)
        )
        if not (res and res2):
            return False
        # 增加交易记录
        real_money = ViewUserAccountOk.objects.filter(user_id=user_id)[0].real_money
        SAccountDetail.objects.create(
            change_type=change_type,
            change_money=change_money,
            now_money=real_money,
            order_id=order_id,
            user_id=user_id,
            remark=remark,
            create_time=datetime.datetime.now()
        )
    return True


# 获取给设备的用户可用余额
def get_user_ok_money_for_eq(devId):
    eq_id = devid2eqid(devId)
    order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
    if not order:
        return 0

    ## 如果用户选择充电模式是定金额充电 返回订单金额
    # if order.charge_type == 'money':
    #     return order.charge_money

    # 返回用户账户可用余额 (不包括当前订单已产生金额，硬件自己计算)
    account = ViewUserAccountOk.objects.filter(user_id=order.user_id).first()
    if not account:
        return 0
    # 加上当前订单冻结金额
    now_order_ice = SAccountIce.objects.filter(user_id=order.user_id, link_type='order', link_id=order.order_id).first()
    if now_order_ice and now_order_ice.ice_amount:
        return account.ok_money + now_order_ice.ice_amount
    return account.ok_money


# 开启充电(异步控制硬件)
def charge_open(eq_id, order_id=None):
    opera = SOperaDetail.objects.create(
        opera_type='charge_open',
        eq_id=eq_id,
        order_id=order_id,
        create_class='0',  # todo 这是什么
        create_time=datetime.datetime.now(),
        state='0'
    )
    return opera


# 停止充电（异步控制硬件）
def charge_stop(eq_id, order_id=None):
    opera = SOperaDetail.objects.create(
        opera_type='charge_stop',
        eq_id=eq_id,
        order_id=order_id,
        create_class='0',
        create_time=datetime.datetime.now(),
        state='0'
    )
    return opera


# # 订单创建
# def order_create(order_id):
#     pass


def _str2float(_str):
    if type(_str) == float:
        return _str
    try:
        _float = float(_str)
    except:
        _float = 0
    return _float


# todo 更新订单参数
def update_order_attr(dev_id, charge_attr_kv):
    log.info(f'dev_id={dev_id}')
    eq_id = devid2eqid(dev_id)
    log.info(f'eq_id={eq_id}')
    # order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
    order = SOrderInfo.objects.filter(eq_id=eq_id).order_by('-create_time').first()
    if not order:
        return
    # 订单已经结算过 不重新结算（也不在更新）
    if order.state != '1':
        return
    charge_state = charge_attr_kv.get('_charge_state')
    use_money = charge_attr_kv.get('_charge_money')
    use_electric = charge_attr_kv.get('_charge_elect')
    begin_timestamp = charge_attr_kv.get('_charge_begin_time')
    end_timestamp = charge_attr_kv.get('_charge_end_time')
    end_type = charge_attr_kv.get('_charge_end_type')

    # 20220816新增 若计算出电量异常不更新数据，连续10次则结束订单
    eq = SEqInfo.objects.filter(eq_id=order.eq_id).first()
    if eq:
        rated_power = float(eq.rated_power)
        use_time = int(end_timestamp) - int(begin_timestamp)
        # 预期最大使用电量=使用时长（小时）*额定功率（kW）+1
        expect_use_elect = round((use_time / 3600) * (rated_power / 1000) + 1, 4)
        if float(use_electric) > expect_use_elect:
            row = SOrderInfo.objects.filter(order_id=order.order_id, error_times__lt=9).update(error_times=F('error_times') + 1)
            # 达到十次连续
            if not row:
                log.info(f'order_id:{order.order_id},expect_use_elect:{expect_use_elect},连续10次上报电量数据异常，即将结束订单')
                order_finish(order.order_id)
        else:
            # 正常，将连续次数清零
            SOrderInfo.objects.filter(order_id=order.order_id).update(error_times=0)

    # 更新已使用金额
    if use_money:
        order.use_money = _str2float(use_money)

    # 更新已使用电量
    if use_electric:
        order.use_electric = _str2float(use_electric)

    # 更新已使用时间
    if begin_timestamp:
        tmp_begin_timestamp = _str2float(begin_timestamp)
        now_timestamp = time.time()
        tmp_use_time = now_timestamp - tmp_begin_timestamp
        if tmp_use_time < 0:
            tmp_use_time = 0
        order.use_time = tmp_use_time

    # 更新开始充电时间
    if begin_timestamp:
        tmp_begin_timestamp = _str2float(begin_timestamp)
        begin_dt = datetime.datetime.fromtimestamp(tmp_begin_timestamp)
        order.begin_time = begin_dt

    # 有结束时间 且 充电状态为结束
    if end_timestamp and charge_state == '1':
        tmp_end_timestamp = _str2float(end_timestamp)
        end_dt = datetime.datetime.fromtimestamp(tmp_end_timestamp)
        order.end_time = end_dt

    # 充电结束且结束类型不为空
    if charge_state == '1' and end_type is not None:
        order.end_type = end_type

    # 更新更新时间
    order.update_time = datetime.datetime.now()

    # 订单保存
    order.save()

    # 更新冻结金额
    if use_money:
        update_account_ice_money(order.user_id, _str2float(use_money), order.order_id, 'order')

    # 充电状态为结束 且 订单状态为充电中 -> 执行订单结算流程
    if charge_state == '1' and order.state == '1':
        # order_finish_by_dev_id(dev_id)
        order_finish(order.order_id)


# 充电更新账户冻结金额_通过dev_id
# def charge_update_account_ice_money_by_dev_id(dev_id, ice_money):
#     eq_id = devid2eqid(dev_id)
#     order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
#     if not order:
#         return
#     update_account_ice_money(order.user_id, ice_money, order.order_id, 'order')


# 更新账户冻结金额
def update_account_ice_money(user_id, ice_money, link_id, link_type='order'):
    ice = SAccountIce.objects.filter(user_id=user_id, link_type=link_type, link_id=link_id, state='1').first()
    if not ice:
        ice = SAccountIce.objects.create(
            ice_amount=ice_money,
            link_id=link_id,
            link_type=link_type,
            user_id=user_id,
            create_time=datetime.datetime.now(),
            update_time=datetime.datetime.now(),
            state='1'
        )
    else:
        ice.ice_amount = ice_money
        ice.update_time = datetime.datetime.now()
        ice.save()


# 订单结算_通过dev_id
# def order_finish_by_dev_id(dev_id):
#     eq_id = devid2eqid(dev_id)
#     order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
#     if not order:
#         return
#     order_finish(order.order_id)


# 订单结算
def order_finish(order_id):
    order = SOrderInfo.objects.filter(order_id=order_id).first()
    ice = SAccountIce.objects.filter(user_id=order.user_id, link_type='order', link_id=order.order_id,
                                     state='1').first()
    # 设置事务保存点
    save_id = transaction.savepoint()
    if not ice:
        log.info(f'订单结算未找到冻结账户:{order_id}')
    else:
        # 解除冻结金额并扣除实际消费金额
        ice.state = '0'
        ice.update_time = datetime.datetime.now()
        ice.save()
    # 更新账户
    use_money = order.use_money if order.use_money else 0
    success = account_change(order.user_id, use_money, 'out', order.order_id, '订单结算扣款')
    if not success:
        # 回滚事务
        transaction.savepoint_rollback(save_id)
        log.error('订单结算异常：账户变更未成功', exc_info=True)
        return
    # 更新订单
    order.state = '2'
    order.save()

    # 将设备充电状态解除占用
    SEqInfo.objects.filter(eq_id=order.eq_id, eq_state='1').update(eq_state='0')

    charge_end_notice(order_id)

    # 提交事务
    transaction.savepoint_commit(save_id)


# 解析充电参数
def unpack_charge_attrs(charge_attrs):
    res = {}
    try:
        tmp_list = charge_attrs.split(';')
        res['_charge_state'] = tmp_list[0]
        res['_charge_begin_time'] = tmp_list[1]
        res['_charge_end_time'] = tmp_list[2]
        res['_charge_v'] = tmp_list[3]
        res['_charge_a'] = tmp_list[4]
        res['_charge_elect'] = tmp_list[5]
        res['_charge_money'] = tmp_list[6]
        res['_charge_end_type'] = tmp_list[7]
    except:
        log.error('充电参数解析失败', exc_info=True)
    return res


# 添加命令
def add_cmd(eq_code, cmd, seq_no=None):
    eq_id = devid2eqid(eq_code)
    # 取命令类型
    try:
        _data = json.loads(cmd)
        cmd_type = str(_data.get('msgType'))
    except:
        cmd_type = None
    SCmdDetail.objects.create(
        cmd_type=cmd_type,
        cmd=cmd,
        eq_id=eq_id,
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


# 添加设备属性数据
def add_eq_attr_data(dev_id, attr_key, attr_value):
    # log.info(f'_add_eq_attr_data dev_id={dev_id},attr_key={attr_key},attr_value={attr_value}')
    eq_id = devid2eqid(dev_id)
    order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
    if order:
        order_id = order.order_id
    else:
        order_id = None
    SEqAttrData.objects.create(
        eq_id=eq_id,
        attr_key=attr_key,
        attr_value=attr_value,
        order_id=order_id,
        create_time=datetime.datetime.now()
    )


# 获取计费策略
def get_price_mode(devId):  # todo 根据设备id获取其计费策略id
    eq = SEqInfo.objects.filter(eq_code=devId).first()
    if not eq or not eq.mode_id:
        mode_id = 1
    else:
        mode_id = eq.mode_id
    mds = SPriceModeDetail.objects.filter(mode_id=mode_id)  # 获取计费策略详情
    if not mds.exists():
        return None
    detail = []
    for item in mds:  # 时间段1是多少钱、时间段2是多少钱。。。
        detail.append({
            'price': item.price,
            'time': f"{item.begin_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}"
        })
    return detail

# 处理微信支付成功，电卡充值
@transaction.atomic
def handle_wx_card_recharge_success(out_trade_no, success_time, transaction_id):
    # time.sleep(10)
    success_time_dt = datetime.datetime.strptime(success_time, "%Y-%m-%dT%H:%M:%S+08:00")
    order = SWxTranCardDetail.objects.filter(order_id=out_trade_no).first()
    log.info(f'handle_wx_card_recharge_success -->out_trade_no：{out_trade_no}')
    if not order:
        log.info(f'电卡充值失败，未找到原充值记录 -->out_trade_no：{out_trade_no}')
        return False
    if order.state != '1':
        log.info(f'电卡充值失败，原充值记录已成功 -->out_trade_no：{out_trade_no}')
        return False

    log.info(f'order -->order.id:{order.id},order.state：{order.state}, order.user_id:{order.user_id}')
    order.finish_time = success_time_dt
    order.transaction_id = transaction_id
    order.state = '2'
    order.save()

    card_num = order.card_num
    card_sn = order.card_sn
    card_tel = order.card_tel
    user_id = order.user_id
    change_money = order.change_money
    # 在电卡充值记录里加上记录
    SCardRechargeDetail.objects.create(
        card_num=card_num,
        card_sn=card_sn,
        card_tel=card_tel,
        recharge_type='online',
        user_id=user_id,
        transaction_id=transaction_id,
        recharge_money=order.change_money,
        remark='在线充值',
        create_time=datetime.datetime.now()
    )
    # 增加卡余额
    # 保证变更金额为正浮点数
    change_money = float(change_money)
    change_money = abs(change_money)

    if card_num and card_sn:
        res = SCardsInfo.objects.filter(card_num=card_num, card_sn=card_sn).update(
            money=F('money') + change_money
        )
    elif card_num:
        res = SCardsInfo.objects.filter(card_num=card_num).update(
            money=F('money') + change_money
        )
    elif card_sn:
        res = SCardsInfo.objects.filter(card_sn=card_sn).update(
            money=F('money') + change_money
        )
    else:
        res = None
    if not res:
        log.info(f'增加卡余额失败，未找到记录 -->card_num：{card_num}， card_sn：{card_sn}')
        return False

# 处理微信支付成功
@transaction.atomic
def handle_wx_recharge_success(out_trade_no, success_time, transaction_id):
    # time.sleep(10)
    success_time_dt = datetime.datetime.strptime(success_time, "%Y-%m-%dT%H:%M:%S+08:00")
    order = SWxTranDetail.objects.filter(order_id=out_trade_no).first()
    if order and order.state == '1':
        order.finish_time = success_time_dt
        order.transaction_id = transaction_id
        order.state = '2'
        order.save()
        account_change(order.user_id, order.change_money, 'in', order.order_id, '微信充值')

        # # todo 测试期间自动退款
        # refund_order_id = get_seq.Get_SeqNo("PAY_ORDER")
        # success, refund_id = wx_pay.order_refund(order.transaction_id,refund_order_id, int(order.change_money * 100))
        #
        # if success:
        #     handle_wx_refund_create(refund_order_id, order.transaction_id, order.change_money, order.user_id, f'测试期间自动退款[退款id{refund_id}]')


def create_charge_order(user_id, transaction_id, out_trade_no, success_time, charge_money):
    from app.shell import req_term   # 发送充电命令
    from app.utils.get_seq import Get_SeqNo
    from app.command.tools.ApiTool import ApiTool
    from app.utils.handle_order import HandleOrder
    apitool = ApiTool(log)
    # 创建微信交易记录
        # 保证变更金额为正浮点数
    success_time_dt = datetime.datetime.strptime(success_time, "%Y-%m-%dT%H:%M:%S+08:00")
    charge_money = float(charge_money)
    charge_money = abs(charge_money)
    OrderNumber_ = Get_SeqNo("CHARGE_ORDER")[-10:]
    OrderNumber = hex(int(OrderNumber_)).lstrip('0x').zfill(8).upper()

    charge_info = SOrderNumMap.objects.filter(sub_order=out_trade_no, user_id=user_id).first()
    if charge_info:
        charge_info.transaction_id = transaction_id
        charge_info.charge_order = OrderNumber
        charge_info.save()

        eq_id = charge_info.eq_id
        eq_port = charge_info.eq_port
        term_address = charge_info.term_address
        charge_type = 'money'
        pay_way = 'online'
        fee_type = charge_info.fee_type
        fee_no = charge_info.fee_no
        site_id = charge_info.site_id
        order_source = charge_info.order_source

        SOrderUseMoney.objects.create(
            order_id=OrderNumber,
            create_time=datetime.datetime.now()
        )

        # 创建订单
        SOrderInfo.objects.create(
            site_id=site_id,
            eq_id=eq_id,
            eq_port=eq_port,
            term_address=term_address,
            charge_type=charge_type,
            pay_way=pay_way,
            charge_time=0,
            charge_electric=0,
            charge_money=charge_money,
            fee_type=fee_type,
            fee_no=fee_no,
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

        SWxTranOrderDetail.objects.filter(order_id=out_trade_no, user_id=user_id).update(
            charge_order=OrderNumber
        )

        handleorder = HandleOrder(log)
        # 创建费用详细信息
        handleorder.create_fee_detail(site_id, OrderNumber, fee_type, fee_no)

        # 发送充电指令
        DurationOrAmount_ = 600
        hex_DurationOrAmount_ = hex(DurationOrAmount_).lstrip('0x').zfill(4)
        DurationOrAmount_h = apitool.str_reverse(hex_DurationOrAmount_)
        json_data = {
            'number': '0420',
            'terminal_address': term_address,
            'Special_data': {
                'SocketNumber': eq_port,
                'OrderNumber': OrderNumber,
                'electrovalence': '0050',  # 这个电价没用，写死
                'type': '01',  # 00：金额，01：时间
                'DurationOrAmount': DurationOrAmount_h
            }
        }
        req_term(json_data)



@transaction.atomic
def handle_wx_order_recharge_success(out_trade_no, success_time, transaction_id):
    """
    订单充值成功，创建充电订单，开启充电
    :param out_trade_no:
    :param success_time:
    :param transaction_id:
    :return:
    """
    # time.sleep(10)
    log.info(f'订单支付成功，开始创建充电订单')
    success_time_dt = datetime.datetime.strptime(success_time, "%Y-%m-%dT%H:%M:%S+08:00")
    order = SWxTranOrderDetail.objects.filter(order_id=out_trade_no).first()
    if order and order.state == '1':
        order.finish_time = success_time_dt
        order.transaction_id = transaction_id
        order.state = '2'
        order.save()
        # user_id, transaction_id, out_trade_no, success_time, charge_money
        create_charge_order(order.user_id, transaction_id, out_trade_no, success_time, order.change_money)


        # # todo 测试期间自动退款
        # refund_order_id = get_seq.Get_SeqNo("PAY_ORDER")
        # success, refund_id = wx_pay.order_refund(order.transaction_id,refund_order_id, int(order.change_money * 100))
        #
        # if success:
        #     handle_wx_refund_create(refund_order_id, order.transaction_id, order.change_money, order.user_id, f'测试期间自动退款[退款id{refund_id}]')


# 处理退款发起后创建操作
def handle_wx_refund_create(order_id, transaction_id, amount, user_id, remark=None):
    SWxTranDetail.objects.create(
        change_type='out',
        change_money=amount,
        user_id=user_id,
        order_id=order_id,
        transaction_id=transaction_id,
        verify_state='1',
        verify_time=datetime.datetime.now(),
        create_time=datetime.datetime.now(),
        remark=remark,
        state='1'
    )


# 处理退款完成操作
def handle_wx_refund_success(refund_order_id, finish_time):
    finish_time_dt = datetime.datetime.strptime(finish_time, "%Y-%m-%dT%H:%M:%S+08:00")
    res = SWxTranDetail.objects.filter(order_id=refund_order_id, change_type='out', state='1').update(state='2', finish_time=finish_time_dt)


def handle_wx_order_refund_success(out_trade_no, out_refund_no, success_time, transaction_id):
    finish_time_dt = datetime.datetime.strptime(success_time, "%Y-%m-%dT%H:%M:%S+08:00")
    # 更新微信订单交易信息
    SWxTranOrderDetail.objects.filter(order_id=out_refund_no, change_type='out', state='1').update(
        state='2',
        finish_time=finish_time_dt,
        transaction_id=transaction_id
    )
    # 更新订单状态
    sub_ouder_info = SOrderNumMap.objects.filter(sub_order=out_trade_no, transaction_id=transaction_id).first()
    charge_order = sub_ouder_info.charge_order
    dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
    SOrderInfo.objects.filter(order_id=charge_order, create_time__gte=dt).update(
        refund_state='1'
    )

# 处理微信转账成功
def handle_wx_transfer_money_success(out_bill_no, transfer_bill_no, state, fail_reason, update_time):
    """

    :param out_bill_no: 商户单号
    :param transfer_bill_no: 微信单号
    :param state: 状态
    :param fail_reason: 失败原因
    :return:
    """
    try:
        log.info(f'转账回调：{out_bill_no}， {transfer_bill_no}， {state}, {fail_reason}')
        from app.utils.handle_order import HandleOrder
        handle = HandleOrder(log)
        finish_time_dt = datetime.datetime.strptime(update_time, "%Y-%m-%dT%H:%M:%S+08:00")
        cashout_info = SWxCashoutDetail.objects.filter(order_id=out_bill_no, transfer_bill_no=transfer_bill_no)[0]
        user_id = cashout_info.user_id
        money = cashout_info.amount
        if state == 'SUCCESS':
            log.info(f'成功')
            SWxCashoutDetail.objects.filter(order_id=out_bill_no, transfer_bill_no=transfer_bill_no).update(
                wx_state_str=state,
                fail_reason=fail_reason,
                finish_time=finish_time_dt,
                state='2',
                user_varify_state='1'
            )
            # 释放冻结
            handle.unfreeze_money(user_id, money)
            # 扣钱
            handle.deduct_money(user_id, money)
        elif state == 'FAIL':
            log.info(f'失败')
            SWxCashoutDetail.objects.filter(order_id=out_bill_no, transfer_bill_no=transfer_bill_no).update(
                wx_state_str=state,
                fail_reason=fail_reason,
                finish_time=finish_time_dt,
                state='9',
            )
            # 释放冻结
            handle.unfreeze_money(user_id, money)
    except Exception as e:
        log.error(f'微信回调处理失败：{e}', exc_info=True)

def handle_profit_share_create(tran_order_id, transaction_id):
    """

    :param tran_order_id: 支付订单号
    :param order_id: 分账订单号
    :param transaction_id: 交易id
    :param receiver_info: 接收人信息
    :return:
    """
    from app.utils.get_seq import Get_SeqNo
    log.info(f'创建分账记录')
    try:
        order = SWxDisProfitOrder.objects.filter(tran_order_id=tran_order_id).first()
        if not order :

            # 对交易进行分类
            recharge_type = tran_order_id[0:6]
            source = ''
            order_money = decimal.Decimal(0)
            if recharge_type == 'WF_CAR':
                tran_order_info = SWxTranCardDetail.objects.filter(order_id=tran_order_id)
                # transaction_id = tran_order_info[0].transaction_id
                order_money = tran_order_info[0].change_money
                source = '卡充值'
            elif recharge_type == 'WF_PAY':
                tran_order_info = SWxTranDetail.objects.filter(order_id=tran_order_id)
                # transaction_id = tran_order_info[0].transaction_id
                order_money = tran_order_info[0].change_money
                source = '钱包充值'

            # elif recharge_type == 'WF_SUB':  # 单独处理
            #     tran_order_info = SWxTranOrderDetail.objects.filter(order_id=tran_order_id)
            #     # transaction_id = tran_order_info[0].transaction_id
            #     order_money = tran_order_info[0].change_money
            #     source = '订单在线支付'
            receiver_info = SDisProfitReceiver.objects.filter()[0]
            type = receiver_info.type
            account = receiver_info.account
            rate = receiver_info.rate
            description = receiver_info.description
            amount = int(order_money * 100 * rate)
            dis_order_id = Get_SeqNo('PROFIT_SHARE_WX')
            profit_info = SWxDisProfitOrder.objects.create(
                dis_order_id=dis_order_id,
                tran_order_id=tran_order_id,
                transaction_id=transaction_id,
                account=account,
                amount=amount / 100,
                source=source,
                description=description,
                create_time=datetime.datetime.now()
            )
            receivers = [
                {
                    'type': type,
                    'account': account,
                    'amount': amount,
                    'description': description
                }
            ]
            time.sleep(10)
            res = wx_pay.wx_profit_share(tran_order_id, dis_order_id, transaction_id, amount, receivers)
            log.info(f'请求分账结果：{res[0]}')
            log.info(f'请求分账结果：{res[1]}')
            # profit_info.
            message = json.loads(res[1])
            wx_order_id = message.get('order_id')

            state = message.get('state')
            receivers = message.get('receivers')
            detail_id = receivers[0].get('detail_id')
            result = receivers[0].get('result')
            fail_reason = receivers[0].get('fail_reason', '')
            finish_time = receivers[0].get('finish_time')
            type = receivers[0].get('type')
            finish_time_dt = datetime.datetime.strptime(finish_time, "%Y-%m-%dT%H:%M:%S+08:00")
            if result == 'PENDING':
                state = '0'
            elif result == 'SUCCESS':
                state = '1'
            elif result == 'CLOSED':
                state = '-1'
            else:
                state = '-2'

            profit_info.wx_order_id = wx_order_id
            profit_info.detail_id = detail_id
            profit_info.wx_state_str = result
            profit_info.fail_reason = fail_reason
            profit_info.finish_time = finish_time_dt
            profit_info.state = state
            profit_info.receiver_type = type
            profit_info.save()



    except Exception as e:
        log.error(f'分賬出現異常：{e}', exc_info=True)




# 创建或更新用户
def create_or_update_user(union_id, wx_open_id=None, xcx_open_id=None, wx_session_key=None):
    user = None
    if union_id:
        user = SUserInfo.objects.filter(union_id=union_id).first()
    if not user:
        log.info('公众号和小程序之前都没进入过')
        # 公众号和小程序之前都没进入过
        user = SUserInfo.objects.create(
            union_id=union_id,
            xcx_open_id=xcx_open_id,
            wx_open_id=wx_open_id,
            wx_session_key=wx_session_key,
            account=0,
            create_time=datetime.datetime.now(),
            wx_update_time=datetime.datetime.now(),
            is_fetch_wx_info='0',
            state='0',
            identity='0',
            max_order_count=10
        )
        user.user_no = str(user.user_id).zfill(8) + str(random.randint(100, 999))
        user.save()

    else:
        log.info('之前进入过小程序或公众号')
        # 之前进入过小程序或公众号
        if wx_open_id:
            user.wx_open_id = wx_open_id
        if xcx_open_id:
            user.xcx_open_id = xcx_open_id
        if wx_session_key:
            user.wx_session_key = wx_session_key
        user.wx_update_time = datetime.datetime.now()
        user.save()
    print('user=',user)
    return user


# 充电开始提醒
def charge_start_notice(order_id):
    log.info('开始发送充电开始提醒')
    try:
        order = SOrderInfo.objects.filter(order_id=order_id).first()
        user = SUserInfo.objects.filter(user_id=order.user_id).first()
        wx_open_id = user.wx_open_id
        if wx_open_id:
            charge_type_kv = {
                'auto': '自动充电',
                'elec': '定电量充电',
                'time': '定时长充电',
                'money': '定金额充电'
            }
            site_address = ''
            eq = SEqInfo.objects.filter(eq_id=order.eq_id).first()
            if eq:
                site = SSiteInfo.objects.filter(site_id=eq.site_id).first()
                site_address = site.site_address
            SWxTempMsg.objects.create(
                temp_type='charge_start',
                open_id=wx_open_id,
                k1='尊敬的用户，您好，您的爱车已经开始充电。',
                k2=order.eq_id,
                k3=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                k4=charge_type_kv.get(order.charge_type),
                k5=site_address,
                k6='充电桩只提供充电服务，不提供看管服务，请保管好随身物品',
                xcx_app_id=WX_XCX_APP_ID,
                xcx_path=f'/pages/Orderdetail/index?orderNum={order.order_id}',
                create_time=datetime.datetime.now(),
                state='0'
            )
    except:
        log.error('发送充电开始提醒失败', exc_info=True)


# 充电结束提醒
def charge_end_notice(order_id):
    log.info('开始发送充电结束提醒')
    try:
        order = SOrderInfo.objects.filter(order_id=order_id).first()
        user = SUserInfo.objects.filter(user_id=order.user_id).first()
        wx_open_id = user.wx_open_id
        if wx_open_id:
            use_time_minute = str(int(order.use_time / 60)) + '分钟'
            use_money = str(order.use_money) + '元'
            end_tip = SEndTypeKv.objects.filter(end_type=order.end_type).first().end_tip
            SWxTempMsg.objects.create(
                temp_type='charge_end',
                open_id=wx_open_id,
                k1='尊敬的用户，您好，您的爱车已经结束充电。',
                k2=order.eq_id,
                k3=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                k4=use_time_minute,
                k5=use_money,
                k6=end_tip,
                k7='感谢您的使用。如有疑问请致电 400-080-6569',
                xcx_app_id=WX_XCX_APP_ID,
                xcx_path=f'/pages/Orderdetail/index?orderNum={order.order_id}',
                create_time=datetime.datetime.now(),
                state='0'
            )
    except:
        log.error('发送充电结束提醒失败', exc_info=True)



# 图片链接转换：字符串相对链接列表转换为绝对链接列表
def img_str2url_list(img_str):
    try:
        relative_img_list = eval(img_str)
    except:
        return []
    img_list = []
    for relative_img in relative_img_list:
        img_list.append(ROOT_API + relative_img)
    return img_list


# 处理设备异常订单 20220804 将设备上报状态是空闲的设备关联充电中订单结算（以最后一次上报数据为准，可能会有偏差）
def handle_eq_exp_order(eq_code):
    eq_id = devid2eqid(eq_code)
    order = SOrderInfo.objects.filter(eq_id=eq_id, state='1').order_by('-create_time').first()
    if not order:
        return
    log.info(f'开始处理异常订单：{order.order_id}')
    order_finish(order.order_id)
