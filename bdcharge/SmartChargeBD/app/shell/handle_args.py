#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_args.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/1/13 10:20 
@Description :  通过查询数据库命令表，来执行相关操作
参数处理一共有两大类：查询参数、设置参数
这两类都有很多方法，需要一一匹配
'''
import decimal
import os
import sys
import django
import time
import json
import datetime

from django.db import transaction

pwd = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(pwd)
parent_dir_ = os.path.dirname(parent_dir)
# print(pwd)
# print(parent_dir)
# print(parent_dir_)
# print(sys.path)
sys.path.append(pwd)
sys.path.append(parent_dir)
sys.path.append(parent_dir_)
# print(sys.path)
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
# print(file_path)
# print(file_name)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger
# print(f'日志创建{file_path}')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()

from app.models import *
from app.utils import wx_temp_msg



class HandleArgsQ:  # 查询参数
    def __init__(self):
        pass

    def Q_commu_para(self, task_id, resp_cmd, operate_result):
        # 查询通信参数
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            heart_cycle = special_data['heart_cycle']
            up_cycle = special_data['up_cycle']
            delay_time = special_data['delay_time']

            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                heart_time=heart_cycle,
                uplink_interval=up_cycle,
                delay_time=delay_time,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询通信参数失败：不支持此功能')

        else:
            log.error(f'查询通信参数失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def Q_domain_port(self, task_id, resp_cmd, operate_result):
        # 查询域名端口
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            domain = special_data['domain']
            port = special_data['port']

            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                domain=domain,
                port=port,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询域名端口失败：不支持此功能')

        else:
            log.error(f'查询域名端口失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def Q_signal_strength(self, task_id, resp_cmd, operate_result):
        # 查询信号强度
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            signal_strength = special_data['Signal_strength']

            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                signal_strength=signal_strength,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询信号强度失败：不支持此功能')

        else:
            log.error(f'查询信号强度失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def Q_power_threshold(self, task_id, resp_cmd, operate_result):
        # 查询功率阈值
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            min_power = special_data['min_power']
            max_power = special_data['max_power']
            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                min_power=min_power,
                max_power=max_power,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询功率阈值失败：不支持此功能')

        else:
            log.error(f'查询功率阈值失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def Q_settle_allocation(self, task_id, resp_cmd, operate_result):
        # 查询结算配置
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            measure_model = special_data['measure_model']
            Hourly_price = special_data['Hourly_price']
            Rate_duration = special_data['Rate_duration']
            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                measure_model=measure_model,
                hourly_price=Hourly_price,
                rate_duration=Rate_duration,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询结算配置失败：不支持此功能')

        else:
            log.error(f'查询结算配置失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    # def Q_pile_status(self, task_id, resp_cmd, operate_result):
    #     # 查询充电桩状态
    #     if operate_result == '0':
    #         special_data = resp_cmd['app_region'].get('Specific_data_detail')
    #         measure_model = special_data['measure_model']
    #         Hourly_price = special_data['Hourly_price']
    #         Rate_duration = special_data['Rate_duration']
    #         terminal_address = resp_cmd['address_region'].get('address_term_r')
    #         # 更新设备参数
    #         SEqArgPrivate.objects.filter(terminal_address=terminal_address).update(
    #             measure_model=measure_model,
    #             hourly_price=Hourly_price,
    #             rate_duration=Rate_duration
    #         )
    #     elif operate_result == '1':
    #         log.error(f'查询结算配置失败：不支持此功能')
    #
    #     else:
    #         log.error(f'查询结算配置失败：未知原因')
    #
    #     SCmdInfo.objects.filter(id=task_id).update(
    #         update_status='1'
    #     )

    def Q_QRcode(self, task_id, resp_cmd, operate_result):
        # 查询二维码
        resp_cmd = json.loads(resp_cmd)
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            QR_data = special_data['QR_data']
            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                QR_code=QR_data,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'查询结算配置失败：不支持此功能')

        else:
            log.error(f'查询结算配置失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    # def Q_socket_status(self, task_id, resp_cmd, operate_result):
    #     log.info(f'接口：查询插座状态')
    #     log.info(f'响应报文：{resp_cmd}')
    #     log.info(f'操作结果：{operate_result}')
    #     pass

    def Q_total_electricity(self, task_id, resp_cmd, operate_result):
        resp_cmd = json.loads(resp_cmd)
        # 查询充电桩累计电量
        if operate_result == '0':
            special_data = resp_cmd['app_region'].get('Specific_data_detail')
            total_electricity = special_data['total_electricity']
            terminal_address = resp_cmd['address_region'].get('address_term_r')
            # 更新设备参数
            SEqInfo.objects.filter(terminal_address=terminal_address).update(
                total_electricity=total_electricity
            )
        elif operate_result == '1':
            log.error(f'查询充电桩累计电量失败：不支持此功能')

        else:
            log.error(f'查询充电桩累计电量失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def get_func_Q(self, AFN, Fn):
        Function_mapping = {
            '0A': {
                '01': self.Q_commu_para,
                '02': self.Q_domain_port,
                '03': self.Q_signal_strength,
                '17': self.Q_power_threshold,
                '18': self.Q_settle_allocation,
                # '19': self.Q_pile_status,  # 没有这个接口
                # '20': self.Q_socket_status,  # 在其他地方实现
                '21': self.Q_QRcode,
                '41': self.Q_total_electricity
            }
        }

        func = Function_mapping[AFN].get(Fn)
        if func:
            log.info(f"接口匹配成功！")
            return func
        elif func is None:
            log.error(f"接口匹配失败，找不到接口！")
            return None

    def handle_main_Q(self, task_id, api_code, req_cmd, resp_cmd, operate_result):
        try:
            AFN = api_code[0:2]
            Fn = api_code[2:4]
            func = self.get_func_Q(AFN, Fn)
            func(task_id, resp_cmd, operate_result)  # 查询参数，需要处理响应命令
        except Exception as e:
            log.error(f'查询参数发生错误：{e}', exc_info=True)



class HandleArgsS:  # 设置参数
    def __init__(self):
        pass

    def S_commu_para(self, task_id, req_cmd, operate_result):
        # 设置通信参数
        log.info(f'接口：设置插座启停')
        log.info(f'请求报文：{req_cmd}')
        log.info(f'操作结果：{operate_result}')
        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        heart_cycle = special_data['heart_cycle']
        up_cycle = special_data['up_cycle']
        delay_time = special_data['delay_time']
        terminal_address = req_cmd['address_region'].get('address_term_r')
        if operate_result == '0':
            # 更新参数表
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                heart_time=heart_cycle,
                uplink_interval=up_cycle,
                delay_time=delay_time,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'设置通信参数失败：不支持此功能')

        elif operate_result == '2':
            log.error(f'设置通信参数失败：设备忙')

        else:
            log.error(f'设置通信参数失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )


    def S_domain_port(self, task_id, req_cmd, operate_result):
        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        domian = special_data['domian']
        port = special_data['port']
        terminal_address = req_cmd['address_region'].get('address_term_r')
        if operate_result == '0':
            # 更新参数表
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                domian=domian,
                port=port,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'设置域名端口失败：不支持此功能')

        elif operate_result == '2':
            log.error(f'设置域名端口失败：设备忙')


        else:
            log.error(f'设置域名端口失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def S_power_threshold(self, task_id, req_cmd, operate_result):
        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        min_power = special_data['min_power']
        max_power = special_data['max_power']
        terminal_address = req_cmd['address_region'].get('address_term_r')
        if operate_result == '0':
            # 更新参数表
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                min_power=min_power,
                max_power=max_power,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'设置功率阈值失败：不支持此功能')

        elif operate_result == '2':
            log.error(f'设置功率阈值失败：设备忙')
        else:
            log.error(f'设置功率阈值失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    def S_settle_allocation(self, task_id, req_cmd, operate_result):
        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        Hourly_price = special_data['Hourly_price']
        Rate_duration = special_data['Rate_duration']
        terminal_address = req_cmd['address_region'].get('address_term_r')
        if operate_result == '0':
            # 更新参数表
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                Hourly_price=Hourly_price,
                Rate_duration=Rate_duration,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'设置结算配置失败：不支持此功能')

        elif operate_result == '2':
            log.error(f'设置结算配置失败：设备忙')
        else:
            log.error(f'设置结算配置失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )

    # def S_pile_status(self, task_id, req_cmd, operate_result):
    #     #充电桩启停：硬件缺失这个接口，不需要这个了
    #     req_cmd = json.loads(req_cmd)
    #     special_data = req_cmd['app_region'].get('Specific_data_detail')
    #     status = special_data['status']
    #     terminal_address = req_cmd['address_region'].get('address_term_r')
    #     if operate_result == '0':
    #         # 更新参数表
    #         SEqArgPrivate.objects.filter(terminal_address=terminal_address).update(
    #             status=status
    #         )
    #     elif operate_result == '1':
    #         log.error(f'设置功率阈值失败：不支持此功能')
    #
    #     elif operate_result == '2':
    #         log.error(f'设置功率阈值失败：设备忙')
    #     else:
    #         log.error(f'设置功率阈值失败：未知原因')
    #
    #     SCmdInfo.objects.filter(id=task_id).update(
    #         update_status='1'
    #     )

    @transaction.atomic()
    def S_socket_status(self, task_id, req_cmd, operate_result):  # 设置开启充电桩
        from app.utils.handle_order import HandleOrder
        handleorder = HandleOrder(log)

        log.info(f'接口：设置插座启停')
        log.info(f'请求报文：{req_cmd}')
        log.info(f'操作结果：{operate_result}')

        def get_elec_grads(order_num, fee_no):
            dt = datetime.datetime.now() - datetime.timedelta(days=30)
            order_grad_detail = SOrderFee2.objects.filter(order_id=order_num, fee_no=fee_no,
                                                          create_time__gte=dt).order_by('grads_no')
            return order_grad_detail

        def cal_grads_money(elec_grads, electricity_quantity):
            electricity_quantity = decimal.Decimal(electricity_quantity)
            # new_elec = electricity_quantity
            for item in elec_grads:
                use_money = 0.00
                all_fee = item.electric_price + item.service_fee  # 总费用为基础电费+服务费
                if electricity_quantity > item.electric_up:
                    use_money = all_fee * (item.electric_up - item.electric_down)
                elif item.electric_down < electricity_quantity <= item.electric_up:
                    use_money = all_fee * (electricity_quantity - item.electric_down)
                # 更新到费用详情表
                dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
                SOrderFee2.objects.filter(order_id=item.order_id, fee_no=item.fee_no, grads_no=item.grads_no,
                                          create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    use_money=use_money
                )

        def get_all_gards_money(order_num, fee_no):
            # 获取所有时段的金额
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            order_fee_detail = SOrderFee2.objects.filter(order_id=order_num, fee_no=fee_no, create_time__gte=dt)
            use_money_all = decimal.Decimal(0.00)
            for item in order_fee_detail:
                use_money_all = use_money_all + item.use_money
            return use_money_all

        def get_oa_open_id(user_id):
            """
            获取openid
            :param user_id:
            :return:
            """
            try:
                user_info = SUserInfo.objects.filter(user_id=user_id, state='0')[0]
                wx_open_id = user_info.wx_open_id
                xcx_open_id = user_info.xcx_open_id
                union_id = user_info.union_id
                return wx_open_id, xcx_open_id, union_id
            except Exception as e:
                log.error(f'获取open_id失败：{e}', exc_info=True)


        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        OrderNumber = special_data.get('OrderNumber')
        DurationOrAmount = special_data.get('DurationOrAmount')
        log.info(f'参数：{DurationOrAmount}')
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        # 查订单的计费规则
        order_info = SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt).exclude(state='9')
        if not order_info:
            SCmdInfo.objects.filter(id=task_id).update(
                update_status='1',
                remark='找不到相关订单'
            )
            return 
        user_id = order_info[0].user_id
        charge_type = order_info[0].charge_type
        type_map = {
            'auto': '充满自停',
            'money': '定金额充电',
            'time': '定时间充电',
            'elec': '定电量充电',
            'card': '刷卡充电'  #  加上防止报错，实际上电卡充电不会到这一步
        }
        charge_type = type_map[charge_type]
        eq_id = order_info[0].eq_id
        eq_port = order_info[0].eq_port
        if not user_id:
            log.error(f'该用户未注册小程序：{OrderNumber}')
        if operate_result == '0':
            if DurationOrAmount == '0000':  # 下发的指令是停止充电
                log.info(f'停止充电：{OrderNumber}')
                try:
                    handleorder.handle_order_stop(order_info, '达到停止条件或用户手动停止')
                    # terminal_address = order_info[0].term_address
                    # eq_port = order_info[0].eq_port
                    # fee_type = order_info[0].fee_type
                    # fee_no = order_info[0].fee_no
                    # pay_way = order_info[0].pay_way
                    # user_id = order_info[0].user_id
                    # charge_type = order_info[0].charge_type
                    # charge_money = order_info[0].charge_money
                    # use_electric = order_info[0].use_electric
                    # begin_time = order_info[0].begin_time
                    # end_time = datetime.datetime.now()
                    # use_time = end_time - begin_time
                    # if fee_type == '1':  # 时段收费
                    #     order_fee_detail = SOrderFee1.objects.filter(order_id=OrderNumber, fee_no=fee_no, create_time__gte=dt)
                    #     use_money_all = decimal.Decimal(0.00)
                    #     for item in order_fee_detail:
                    #         use_money_all = use_money_all + item.use_money
                    #     remark = ''
                    #     state = '2'
                    #     # 判断充电类型
                    #     if charge_type == 'auto' or charge_type == 'time' or charge_type == 'elec':
                    #         # 这三种模式不需要退钱
                    #         # 金额解冻
                    #         res1 = handleorder.unfreeze_money(user_id, unfreeze_money=1)
                    #         # 扣钱
                    #         res2 = handleorder.deduct_money(user_id, deduct_money=use_money_all)
                    #
                    #         remark = ''
                    #         state = '2'
                    #         if not (res1 and res2):
                    #             remark = '扣款出现错误'
                    #             state = '-1'
                    #     elif charge_type == 'money':
                    #         if charge_money > use_money_all:  # 实际使用金额小于用户所选金额，需要退款
                    #             # 判断支付方式
                    #             if pay_way == 'online':
                    #                 # 在线支付，需要退款
                    #                 return_money = charge_money - use_money_all  # 需要返还的金额
                    #                 handleorder.refund_money_online(charge_order=OrderNumber, refund_amount=return_money)
                    #             if pay_way == 'account':
                    #                 # 余额支付，无需退款，扣除实际使用金额即可
                    #                 # 解冻金额
                    #                 res1 = handleorder.unfreeze_money(user_id, unfreeze_money=charge_money)
                    #                 res2 = handleorder.deduct_money(user_id, deduct_money=use_money_all)
                    #
                    #                 if not (res1 and res2):
                    #                     remark = '扣款出现错误'
                    #                     state = '-1'
                    #         else:  # 实际金额大于等于用户所选金额
                    #             if pay_way == 'online':
                    #                 # 不需要扣款，不需要退款
                    #                 pass
                    #             if pay_way == 'account':
                    #                 # 余额支付，无需退款，扣除实际使用金额即可
                    #                 # 解冻金额
                    #                 res1 = handleorder.unfreeze_money(user_id, unfreeze_money=charge_money)
                    #                 res2 = handleorder.deduct_money(user_id, deduct_money=use_money_all)
                    #
                    #                 if not (res1 and res2):
                    #                     remark = '扣款出现错误'
                    #                     state = '-1'
                    #
                    #     SOrderInfo.objects.filter(order_id=OrderNumber).update(
                    #         use_money=use_money_all,
                    #         end_time=end_time,
                    #         use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                    #         end_type='2',
                    #         state=state,
                    #         remark=remark
                    #     )
                    # if fee_type == '2':
                    #     # 查询电量梯度
                    #     elec_grads = get_elec_grads(OrderNumber, fee_no)
                    #     # 从订单表中查当前使用电量
                    #
                    #     # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                    #     cal_grads_money(elec_grads, use_electric)
                    #     # 更新订单表
                    #     all_money = get_all_gards_money(OrderNumber, fee_no)
                    #     end_time = datetime.datetime.now()
                    #     use_time = end_time - begin_time
                    #
                    #     remark = ''
                    #     state = '2'
                    #     # 判断充电类型
                    #     if charge_type == 'auto' or charge_type == 'time' or charge_type == 'elec':
                    #         # 这三种模式不需要退钱
                    #         # 金额解冻
                    #         res1 = handleorder.unfreeze_money(user_id, unfreeze_money=1)
                    #         # 扣钱
                    #         res2 = handleorder.deduct_money(user_id, deduct_money=all_money)
                    #
                    #         remark = ''
                    #         state = '2'
                    #         if not (res1 and res2):
                    #             remark = '扣款出现错误'
                    #             state = '-1'
                    #     elif charge_type == 'money':
                    #         if charge_money > all_money:  # 实际使用金额小于用户所选金额，需要退款
                    #             # 判断支付方式
                    #             if pay_way == 'online':
                    #                 # 在线支付，需要退款
                    #                 return_money = charge_money - all_money  # 需要返还的金额
                    #                 handleorder.refund_money_online(charge_order=OrderNumber,
                    #                                                 refund_amount=return_money)
                    #             if pay_way == 'account':
                    #                 # 余额支付，无需退款，扣除实际使用金额即可
                    #                 # 解冻金额
                    #                 res1 = handleorder.unfreeze_money(user_id, unfreeze_money=charge_money)
                    #                 res2 = handleorder.deduct_money(user_id, deduct_money=all_money)
                    #
                    #                 if not (res1 and res2):
                    #                     remark = '扣款出现错误'
                    #                     state = '-1'
                    #         else:  # 实际金额大于等于用户所选金额
                    #             if pay_way == 'online':
                    #                 # 不需要扣款，不需要退款
                    #                 pass
                    #             if pay_way == 'account':
                    #                 # 余额支付，无需退款，扣除实际使用金额即可
                    #                 # 解冻金额
                    #                 res1 = handleorder.unfreeze_money(user_id, unfreeze_money=charge_money)
                    #                 res2 = handleorder.deduct_money(user_id, deduct_money=all_money)
                    #
                    #                 if not (res1 and res2):
                    #                     remark = '扣款出现错误'
                    #                     state = '-1'
                    #
                    #     SOrderInfo.objects.filter(order_id=OrderNumber).update(
                    #         use_money=all_money,
                    #         end_time=end_time,
                    #         use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                    #         end_type='2',
                    #         state=state,
                    #         remark=remark
                    #     )
                    #
                    # # 释放端口
                    # log.info(f'释放端口')
                    # SEqPort.objects.filter(terminal_address=terminal_address, eq_port=eq_port).update(
                    #     use_state='0'
                    # )
                except Exception as e:
                    log.error(f'停止充电发生错误：{e}', exc_info=True)
            else:
                begin_time = datetime.datetime.now()
                SOrderInfo.objects.filter(order_id=OrderNumber).update(
                    state='1',
                    begin_time=begin_time
                )
                # 发送模板消息
                if user_id: # 用户注册过小程序
                    log.info(f'发送充电开启消息')
                    wx_open_id, xcx_open_id, union_id = get_oa_open_id(user_id=user_id)
                    if wx_open_id: # 用户关注了公众号

                        data_start = {
                            "order_id": OrderNumber,
                            "begin_time": begin_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "charge_type": charge_type,
                            "eq_id": eq_id,
                            "eq_port": eq_port
                        }
                        log.info(f'发送的内容：{data_start}')
                        # wx_temp_msg.send_charge_start_notice(wx_open_id, data_start)

                        SWxTempMsg.objects.create(
                            user_id=user_id,
                            wx_open_id=wx_open_id,
                            xcx_open_id=xcx_open_id,
                            union_id=union_id,
                            msg_type='charge_open',
                            send_data=json.dumps(data_start),
                            create_time=datetime.datetime.now(),
                            state='0'
                        )

            SCmdInfo.objects.filter(id=task_id).update(
                update_status='1'
            )
        elif operate_result == '1':
            SOrderInfo.objects.filter(order_id=OrderNumber).update(
                state='-1',
                remark='通信错误：不支持该功能',
                begin_time=datetime.datetime.now()
            )
            SCmdInfo.objects.filter(id=task_id).update(
                update_status='1'
            )
        elif operate_result == '2':
            log.error(f'开启充电错误: 设备忙')
            SOrderInfo.objects.filter(order_id=OrderNumber).update(
                state='-1',
                remark='设备忙',
                begin_time=datetime.datetime.now()
            )
            SCmdInfo.objects.filter(id=task_id).update(
                update_status='1'
            )
        else:
            log.error(f'开启充电错误：未知原因')


    def S_QRcode(self, task_id, req_cmd, operate_result):
        req_cmd = json.loads(req_cmd)
        special_data = req_cmd['app_region'].get('Specific_data_detail')
        QR_data = special_data['QR_data']
        terminal_address = req_cmd['address_region'].get('address_term_r')
        if operate_result == '0':
            # 更新参数表
            SEqArgsPrivate.objects.filter(terminal_address=terminal_address).update(
                QR_code=QR_data,
                update_time=datetime.datetime.now()
            )
        elif operate_result == '1':
            log.error(f'设置二维码失败：不支持此功能')

        elif operate_result == '2':
            log.error(f'设置二维码失败：设备忙')
        else:
            log.error(f'设置二维码失败：未知原因')

        SCmdInfo.objects.filter(id=task_id).update(
            update_status='1'
        )


    def get_func_S(self, AFN, Fn):
        """
        匹配接口
        :param dict_data: 解包后的数据
        :return: 对应的接口
        对于服务器为主动站的情况，终端发过来的数据，还用原来的方式，通过api_func来返回
        这里只用来解析终端主动上报的数据
        """
        Function_mapping = {
            '04': {
                '01': self.S_commu_para,
                '02': self.S_domain_port,
                '17': self.S_power_threshold,
                '18': self.S_settle_allocation,
                # '19': self.S_pile_status,   # 硬件接口缺失
                '20': self.S_socket_status,
                '21': self.S_QRcode
            }
        }

        func = Function_mapping[AFN].get(Fn)
        if func:
            log.info(f"接口匹配成功！")
            return func
        elif func is None:
            log.error(f"接口匹配失败，找不到接口！", exc_info=True)
            return None

    def handle_main_S(self, task_id, api_code, req_cmd, resp_cmd, operate_result):
        try:
            AFN = api_code[0:2]
            Fn = api_code[2:4]
            func = self.get_func_S(AFN, Fn)
            func(task_id, req_cmd, operate_result)  # 设置参数，需要处理请求命令
        except Exception as e:
            log.error(f'设置参数发生错误：{e}', exc_info=True)


def get_task():
    handleQ = HandleArgsQ()
    handleS = HandleArgsS()
    # 找出命令表中，有响应、没执行更新的数据，每一条都是一个更新任务
    tasks = SCmdInfo.objects.filter(resp_status='1', update_status='0')
    # log.info(tasks.count())
    for task in tasks:
        log.info(f'@@@@@@@@@@@@@@@@@@@@@@开始处理报文@@@@@@@@@@@@@@@@@@@@@@')
        api_code = task.api_code
        req_cmd = task.req_cmd
        resp_cmd = task.resp_cmd
        operate_result = task.operate_result
        task_id = task.id
        log.info(f'任务id：{task_id}')
        if api_code[0:2] == '04':  # 设置参数
            log.info(f'设置参数：{operate_result}, 详情：{req_cmd}')
            handleS.handle_main_S(task_id, api_code, req_cmd, resp_cmd, operate_result)
        if api_code[0:2] == '0A':  # 查询参数
            log.info(f'查询参数：{operate_result}, 详情：{resp_cmd}')
            handleQ.handle_main_Q(task_id, api_code, req_cmd, resp_cmd, operate_result)
        log.info(f'@@@@@@@@@@@@@@@@@@@@@@处理结束@@@@@@@@@@@@@@@@@@@@@@')

def main():

    while True:
        time.sleep(0.1)
        get_task()


if __name__ == '__main__':
    main()