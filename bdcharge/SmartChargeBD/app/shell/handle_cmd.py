import re
import sys
import os
import time

import django
import datetime

# 添加当前路径到环境变量中

# pwd = os.path.dirname(os.path.realpath(__file__))
# pwd = pwd.replace('\charge\shell', '').replace('/charge/shell', '')
# # pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCharge.settings_real')  # VueSt是自己的项目名称
# django.setup()  # 更新配置

import json
import datetime
from app.models import *
from django.db.models import Q
from app.utils.eq_api.tieta_api import TietaApi
from app.utils.eq_api import tieta_handle2
from app.utils import MyLog
from app.utils import handle
from SmartChargeBD.settings import BASE_DIR
from SmartChargeBD.settings import WX_XCX_APP_ID
from app.utils import wx_temp_msg

# log = MyLog.getLogger(__file__)
log = MyLog.MyLog(__file__, 'handle_cmd.log', BASE_DIR).logger
log.info('handle_cmd start')

api = TietaApi()
th = tieta_handle2.TietaHandle(SCmdDetail)


# 处理注册
def handle_register(devId, txnNo, cmd):
    login_info, reply_cmd = api.recv_login_up(cmd.cmd)
    # 更新设备信息
    SEqInfo.objects.filter(eq_code=devId).update(
        eq_type=login_info.get('devType'),
        eq_attr=login_info.get('devAttr'),
        eq_elec_attr=login_info.get('devElecAttr'),
        soft_version=login_info.get('softVersion'),
        hard_version=login_info.get('hardVersion'),
        agree_version=login_info.get('protocolVersion'),
        iccid=login_info.get('iccid'),
        last_conn_time=datetime.datetime.now()
    )
    handle.add_cmd(devId, reply_cmd, txnNo)
    # 设置计费策略
    priceMode = handle.get_price_mode(devId)
    th.set_price_mode_car(devId, priceMode)
    handle.end_cmd(cmd)


# 处理属性上报
def handle_attr_up(devId, txnNo, cmd):
    attr_info_list, reply_cmd = api.recv_attr_up(cmd.cmd)
    log.info(f"attr_info_list={attr_info_list}")
    for item in attr_info_list:
        devId = item.get('devId')
        k = item.get('k')
        v = item.get('v')
        # 添加采集数据
        handle.add_eq_attr_data(devId, k, v)
        # 20220804增加 根据最新上报设备状态处理异常订单（未结束订单）
        if k == 'charge_state' and v == '1':
            handle.handle_eq_exp_order(devId)

    handle.add_cmd(devId, reply_cmd, txnNo)
    handle.end_cmd(cmd)


# 处理交易上报
def handle_tran_up(devId, txnNo, cmd):
    # 传给硬件的用户余额
    account = handle.get_user_ok_money_for_eq(devId)
    attr_info_list, reply_cmd = api.recv_tran_up(cmd.cmd, account)
    log.info(f"attr_info_list={attr_info_list}")
    for item in attr_info_list:
        devId = item.get('devId')
        k = item.get('k')
        v = item.get('v')
        if k == 'charge_attrs':
            _charge_attrs_kv = handle.unpack_charge_attrs(v)
            # 更新订单参数
            handle.update_order_attr(devId, _charge_attrs_kv)
            # 添加子采集数据
            for sub_k, sub_v in _charge_attrs_kv.items():
                handle.add_eq_attr_data(devId, sub_k, sub_v)
        else:
            # 添加采集数据
            handle.add_eq_attr_data(devId, k, v)
    handle.add_cmd(devId, reply_cmd, txnNo)
    handle.end_cmd(cmd)


# 处理控制操作返回
def handle_ctrl_res(devId, txnNo, cmd):
    eq_id = handle.devid2eqid(devId)
    opera = SOperaDetail.objects.filter(eq_id=eq_id, seq_no=txnNo).first()
    if not opera:
        handle.end_cmd(cmd)
        return

    success = api.unpack_ctrl_post_one(cmd.cmd)
    if opera.opera_type == 'charge_open':
        _handle_charge_open_order(devId, txnNo, eq_id, success)
    elif opera.opera_type == 'charge_stop':
        # 充电停止成功返回 不需要额外处理 订单结算是通过上送的采集数据状态进行结算
        pass
        # _handle_charge_stop(eq_id, success)

    # 第一次更新 后续不更新
    if opera.state == '1':
        if success:
            opera.state = '2'
        else:
            opera.state = '3'
        opera.update_time = datetime.datetime.now()

        opera.save()
    handle.end_cmd(cmd)


# 回复502
def _reply_502(devId, txnNo, success):
    log.info(f'发送502,devId={devId}, txnNo={txnNo}, success={success}')
    reply_cmd = api.reply_501_ack(devId, txnNo, success)
    handle.add_cmd(devId, reply_cmd, txnNo)


# 处理开始充电订单（发送命令硬件回复后处理）
def _handle_charge_open_order(devId, txnNo, eq_id, success=True):
    # order = SOrderInfo.objects.filter(eq_id=eq_id, state='0').order_by('-create_time').first()
    order = SOrderInfo.objects.filter(eq_id=eq_id).order_by('-create_time').first()

    # 第一次收到501 处理充电开始
    if order.state == '0':
        if success:
            order.state = '1'
            order.begin_time = datetime.datetime.now()
            handle.charge_start_notice(order.order_id)
        else:
            order.state = '9'
            order.remark = '充电桩开启失败'
            order.end_time = datetime.datetime.now()
            # 将设备充电状态解除占用
            SEqInfo.objects.filter(eq_id=eq_id, eq_state='1').update(eq_state='0')
        order.save()
    # 非第一次收到501 不处理 只回复502
    else:
        pass

    # 回复确认收到501消息（502）
    _reply_502(devId, txnNo, success)


# 处理开始充电（发送命令前处理）
def _handle_charge_open_send(dev_id, opera):
    order_id = opera.order_id
    if not order_id:
        return None
    order = SOrderInfo.objects.filter(order_id=order_id).first()
    if not order:
        return None
    account_ok = ViewUserAccountOk.objects.filter(user_id=order.user_id).first()
    if not account_ok:
        return None
    # 准备调用函数开启充电 判断传参
    to_kwargs = {'account_money': account_ok.ok_money}
    charge_type = order.charge_type
    if charge_type == 'auto':
        pass
    elif charge_type == 'elec':
        to_kwargs['set_elect'] = order.charge_electric
    elif charge_type == 'time':
        to_kwargs['set_time'] = order.charge_time
    elif charge_type == 'money':
        to_kwargs['set_money'] = order.charge_money
    seq_no = th.eq_charge_open(dev_id, True, **to_kwargs)
    return seq_no


# 处理结束充电（发送命令前处理）
def _handle_charge_stop_send(dev_id, opera):
    seq_no = th.eq_charge_open(dev_id, False)
    return seq_no


# 发送开启充电超时微信模板消息
def _send_open_timeout_wx_temp_msg(order_id):
    order = SOrderInfo.objects.filter(order_id=order_id).first()
    if not order:
        return
    user = SUserInfo.objects.filter(user_id=order.user_id).first()
    if not user:
        return
    wx_open_id = user.wx_open_id
    end_tip = "开启充电桩超时"
    remark = '可能因为以下原因导致结束充电：\r\n1、您的充电器待机，停止充电；\r\n2、您的插头没插好或松动。\r\n感谢您的使用，如有疑问请致电 400-080-6569'
    SWxTempMsg.objects.create(
        temp_type='charge_end',
        open_id=wx_open_id,
        k1='尊敬的用户，您好，您的爱车已经结束充电。',
        k2=order.eq_id,
        k3=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        k4='0',
        k5='0',
        k6=end_tip,
        k7=remark,
        xcx_app_id=WX_XCX_APP_ID,
        xcx_path=f'/pages/Orderdetail/index?orderNum={order.order_id}',
        create_time=datetime.datetime.now(),
        state='0'
    )


# 处理超时操作 超时返回True 否则返回False
def handle_opera_timeout(opera):
    OPERA_TIMEOUT_SECONDS = 60
    timeout_dt = datetime.datetime.now() - datetime.timedelta(seconds=OPERA_TIMEOUT_SECONDS)
    if opera.create_time >= timeout_dt:
        return False
    log.info(f'操作超时处理程序开始,opera_id={opera.id}')
    # 开启订单超时处理程序
    if opera.opera_type == 'charge_open':
        order = SOrderInfo.objects.filter(eq_id=opera.eq_id, state='0').order_by('-create_time').first()
        if order:
            order.state = '9'
            order.update_time = datetime.datetime.now()
            order.save()

            # 将设备充电状态解除占用
            SEqInfo.objects.filter(eq_id=opera.eq_id, eq_state='1').update(eq_state='0')

            # 回复设备502 超时关闭订单
            devId = handle.eqid2devid(opera.eq_id)
            txnNo = opera.seq_no
            if devId and txnNo:
                _reply_502(devId, txnNo, False)

            # 发送模板消息
            _send_open_timeout_wx_temp_msg(order.order_id)

    # 订单结束超时处理
    elif opera.opera_type == 'charge_stop':
        # 订单结束超时不需要处理
        pass

    opera.update_time = datetime.datetime.now()
    opera.state = '9'
    opera.save()
    return True


# 处理单个操作 操作状态 0 -> 1
def handle_opera_one(opera):
    dev_id = handle.eqid2devid(opera.eq_id)
    # 创建操作命令
    seq_no = None
    if opera.opera_type == 'charge_open':
        seq_no = _handle_charge_open_send(dev_id, opera)
    elif opera.opera_type == 'charge_stop':
        seq_no = _handle_charge_stop_send(dev_id, opera)
    elif opera.opera_type == '':
        pass
    opera.seq_no = seq_no
    opera.state = '1'
    opera.update_time = datetime.datetime.now()
    opera.save()


# 处理设备报文主函数
def handle_eq_cmd_main(cmd):
    log.info(f'handle_main {cmd.cmd}')
    data = json.loads(cmd.cmd)
    msgType = data.get('msgType')
    devId = data.get('devId')
    txnNo = data.get('txnNo')
    if not msgType:
        return
    if msgType == 110:
        handle_register(devId, txnNo, cmd)
    elif msgType == 310:
        handle_attr_up(devId, txnNo, cmd)
    elif msgType == 320:
        handle_tran_up(devId, txnNo, cmd)
    elif msgType == 501:
        handle_ctrl_res(devId, txnNo, cmd)
    else:
        handle.end_cmd(cmd)

    # 更新设备最后活动时间
    SEqInfo.objects.filter(eq_code=devId).update(last_active_time=datetime.datetime.now())


# 设备离线运维判断（自动创建运维任务）
def eq_offline_devops_check(times):
    try:
        if times % 100 != 0:
            # 循环100次执行一次判断
            return
        # 1小时未活动的设备认为离线
        dt = datetime.datetime.now() - datetime.timedelta(hours=1)
        eqs = SEqInfo.objects.filter(last_active_time__lt=dt)
        for eq in eqs:
            # 如果没有待处理或处理中的运维任务就创建
            task = SDevopsTaskInfo.objects.filter(eq_id=eq.eq_id, state__in=['0', '1']).first()
            if not task:
                SDevopsTaskInfo.objects.create(
                    task_name=f'{eq.eq_id}号充电桩离线',
                    task_desc=f'{eq.eq_id}号充电桩离线',
                    task_type='1',
                    site_id=eq.site_id,
                    eq_id=eq.eq_id,
                    create_type='sys',
                    create_time=datetime.datetime.now(),
                    state='0'
                )
    except:
        log.error('eq_offline_devops_check error', exc_info=True)


def main():
    times = 0
    while True:
        dt = datetime.datetime.now() - datetime.timedelta(hours=1)
        cmds = SCmdDetail.objects.filter(send_type='2', state='0', create_time__gte=dt)
        for cmd in cmds:
            try:
                handle_eq_cmd_main(cmd)
            except:
                log.error('error', exc_info=True)

        # 查询是否有待处理操作命令
        # # 将超时操作更新
        # timeout_dt = datetime.datetime.now() - datetime.timedelta(seconds=OPERA_TIMEOUT_SECONDS)
        # SOperaDetail.objects.filter(Q(state='0') | Q(state='1'), create_time__lt=timeout_dt).update(state='9',
        #                                                                                             update_time=datetime.datetime.now())

        # 处理操作
        operas = SOperaDetail.objects.filter(state__in=['0', '1'])
        for opera in operas:
            try:
                is_time_out = handle_opera_timeout(opera)
                if not is_time_out:
                    if opera.state == '0':
                        handle_opera_one(opera)
            except:
                log.error('error2', exc_info=True)

        # 判断设备连接状态
        # 将连接状态是在线，且10分钟未活动的设备置为未连接状态
        dt1 = datetime.datetime.now() - datetime.timedelta(minutes=10)
        SEqInfo.objects.filter(Q(last_active_time__lt=dt1) | Q(last_active_time=None), conn_state='1').update(conn_state='0')
        # 将连接状态是离线，且5分钟内活动过的设备置为连接状态
        dt2 = datetime.datetime.now() - datetime.timedelta(minutes=5)
        SEqInfo.objects.filter(conn_state='0', last_active_time__gte=dt2).update(conn_state='1')

        eq_offline_devops_check(times)

        time.sleep(1)
        times = (times + 1) % 1000


if __name__ == "__main__":
    # exit(0)
    main()
