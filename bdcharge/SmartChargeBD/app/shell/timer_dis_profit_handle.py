"""
定时处理分润
"""
import time
import datetime
from SmartChargeBD.settings import BASE_DIR
from app.models import SDisProfitMode, SDisProfitDetail, SOrderInfo, SEqInfo, SSiteInfo, SPlatInfo, SOperatorInfo, \
    SHardFirmInfo
from app.utils.handle import account_change
from app.utils import MyLog
from django.db import transaction

log = MyLog.MyLog(__file__, 'dis_profit.log', BASE_DIR).logger


# 平台分润
def _dis_profit_plat(order, eq, site, disMode):
    log.info('开始平台分润')
    site_id = site.site_id
    plat_id = site.plat_id
    plat_rate = disMode.plat_rate
    all_amount = order.use_money
    log.info(f'order_id={order.order_id},site_id={site_id},plat_rate={plat_rate},all_amount={all_amount}')
    if not plat_id:
        log.info(f'站点未关联平台，平台不分润，site_id={site_id}')
        return
    plat = SPlatInfo.objects.filter(plat_id=plat_id).first()
    if not plat:
        log.info(f'未找到平台信息，平台不分润，plat_id={plat_id}')
        return
    bind_user_id = plat.bind_user_id
    if not bind_user_id:
        log.info(f'平台未绑定微信账号，平台不分润，plat_id={plat_id}')
        return
    own_dis_amount = float((all_amount * plat_rate) / 100)
    if own_dis_amount < 0.01:
        log.info(f'平台分润金额小于0.01，不分润')
        return
    # 更新用户钱包
    flag = account_change(bind_user_id, own_dis_amount, 'in', order.order_id, '订单分润（平台）')
    if not flag:
        log.error(f'平台分润失败', exc_info=True)
        return
    # 创建分润记录
    SDisProfitDetail.objects.create(
        eq_id=eq.eq_id,
        site_id=site_id,
        order_id=order.order_id,
        dis_mode_id=disMode.dis_mode_id,
        dis_type='plat',
        dis_own_id=plat_id,
        user_id=bind_user_id,
        order_money=order.use_money,
        order_finish_time=order.update_time,
        dis_rate=plat_rate,
        dis_money=own_dis_amount,
        create_time=datetime.datetime.now(),
        state='1'
    )
    log.info(f'平台分润成功，order_id={order.order_id}')
    return


# 运营商分润
def _dis_profit_opera(order, eq, site, disMode):
    log.info('开始运营商分润')
    site_id = site.site_id
    operator_id = site.operator_id
    opera_rate = disMode.opera_rate
    all_amount = order.use_money
    log.info(f'order_id={order.order_id},site_id={site_id},operator_id={operator_id},all_amount={all_amount}')
    if not operator_id:
        log.info(f'站点未关联运营商，运营商不分润，site_id={site_id}')
        return
    operator = SOperatorInfo.objects.filter(operator_id=operator_id).first()
    if not operator:
        log.info(f'未找到运营商信息，运营商不分润')
        return
    bind_user_id = operator.bind_user_id
    if not bind_user_id:
        log.info(f'运营商未绑定微信账号，运营商不分润，operator_id={operator_id}')
        return
    own_dis_amount = float((all_amount * opera_rate) / 100)
    if own_dis_amount < 0.01:
        log.info(f'运营商分润金额小于0.01，不分润')
        return
    # 更新用户钱包
    flag = account_change(bind_user_id, own_dis_amount, 'in', order.order_id, '订单分润(运营商)')
    if not flag:
        log.error(f'运营商分润失败', exc_info=True)
        return
    # 创建分润记录
    SDisProfitDetail.objects.create(
        eq_id=eq.eq_id,
        site_id=site_id,
        order_id=order.order_id,
        dis_mode_id=disMode.dis_mode_id,
        dis_type='opera',
        dis_own_id=operator_id,
        user_id=bind_user_id,
        order_money=order.use_money,
        order_finish_time=order.update_time,
        dis_rate=opera_rate,
        dis_money=own_dis_amount,
        create_time=datetime.datetime.now(),
        state='1'
    )
    log.info(f'运营商分润成功，order_id={order.order_id}')
    return


# 硬件商分润
def _dis_profit_hard(order, eq, site, disMode):
    log.info('开始硬件商分润')
    site_id = site.site_id
    hard_id = eq.hard_id
    hard_rate = disMode.hard_rate
    all_amount = order.use_money
    log.info(f'order_id={order.order_id},site_id={site_id},hard_id={hard_id},all_amount={all_amount}')
    if not hard_id:
        log.info(f'设备未关联硬件商，硬件商不分润，eq_id={eq.eq_id}')
        return
    operator = SHardFirmInfo.objects.filter(id=hard_id).first()
    if not operator:
        log.info(f'未找到硬件商信息，硬件商不分润')
        return
    bind_user_id = operator.bind_user_id
    if not bind_user_id:
        log.info(f'硬件商未绑定微信账号，硬件商不分润，hard_id={hard_id}')
        return
    own_dis_amount = float((all_amount * hard_rate) / 100)
    if own_dis_amount < 0.01:
        log.info(f'硬件商分润金额小于0.01，不分润')
        return
    # 更新用户钱包
    flag = account_change(bind_user_id, own_dis_amount, 'in', order.order_id, '订单分润(硬件商)')
    if not flag:
        log.error(f'硬件商分润失败', exc_info=True)
        return
    # 创建分润记录
    SDisProfitDetail.objects.create(
        eq_id=eq.eq_id,
        site_id=site_id,
        order_id=order.order_id,
        dis_mode_id=disMode.dis_mode_id,
        dis_type='hard',
        user_id=bind_user_id,
        order_money=order.use_money,
        order_finish_time=order.update_time,
        dis_rate=hard_rate,
        dis_money=own_dis_amount,
        create_time=datetime.datetime.now(),
        state='1'
    )
    log.info(f'硬件商分润成功，order_id={order.order_id}')
    return


# 订单分润
@transaction.atomic()
def dis_profit(order):
    log.info(f'开始分润订单：{order.order_id}')
    eq_id = order.eq_id
    eq = SEqInfo.objects.filter(eq_id=eq_id).first()
    site_id = eq.site_id
    site = SSiteInfo.objects.filter(site_id=site_id).first()
    dis_mode_id = site.dis_mode_id
    if not dis_mode_id:
        log.info(f'站点未设置分润策略，不分润，eq_id={eq_id}，site_id={site_id}')
        return
    disMode = SDisProfitMode.objects.filter(dis_mode_id=dis_mode_id).first()
    if disMode.state != '1':
        log.info(f'分润策略未开启，不分润')
        return
    if disMode.dis_begin_time and order.update_time < disMode.dis_begin_time:
        log.info(f'订单完成时间小于分润策略设置起始时间，不分润')
        return
    dis_all_amount = order.use_money
    if dis_all_amount < 0.01:
        log.info(f'分润总金额小于0.01，不分润')
        return
    plat_rate = disMode.plat_rate
    opera_rate = disMode.opera_rate
    hard_rate = disMode.hard_rate
    if (plat_rate + opera_rate + hard_rate) > 100:
        log.info(f'分润总比例大于100%，不分润，eq_id={eq_id}，site_id={site_id}')
        return
    # 平台分润
    _dis_profit_plat(order, eq, site, disMode)
    # 运营商分润
    _dis_profit_opera(order, eq, site, disMode)
    # 硬件商分润
    _dis_profit_hard(order, eq, site, disMode)
    log.info(f'订单分润完成，order_id={order.order_id}')
    return


def main():
    log.info('handle_main start')
    before_72hour_dt = datetime.datetime.now() - datetime.timedelta(hours=72)
    before_96hour_dt = datetime.datetime.now() - datetime.timedelta(hours=96)
    begin_date = datetime.datetime.strptime('2022-08-20 00:00:00', '%Y-%m-%d %H:%M:%S')
    orders = SOrderInfo.objects.filter(state='2', update_time__lte=before_72hour_dt, update_time__gte=begin_date, use_money__gte=0)
    if SDisProfitDetail.objects.count() > 0:
        # 已经分润过 查询92小时前到72小时前订单即可
        orders = orders.filter(update_time__gte=before_96hour_dt)
    for order in orders:
        # 分润过不再参与分润
        if SDisProfitDetail.objects.filter(order_id=order.order_id).exists():
            continue
        dis_profit(order)
    log.info('handle_main end')
