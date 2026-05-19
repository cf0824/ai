"""
周期处理微信提现
"""

import time
import json
import datetime
import os
import sys
import django
import decimal

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

from app.models import SWxCashoutDetail, SAccountIce, ViewUserAccountOk
from django.db.models import Q
from app.utils import MyLog
from django.db import transaction
from app.utils import wx_pay
# from SmartChargeBD.settings import BASE_DIR
from app.utils import handle

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
print(file_path)
print(file_name)

log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger
# log = MyLog.MyLog(__file__, 'handle_wx_cashout.log', BASE_DIR).logger


# 释放冻结
def _quit_ice_account(order_id):
    SAccountIce.objects.filter(link_type='cashout', link_id=order_id, state='1').update(state='0',
                                                                                        update_time=datetime.datetime.now())
def unfreeze_money(user_id, unfreeze_money):
    """
    释放冻结金额
    :param user_id:  用户id
    :param ice_money:  需要冻结的金额
    :return:
    """
    log.info(f'解冻金额：{user_id}, {unfreeze_money}')
    unfreeze_money = decimal.Decimal(str(unfreeze_money))
    # 查询用户账户信息
    user_account_info =ViewUserAccountOk.objects.filter(user_id=user_id).first()
    if not user_account_info:
        return False
    real_money = user_account_info.real_money
    ok_money = user_account_info.ok_money
    ice_money = user_account_info.ice_money

    # 检查需要解冻的金额是否大于已冻结的金额
    if unfreeze_money > ice_money:
        return False
    user_account_info.ok_money = ok_money + unfreeze_money
    user_account_info.ice_money = ice_money - unfreeze_money
    user_account_info.save()


    return True

# 处理提现订单
@transaction.atomic()
def handle_cash_out_order(order):
    try:
        log.info(f'开始处理提现订单：{order.order_id}')
        verify_state = order.verify_state
        if verify_state == '9':
            # 拒绝，释放冻结，提现失败
            _quit_ice_account(order.order_id)
            SWxCashoutDetail.objects.filter(order_id=order.order_id, verify_state='9', state='0').update(state='9',
                                                                                                         finish_time=datetime.datetime.now())
        elif verify_state == '1':
            # 通过，调用微信付款接口
            # 转换为分
            amount = int(order.amount * 100)
            res, paras = wx_pay.wx_cash_out(order.order_id, '账户提现', amount, order.open_id)
            log.info(f'提现res={res}, paras={paras}')
            if not res or not res[0]:
                log.error(f'返回数据错误，本次不处理，order_id={order.order_id}', exc_info=True)
                return
            code = res[0]
            detail = res[1]
            detail = json.loads(detail)
            state = detail.get('state')
            transfer_bill_no = detail.get('transfer_bill_no')
            package_info = detail.get('package_info')
            if code == 200:
                if state == 'WAIT_USER_CONFIRM':
                    log.info('提现响应：等待用户收款')
                    SWxCashoutDetail.objects.filter(order_id=order.order_id, verify_state='1', state='0').update(
                        state='1',
                        transfer_bill_no=transfer_bill_no,
                        package_info=package_info,
                        pay_start_time=datetime.datetime.now(),
                        wx_state_str=state,
                        wx_state='0'
                    )
                if state == 'PROCESSING':
                    log.info('提现响应：商户账户余额不足')
                    SWxCashoutDetail.objects.filter(order_id=order.order_id, verify_state='1', state='0').update(
                        state='9',
                        transfer_bill_no=transfer_bill_no,
                        package_info=package_info,
                        pay_start_time=datetime.datetime.now(),
                        wx_state_str=state,
                        wx_state='-1'
                    )
                log.info(f'已完成处理提现订单：{order.order_id}')
                return
            # todo 其实除了200 都是失败，只有500时可以重新发起，是微信那边的错误，其他情况都失败
            elif code == 500:
                log.error(f'微信返回500，官方建议重新发起，本次不处理，order_id={order.order_id}')
                return
            else:
                log.error('调用微信付款失败，更新提现失败')
                unfreeze_money(order.user_id, order.amount)
                _quit_ice_account(order.order_id)
                SWxCashoutDetail.objects.filter(order_id=order.order_id, verify_state='1', state='0').update(
                    state='9',
                    pay_start_time=datetime.datetime.now(),
                    finish_time=datetime.datetime.now(),
                    fail_reason=str(res),
                    wx_state='-1'
                )
        else:
            return
    except Exception as e:
        log.error(f'微信提现出现错误：{e}', exc_info=True)



# 处理提现结果
@transaction.atomic()
def handle_cash_out_result(order):
    log.info(f'开始处理提现结果订单：{order.order_id}')
    res = wx_pay.get_wx_cash_out_result(order.order_id)
    log.info(f'查询结果res={res}')
    if not res or not res[0] or not res[1]:
        log.error(f'返回数据错误，本次不处理，order_id={order.order_id}', exc_info=True)
        return
    code = res[0]
    detail = res[1]
    detail = json.loads(detail)
    if code != 200:
        log.error(f'本次不处理，order_id={order.order_id}')
        return
    state = detail.get('state')
    # 等待用户提现， 不做处理
    if state == 'WAIT_USER_CONFIRM':
        log.info('提现：等待用户收款')
        return
    # 成功处理
    if state == 'SUCCESS':
        log.info('开始提现成功处理')
        # 账户扣款
        success = handle.account_change(order.user_id, order.amount, 'out', order.order_id, '账户提现')
        if not success:
            log.error('扣款失败，本次不处理')
            return
        # 冻结释放
        _quit_ice_account(order.order_id)
        # 更新提现订单成功状态
        SWxCashoutDetail.objects.filter(order_id=order.order_id,
                                        verify_state='1',
                                        state='1').update(state='2',
                                                          wx_state='1',
                                                          finish_time=datetime.datetime.now())
        log.info('已完成提现成功处理')
        return
    # 失败处理
    if state == 'FAIL':
        log.info('开始提现失败处理')
        _quit_ice_account(order.order_id)
        SWxCashoutDetail.objects.filter(order_id=order.order_id,
                                        verify_state='1',
                                        state='1').update(state='9',
                                                          wx_state='-1',
                                                          finish_time=datetime.datetime.now(),
                                                          fail_reason=str(res))
        log.info('已完成提现失败处理')
        return
    # 其余不处理
    return



def main():
    log.info('微信提现订单处理程序启动')
    while True:
        # Q对象用于封装一个查询条件，而~Q则用于表示该查询条件的相反情况
        orders = SWxCashoutDetail.objects.filter(~Q(verify_state='0'), state='0') # 已经审核的，没处理的
        orders_count = orders.count()
        if orders_count > 0:
            log.info(f'待处理提现订单数:{orders_count}')
        for order in orders:
            handle_cash_out_order(order)

        # # 不用一直自动查
        # result_orders = SWxCashoutDetail.objects.filter(verify_state='1', state='1') # 审核通过、处理过的
        # result_orders_count = result_orders.count()
        # if result_orders_count > 0:
        #     log.info(f'待处理提现结果订单数:{result_orders_count}')
        # for order in result_orders:
        #     handle_cash_out_result(order)

        time.sleep(1)

if __name__ == '__main__':
    main()
