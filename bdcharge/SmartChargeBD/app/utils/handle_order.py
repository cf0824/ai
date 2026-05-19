#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_order.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/1/11 10:10 
@Description :
'''
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()
import datetime
import decimal
import json

from django.db import transaction
from app.command.hardware_api import HardwareApi

from app.models import *
from app.utils import wx_temp_msg
from SmartChargeBD.settings import POWER_INTERVAL_TIME


class HandleOrder:
    def __init__(self, log):
        self.log = log
        self.hardwareapi = HardwareApi()

    def stop_charge(self, terminal_address, SocketNumber, OrderNumber):
        self.log.info(f'停止充电：{OrderNumber}')
        special_data = {
            'SocketNumber': SocketNumber,
            'OrderNumber': OrderNumber,
            'electrovalence': '0050',  # 这个电价没用，写死
            'type': '01',  # 00：金额，01：时间
            'DurationOrAmount': '0000'  # 为0，表示停止充电
        }
        self.hardwareapi.set_socket_status(terminal_address, special_data)


    def get_fee_type(self, order_num):
        '''
        根据订单号，获取该订单所使用的计费类型、计费规则编号
        :param order_num:
        :return:
        '''
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).exclude(state='9')
        fee_type = order_info[0].fee_type
        fee_no = order_info[0].fee_no
        return fee_type, fee_no

    def get_order_info(self, order_num):
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).exclude(state='9')
        return order_info[0]

    def get_fee_struct(self, fee_type, fee_no):
        '''
        获取时段费用结构
        :param order_num:
        :return:
        目前不需要
        '''
        if fee_type==1:  # 按时段
            fee_time_frame = SFeeStandard1.objects.filter(fee_no=fee_no)  # 费用时段
            # fee_detail = SFeeStandard1.objects.filter(fee_no=fee_no)

            fee_dict = {}
            count = fee_time_frame.count()
            i = 0
            for item in fee_time_frame:
                i = i + 1
                fee_no = item.fee_no
                begin_time = item.begin_time
                end_time = item.end_time
                electric_price = item.electric_price
                service_fee = item.service_fee
                fee_dict[i] = {
                    'fee_no': fee_no,
                    'begin_time': begin_time,
                    'end_time': end_time,
                    'electric_price': electric_price,
                    'service_fee': service_fee
                }
                print(fee_dict)

            print(fee_dict)


    def create_fee_detail(self, site_id, order_num, fee_type, fee_no):
        """
        根据计费类型，决定是否需要创建订单时段费用详情表
        :param order_num:
        :return:
        """
        # 获取计费类型
        # fee_type, fee_no = self.get_fee_type(order_num)
        if fee_type=='1':
            fee_time_frame = SFeeStandard1.objects.filter(site_id=site_id, fee_no=fee_no)  # 费用时段
            self.log.info(f'订单：{order_num} 的费用时段为：{fee_time_frame}, 共有{fee_time_frame.count()}个时段')
            for item in fee_time_frame:
                fee_no = item.fee_no
                time_frame_no = item.time_frame_no
                standard_name = item.standard_name
                begin_time = item.begin_time
                end_time = item.end_time
                electric_price = item.electric_price
                service_fee = item.service_fee
                SOrderFee1.objects.create(
                    order_id=order_num,
                    fee_no=fee_no,
                    time_frame_no=time_frame_no,
                    standard_name=standard_name,
                    begin_time=begin_time,
                    end_time=end_time,
                    use_electric=0.00,
                    use_money=0.00,
                    electric_price=electric_price,
                    service_fee=service_fee,
                    cal_status='0',
                    create_time=datetime.datetime.now()
                )
        elif fee_type=='2':
            fee_grads = SFeeStandard2.objects.filter(site_id=site_id, fee_no=fee_no)
            self.log.info(f'订单：{order_num} 的电量梯度为：{fee_grads}, 共有{fee_grads.count()}个时段')
            for item in fee_grads:
                fee_no = item.fee_no
                grads_no = item.grads_no
                standard_name = item.standard_name
                electric_down = item.electric_down
                electric_up = item.electric_up
                electric_price = item.electric_price
                service_fee = item.service_fee
                SOrderFee2.objects.create(
                    order_id=order_num,
                    fee_no=fee_no,
                    grads_no=grads_no,
                    standard_name=standard_name,
                    electric_down=electric_down,
                    electric_up=electric_up,
                    use_electric=0.00,
                    use_money=0.00,
                    electric_price=electric_price,
                    service_fee=service_fee,
                    create_time=datetime.datetime.now()
                )





    def cal_fee1(self):
        '''暂时没用
        计算订单费用：
        1）按时段收费
        2）按梯度收费
        :return:
        '''
        pass

    def update_electric(self, order_num, electricity_quantity, fee_type, fee_no):
        SOrderInfo.objects.filter(order_id=order_num).update(
            use_electric=electricity_quantity
        )

    def is_time_in_range(self, start, end, check_time):
        """
        判断一个时间点是否在一个时间段内

        :param start: 时间段开始时间 (datetime 对象)
        :param end: 时间段结束时间 (datetime 对象)
        :param check_time: 要检查的时间点 (datetime 对象)
        :return: 如果 check_time 在 [start, end) 范围内返回 True，否则返回 False
        """
        if start <= end:
            return start <= check_time < end
        else:
            # 处理跨零点的情况，例如 [22:00, 06:00)
            return start <= check_time or check_time < end

    def get_now_time_frame(self, order_num, nowtime):
        now_time = datetime.time(nowtime.hour, nowtime.minute, nowtime.second)
        fee_struct = SOrderFee1.objects.filter(order_id=order_num)
        for item in fee_struct:
            # print(item.end_time)
            # print(type(item.end_time))
            if self.is_time_in_range(item.begin_time, item.end_time, now_time):
                self.log.info(f'item:{item.time_frame_no}')
                now_time_frame_no = item.time_frame_no

                # return now_time_frame_no
                return item
    def get_last_time_frame(self, order_num, fee_no, time_frame_no):  # 获取当前时间段的上个时间段
        '''
        # 获取当前时间段的上个时间段
        :param order_num: 订单号
        :param fee_no: 收费编号
        :param time_frame_no: 当前具体时间段的编号
        :return:
        '''
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        # # 当前的时段通过时段编号查询
        # now_time_frame = SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=time_frame_no,
        #                                            create_time__gte=dt)
        # self.log.info(now_time_frame)
        # now_time_frame_endtime = now_time_frame.first().begin_time
        # # 上一个时段通过结束时间查询
        # last_time_frame = SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, end_time=now_time_frame_endtime,
        #                                             create_time__gte=dt)
        # self.log.info(type(last_time_frame[0]))
        # 2025.05.19更新，以上方法因为会导致59错误，采用新的方法
        time_frame_len = SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, create_time__gte=dt).count()

        time_frame_no = int(time_frame_no)
        def last(no, len):
            last_no = (no - 1 + len) % len
            if last_no == 0:
                return len
            return last_no

        last_time_frame_no = last(time_frame_no, time_frame_len)
        last_time_frame = SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=last_time_frame_no,
                                                    create_time__gte=dt)

        return last_time_frame[0]

    def update_order_fee(self, electricity_status, order_num, electricity_quantity, fee_type, fee_no):
        # 暂时没用
        if fee_type == '1':  # 按时段
            now_time = datetime.datetime.now()
            use_money = self.cal_fee1()
            if electricity_status == '1':  # 正在充电中
                SOrderFee1.objects.filter(order_id=order_num).update(
                    use_electric=electricity_quantity,
                    use_money=use_money,
                    cal_status='1'
                )

            if electricity_status == '2':  # 结束充电
                SOrderFee1.objects.filter(order_id=order_num).update(
                    use_electric=electricity_quantity,
                    use_money=use_money,
                    cal_status='2'
                )

    def get_all_time_money(self, order_num, fee_no):
        # 获取所有时段的金额
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        order_fee_detail = SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, create_time__gte=dt)
        use_money_all = decimal.Decimal(0.00)
        for item in order_fee_detail:
            use_money_all = use_money_all + item.use_money
        return use_money_all

    def get_all_gards_money(self, order_num, fee_no):
        # 获取所有时段的金额
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        order_fee_detail = SOrderFee2.objects.filter(order_id=order_num, fee_no=fee_no, create_time__gte=dt)
        use_money_all = decimal.Decimal(0.00)
        for item in order_fee_detail:
            use_money_all = use_money_all + item.use_money
        return use_money_all

    def get_elec_grads(self, order_num, fee_no):
        dt = datetime.datetime.now() - datetime.timedelta(days=30)
        order_grad_detail = SOrderFee2.objects.filter(order_id=order_num, fee_no=fee_no, create_time__gte=dt).order_by('grads_no')
        return order_grad_detail

    def cal_grads_money(self, elec_grads, electricity_quantity):
        electricity_quantity = decimal.Decimal(electricity_quantity)
        self.log.info(f'当前使用电量：{electricity_quantity}')
        # new_elec = electricity_quantity
        for item in elec_grads:
            self.log.info(f'梯度：{item.grads_no}')
            self.log.info(f'电量区间：[{item.electric_down}, {item.electric_up}]')
            use_money = 0.00
            all_fee = item.electric_price + item.service_fee  # 总费用为基础电费+服务费
            if electricity_quantity > item.electric_up:
                use_money = all_fee * (item.electric_up - item.electric_down)
            elif item.electric_down < electricity_quantity <= item.electric_up:
                use_money = all_fee * (electricity_quantity - item.electric_down)
            # 更新到费用详情表
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            SOrderFee2.objects.filter(order_id=item.order_id, fee_no=item.fee_no, grads_no=item.grads_no, create_time__gte=dt).update(
                use_electric=electricity_quantity,
                use_money=use_money
            )

    def add_power_info(self, order_num, power):
        """
        向功率表中插入功率信息
        :param order_num:
        :return:
        """
        power_info = SOrderPower.objects.filter(order_id=order_num).order_by('-create_time').first()
        if power_info:
            create_time = power_info.create_time
            now = datetime.datetime.now()
            if int((now - create_time).total_seconds()) >= POWER_INTERVAL_TIME:
                self.log.info(f'间隔超过{POWER_INTERVAL_TIME}秒')
                SOrderPower.objects.create(
                    order_id=order_num,
                    power=power,
                    power_time=datetime.datetime.now(),
                    create_time=datetime.datetime.now()
                )
            else:
                self.log.info(f'间隔小于{POWER_INTERVAL_TIME}秒')
        if not power_info:
            SOrderPower.objects.create(
                order_id=order_num,
                power=power,
                power_time=datetime.datetime.now(),
                create_time=datetime.datetime.now()
            )

    def handle_order_auto(self, user_id, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity, begin_time):
        '''
        处理充满自停
        :param electricity_status:
        :param order_num:
        :return:
        '''
        try:
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            # 1）获取计费规则
            now_time = datetime.datetime.now()
            fee_type, fee_no = self.get_fee_type(order_num)
            # 订单信息
            order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)
            eq_id = order_info[0].eq_id

            if fee_type == '1':  # 时段收费

                # 判断充电桩上报的充电状态

                now_time_frame = self.get_now_time_frame(order_num, now_time)  # 获取当前时段
                now_time_frame_no = now_time_frame.time_frame_no  # 当前时段的编号  （#todu这里可以优化一下,给下边传入当前时段的开始时间，少查一次数据库）
                last_time_frame = self.get_last_time_frame(order_num, fee_no, now_time_frame_no)
                # 给上个时段状态设置为'已计算'
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=last_time_frame.time_frame_no, create_time__gte=dt).update(
                    cal_status='2'
                )
                # 获取上个时段的电量
                last_time_elec = last_time_frame.use_electric
                self.log.info(f'上个时段的电量：{last_time_elec}')
                now_time_elec = decimal.Decimal(electricity_quantity) - last_time_elec
                # 计算当前时段的金额
                # 获取当前时段的基础电费 + 服务费
                electric_price = now_time_frame.electric_price
                service_fee = now_time_frame.service_fee
                final_fee = electric_price + service_fee
                now_time_use_money = final_fee * now_time_elec
                self.log.info(f'1')
                # 把当前费用更新到费用明细表里
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no, create_time__gte=dt).update(
                    cal_status='1',  # 计算中
                    use_electric=now_time_elec,
                    use_money=now_time_use_money
                )

                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                self.log.info(f'用电成本：{elec_cost}')
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )

                # 添加功率信息
                self.add_power_info(order_num, power)

                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )

                if electricity_status == '02':
                    self.log.info(f'订单结束：{order_num}')
                    # 查询订单状态
                    order_state = SOrderInfo.objects.get(order_id=order_num, create_time__gte=dt).state
                    if order_state == '2':
                        self.log.info(f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息')
                        SErrorRecord.objects.create(
                            remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                            create_time=datetime.datetime.now()
                        )
                        return
                    if order_state == '-1':
                        self.log.info(f'订单状态为-1，充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息')
                        SErrorRecord.objects.create(
                            remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                            create_time=datetime.datetime.now()
                        )
                        return


                    SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no, create_time__gte=dt).update(
                        cal_status='2'  # 计算完成
                    )
                    # 更新订单表
                    # 获取所有时段金额
                    all_money = self.get_all_time_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 金额解冻
                    # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录
                        self.add_account_record(user_id, order_id=order_num, money=deduct_account, remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney, remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'

                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )
                    # 释放端口
                    self.log.info(f'释放端口')
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
            elif fee_type=='2':  # 按电量梯度收费
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                if electricity_status == '01':  # 还在充电中，不需要做其他事情
                    pass

                elif electricity_status == '02':  # 结束充电，根据电量判断使用金额
                    self.log.info(f'订单结束：{order_num}')
                    # 查询电量梯度
                    elec_grads = self.get_elec_grads(order_num, fee_no)
                    # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                    self.cal_grads_money(elec_grads, electricity_quantity)
                    # 更新订单表
                    all_money = self.get_all_gards_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 金额解冻
                    # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录
                        self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'

                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )

                    # 释放端口
                    self.log.info(f'释放端口')
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
        except Exception as e:
            self.log.error(f'处理插座上报信息出现错误：{e}', exc_info=True)

#---------------------------------------------按时间充电-----------------------------------------------
    def handle_order_time(self, order_num, fee_no):
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        # 1）获取计费规则
        now_time = datetime.datetime.now()
        fee_type, fee_no = self.get_fee_type(order_num)

        if fee_type == '1':  # 时段收费
            pass

#---------------------------------------------按金额充电-----------------------------------------------
    def handle_order_money(self, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity, begin_time):
        '''
        处理按金额充电
        :param electricity_status:
        :param order_num:
        :return:
        '''
        try:
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            # 1）获取计费规则
            now_time = datetime.datetime.now()
            fee_type, fee_no = self.get_fee_type(order_num)
            # 订单信息
            order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)
            charge_money = order_info[0].charge_money
            pay_way = order_info[0].pay_way
            user_id = order_info[0].user_id
            eq_id = order_info[0].eq_id

            if fee_type == '1':  # 时段收费

                # 判断充电桩上报的充电状态

                now_time_frame = self.get_now_time_frame(order_num, now_time)  # 获取当前时段
                now_time_frame_no = now_time_frame.time_frame_no  # 当前时段的编号  （#todu这里可以优化一下,给下边传入当前时段的开始时间，少查一次数据库）
                last_time_frame = self.get_last_time_frame(order_num, fee_no, now_time_frame_no)
                # 给上个时段状态设置为'已计算'
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=last_time_frame.time_frame_no,
                                          create_time__gte=dt).update(
                    cal_status='2'
                )
                # 获取上个时段的电量
                last_time_elec = last_time_frame.use_electric
                self.log.info(f'上个时段的电量：{last_time_elec}')
                now_time_elec = decimal.Decimal(electricity_quantity) - last_time_elec
                # 计算当前时段的金额
                # 获取当前时段的基础电费 + 服务费
                electric_price = now_time_frame.electric_price
                service_fee = now_time_frame.service_fee
                final_fee = electric_price + service_fee
                now_time_use_money = final_fee * now_time_elec
                # 把当前费用更新到费用明细表里
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no,
                                          create_time__gte=dt).update(
                    cal_status='1',  # 计算中
                    use_electric=now_time_elec,
                    use_money=now_time_use_money
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                if electricity_status == '02':
                    # 充电桩主动结束
                    self.log.info(f'订单结束：{order_num}')
                    SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no,
                                              create_time__gte=dt).update(
                        cal_status='2'  # 计算完成
                    )
                    # 更新订单表
                    # 获取所有时段金额
                    all_money = self.get_all_time_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time


                    # charge_money = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].charge_money
                    remark = ''
                    state = '2'
                    if charge_money > all_money:  # 实际使用金额小于用户所选金额，需要退款
                        return_money = charge_money - all_money  # 需要返还的金额
                        # 判断支付方式
                        # pay_way = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].pay_way
                        if pay_way == 'online':
                            # 在线支付，需要退款
                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                online_money=all_money,
                                update_time=datetime.datetime.now()
                            )

                            SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                return_money=return_money
                            )
                            self.refund_money_online(charge_order=order_num, refund_amount=return_money, total_money=charge_money)
                            if all_money > decimal.Decimal(0.00):
                                self.wx_dis_profit(charge_order=order_num, use_money_all=all_money)
                        if pay_way == 'account':
                            # 余额支付，无需退款，扣除实际使用金额即可

                            # 金额解冻
                            # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                            # 扣钱
                            res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )
                            if res2:
                                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                    return_money=return_money,
                                    refund_state='1'
                                )

                            if res2:
                                # 创建消费记录
                                self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                        remark='充电花费-基本余额')

                                self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                        remark='充电花费-赠送余额')

                            remark = ''
                            state = '2'
                            if not (res2):
                                remark = '扣款出现错误'
                                state = '-1'



                    else:  # 实际金额大于等于用户所选金额
                        # pay_way = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].pay_way
                        if pay_way == 'online':
                            # 不需要扣款，不需要退款
                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                online_money=charge_money,
                                update_time=datetime.datetime.now()
                            )

                        if pay_way == 'account':
                            # 余额支付，无需退款，扣除实际使用金额即可
                            # 解冻金额
                            # 扣钱
                            res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )

                            if res2:
                                # 创建消费记录
                                self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                        remark='充电花费-基本余额')

                                self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                        remark='充电花费-赠送余额')

                            remark = ''
                            state = '2'
                            if not (res2):
                                remark = '扣款出现错误'
                                state = '-1'


                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        state=state,
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )
                    # 释放端口
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
                # 判断是否达到结束条件
                all_money = self.get_all_time_money(order_num, fee_no)  # 当前所有时段的金额
                charge_money = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].charge_money
                if all_money >= charge_money:
                    self.stop_charge(terminal_address, socket_no, order_num)

            elif fee_type == '2':  # 按电量梯度收费
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                # 查询电量梯度
                elec_grads = self.get_elec_grads(order_num, fee_no)
                # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                self.cal_grads_money(elec_grads, electricity_quantity)
                # 更新订单表
                all_money = self.get_all_gards_money(order_num, fee_no)
                charge_money = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].charge_money
                if all_money >= charge_money:
                    self.stop_charge(terminal_address, socket_no, order_num)

                if electricity_status == '01':  # 还在充电中，不需要做其他事情
                    pass

                elif electricity_status == '02':  # 结束充电，根据电量判断使用金额
                    self.log.info(f'订单结束：{order_num}')
                    # 查询电量梯度
                    # elec_grads = self.get_elec_grads(order_num, fee_no)
                    # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                    # self.cal_grads_money(elec_grads, electricity_quantity)
                    # 更新订单表
                    # all_money = self.get_all_gards_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # charge_money = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].charge_money
                    remark = ''
                    state = '2'
                    if charge_money > all_money:  # 实际使用金额小于用户所选金额，需要退款
                        return_money = charge_money - all_money  # 需要返还的金额
                        # 判断支付方式
                        # pay_way = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].pay_way
                        if pay_way == 'online':
                            # 在线支付，需要退款
                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                online_money=all_money,
                                update_time=datetime.datetime.now()
                            )

                            SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                return_money=return_money
                            )
                            self.refund_money_online(charge_order=order_num, refund_amount=return_money, total_money=charge_money)
                            if all_money > decimal.Decimal(0.00):
                                self.wx_dis_profit(charge_order=order_num, use_money_all=all_money)
                        if pay_way == 'account':
                            # 余额支付，无需退款，扣除实际使用金额即可
                            # 扣钱
                            res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                            SOrderUseMoney.objects.filter(order_id=order_num).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )

                            if res2:
                                # 创建消费记录
                                self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                        remark='充电花费-基本余额')

                                self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                        remark='充电花费-赠送余额')

                            if res2:
                                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                    return_money=return_money,
                                    refund_state='1'
                                )

                            remark = ''
                            state = '2'
                            if not (res2):
                                remark = '扣款出现错误'
                                state = '-1'


                    else:  # 实际金额大于等于用户所选金额
                        # pay_way = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0].pay_way
                        if pay_way == 'online':
                            # 不需要扣款，不需要退款
                            SOrderUseMoney.objects.filter(order_id=order_num, create_time__gte=dt).update(
                                online_money=charge_money,
                                update_time=datetime.datetime.now()
                            )
                        if pay_way == 'account':
                            # 余额支付，无需退款，扣除实际使用金额即可

                            # 扣钱
                            res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                            SOrderUseMoney.objects.filter(order_id=order_num).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )

                            if res2:
                                # 创建消费记录
                                self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                        remark='充电花费-基本余额')

                                self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                        remark='充电花费-赠送余额')

                            remark = ''
                            state = '2'
                            if not (res2):
                                remark = '扣款出现错误'
                                state = '-1'




                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )
                    # 释放端口
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
        except Exception as e:
            self.log.error(f'处理插座上报信息出现错误：{e}', exc_info=True)

    def handle_order_elec(self, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity, begin_time):
        '''
        处理按电量充电
        :param electricity_status:
        :param order_num:
        :return:
        '''
        try:
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            # 1）获取计费规则
            now_time = datetime.datetime.now()
            fee_type, fee_no = self.get_fee_type(order_num)

            order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)
            charge_money = order_info[0].charge_money
            pay_way = order_info[0].pay_way
            user_id = order_info[0].user_id
            eq_id = order_info[0].eq_id

            if fee_type == '1':  # 时段收费

                # 判断充电桩上报的充电状态

                now_time_frame = self.get_now_time_frame(order_num, now_time)  # 获取当前时段
                now_time_frame_no = now_time_frame.time_frame_no  # 当前时段的编号  （#todu这里可以优化一下,给下边传入当前时段的开始时间，少查一次数据库）
                last_time_frame = self.get_last_time_frame(order_num, fee_no, now_time_frame_no)
                # 给上个时段状态设置为'已计算'
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=last_time_frame.time_frame_no,
                                          create_time__gte=dt).update(
                    cal_status='2'
                )
                # 获取上个时段的电量
                last_time_elec = last_time_frame.use_electric
                self.log.info(f'上个时段的电量：{last_time_elec}')
                now_time_elec = decimal.Decimal(electricity_quantity) - last_time_elec
                # 计算当前时段的金额
                # 获取当前时段的基础电费 + 服务费
                electric_price = now_time_frame.electric_price
                service_fee = now_time_frame.service_fee
                final_fee = electric_price + service_fee
                now_time_use_money = final_fee * now_time_elec
                # 把当前费用更新到费用明细表里
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no,
                                          create_time__gte=dt).update(
                    cal_status='1',  # 计算中
                    use_electric=now_time_elec,
                    use_money=now_time_use_money
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                if electricity_status == '02':
                    # 充电桩主动结束
                    self.log.info(f'订单结束：{order_num}')
                    SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no,
                                              create_time__gte=dt).update(
                        cal_status='2'  # 计算完成
                    )
                    # 更新订单表
                    # 获取所有时段金额
                    all_money = self.get_all_time_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录
                        self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'



                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )

                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )

                    # 释放端口
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
                # 判断是否达到结束条件
                # all_money = self.get_all_time_money(order_num, fee_no)  # 当前所有时段的金额
                order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0]
                charge_electric = order_info.charge_electric
                use_electric = order_info.use_electric
                if use_electric >= charge_electric:
                    self.stop_charge(terminal_address, socket_no, order_num)

            elif fee_type == '2':  # 按电量梯度收费
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)[0]
                charge_electric = order_info.charge_electric
                use_electric = order_info.use_electric
                if use_electric >= charge_electric:
                    self.stop_charge(terminal_address, socket_no, order_num)
                if electricity_status == '01':  # 还在充电中，不需要做其他事情
                    pass

                elif electricity_status == '02':  # 结束充电，根据电量判断使用金额
                    self.log.info(f'订单结束：{order_num}')
                    # 查询电量梯度
                    elec_grads = self.get_elec_grads(order_num, fee_no)
                    # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                    self.cal_grads_money(elec_grads, electricity_quantity)
                    # 更新订单表
                    all_money = self.get_all_gards_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录
                        self.add_account_record(user_id, order_id=order_num, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=order_num, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'


                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    if user_id:  # 用户注册过小程序
                        self.log.info(f'发送充电结束消息')
                        wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                        if wx_open_id:  # 用户关注了公众号
                            data_stop = {
                                'order_id': order_num,
                                'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'use_money': f'{all_money}元',
                                'use_electric': str(electricity_quantity)
                            }
                            self.log.info(f'发送的内容：{data_stop}')
                            # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                            SWxTempMsg.objects.create(
                                user_id=user_id,
                                wx_open_id=wx_open_id,
                                xcx_open_id=xcx_open_id,
                                union_id=union_id,
                                msg_type='charge_end',
                                send_data=json.dumps(data_stop),
                                create_time=datetime.datetime.now(),
                                state='0'
                            )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )
                    # 释放端口
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )


        except Exception as e:
            self.log.error(f'处理插座上报信息出现错误：{e}', exc_info=True)




    def handle_order_card(self, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity, begin_time):
        '''
        处理刷卡充电
        :param electricity_status:
        :param order_num:
        :return:
        '''
        try:
            dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
            # 1）获取计费规则
            now_time = datetime.datetime.now()
            fee_type, fee_no = self.get_fee_type(order_num)
            # 订单信息
            order_info = SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt)
            eq_id = order_info[0].eq_id
            card_num = order_info[0].card_num

            if fee_type == '1':  # 时段收费

                # 判断充电桩上报的充电状态

                now_time_frame = self.get_now_time_frame(order_num, now_time)  # 获取当前时段
                now_time_frame_no = now_time_frame.time_frame_no  # 当前时段的编号  （#todu这里可以优化一下,给下边传入当前时段的开始时间，少查一次数据库）
                last_time_frame = self.get_last_time_frame(order_num, fee_no, now_time_frame_no)
                # 给上个时段状态设置为'已计算'
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=last_time_frame.time_frame_no, create_time__gte=dt).update(
                    cal_status='2'
                )
                # 获取上个时段的电量
                last_time_elec = last_time_frame.use_electric
                self.log.info(f'上个时段的电量：{last_time_elec}')
                now_time_elec = decimal.Decimal(electricity_quantity) - last_time_elec
                # 计算当前时段的金额
                # 获取当前时段的基础电费 + 服务费
                electric_price = now_time_frame.electric_price
                service_fee = now_time_frame.service_fee
                final_fee = electric_price + service_fee
                now_time_use_money = final_fee * now_time_elec
                self.log.info(f'1')
                # 把当前费用更新到费用明细表里
                SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no, create_time__gte=dt).update(
                    cal_status='1',  # 计算中
                    use_electric=now_time_elec,
                    use_money=now_time_use_money
                )

                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                self.log.info(f'用电成本：{elec_cost}')
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )

                # 添加功率信息
                self.add_power_info(order_num, power)

                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )

                if electricity_status == '02':
                    self.log.info(f'订单结束：{order_num}')
                    # 查询订单状态
                    order_state = SOrderInfo.objects.get(order_id=order_num, create_time__gte=dt).state
                    if order_state == '2':
                        self.log.info(f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息')
                        SErrorRecord.objects.create(
                            remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                            create_time=datetime.datetime.now()
                        )
                        return
                    if order_state == '-1':
                        self.log.info(f'订单状态为-1，充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息')
                        SErrorRecord.objects.create(
                            remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                            create_time=datetime.datetime.now()
                        )
                        return


                    SOrderFee1.objects.filter(order_id=order_num, fee_no=fee_no, time_frame_no=now_time_frame_no, create_time__gte=dt).update(
                        cal_status='2'  # 计算完成
                    )
                    # 更新订单表
                    # 获取所有时段金额
                    all_money = self.get_all_time_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 金额解冻
                    # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money_card(card_num=card_num, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录card_num, order_id, money, remark
                        self.add_account_record_card(card_num, order_id=order_num, money=deduct_account, remark='充电花费-基本余额')

                        self.add_account_record_card(card_num, order_id=order_num, money=duduct_giftmoney, remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'

                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息
                    # if user_id:  # 用户注册过小程序
                    #     self.log.info(f'发送充电结束消息')
                    #     wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                    #     if wx_open_id:  # 用户关注了公众号
                    #         data_stop = {
                    #             'order_id': order_num,
                    #             'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                    #             'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    #             'use_money': f'{all_money}元',
                    #             'use_electric': str(electricity_quantity)
                    #         }
                    #         self.log.info(f'发送的内容：{data_stop}')
                    #         # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)
                    #
                    #         SWxTempMsg.objects.create(
                    #             user_id=user_id,
                    #             wx_open_id=wx_open_id,
                    #             xcx_open_id=xcx_open_id,
                    #             union_id=union_id,
                    #             msg_type='charge_end',
                    #             send_data=json.dumps(data_stop),
                    #             create_time=datetime.datetime.now(),
                    #             state='0'
                    #         )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )
                    # 释放端口
                    self.log.info(f'释放端口')
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
                    self.log.info(f'释放电卡')
                    SCardsInfo.objects.filter(card_num=card_num).update(
                        use_state='0'
                    )
            elif fee_type=='2':  # 按电量梯度收费
                # 添加功率信息
                self.add_power_info(order_num, power)
                # 更新插座当前功率
                SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                    power_time=datetime.datetime.now(),
                    power=power
                )
                # 计算用电成本
                elec_cost = self.cal_elec_cost(eq_id, electricity_quantity)
                # 订单表中更新电量
                SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                    use_electric=electricity_quantity,
                    elec_cost=elec_cost
                )
                if electricity_status == '01':  # 还在充电中，不需要做其他事情
                    pass

                elif electricity_status == '02':  # 结束充电，根据电量判断使用金额
                    self.log.info(f'订单结束：{order_num}')
                    # 查询电量梯度
                    elec_grads = self.get_elec_grads(order_num, fee_no)
                    # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                    self.cal_grads_money(elec_grads, electricity_quantity)
                    # 更新订单表
                    all_money = self.get_all_gards_money(order_num, fee_no)
                    end_time = datetime.datetime.now()
                    use_time = end_time - begin_time

                    # 金额解冻
                    # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                    # 扣钱
                    res2, deduct_account, duduct_giftmoney = self.deduct_money_card(card_num=card_num, deduct_money=all_money)

                    SOrderUseMoney.objects.filter(order_id=order_num).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )

                    if res2:
                        # 创建消费记录
                        self.add_account_record_card(card_num, order_id=order_num, money=deduct_account,
                                                     remark='充电花费-基本余额')

                        self.add_account_record_card(card_num, order_id=order_num, money=duduct_giftmoney,
                                                     remark='充电花费-赠送余额')

                    remark = ''
                    state = '2'
                    if not res2:
                        remark = '扣款出现错误'
                        state = '-1'

                    SOrderInfo.objects.filter(order_id=order_num, create_time__gte=dt).update(
                        use_money=all_money,
                        end_time=end_time,
                        end_type='1',
                        use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        state=state,
                        remark=remark,
                        end_reason='已充满'
                    )
                    # 分账
                    self.dis_profit(order_id=order_num, use_money=all_money, eq_id=eq_id)
                    # 发送充电结束消息   电卡不发送
                    # if user_id:  # 用户注册过小程序
                    #     self.log.info(f'发送充电结束消息')
                    #     wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                    #     if wx_open_id:  # 用户关注了公众号
                    #         data_stop = {
                    #             'order_id': order_num,
                    #             'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                    #             'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    #             'use_money': f'{all_money}元',
                    #             'use_electric': str(electricity_quantity)
                    #         }
                    #         self.log.info(f'发送的内容：{data_stop}')
                    #         # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)
                    #
                    #         SWxTempMsg.objects.create(
                    #             user_id=user_id,
                    #             wx_open_id=wx_open_id,
                    #             xcx_open_id=xcx_open_id,
                    #             union_id=union_id,
                    #             msg_type='charge_end',
                    #             send_data=json.dumps(data_stop),
                    #             create_time=datetime.datetime.now(),
                    #             state='0'
                    #         )
                    # 更新插座当前功率
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        power_time=datetime.datetime.now(),
                        power=0
                    )

                    # 释放端口
                    self.log.info(f'释放端口')
                    SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no).update(
                        use_state='0'
                    )
                    self.log.info(f'释放电卡')
                    SCardsInfo.objects.filter(card_num=card_num).update(
                        use_state='0'
                    )
        except Exception as e:
            self.log.error(f'处理插座上报信息出现错误：{e}', exc_info=True)
    @transaction.atomic()
    def update_order(self, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity):
        '''
        充电桩上报插座状态，这里对插座的订单进行更新（包括：更新功率、电量、是否达到充电结束的条件）
        充电结束：
        1）按电量充电：电量达到预设电量
        2）按金额充电：根据电量换算出金额
        :param electricity_status: 用电状态：0起始，1充电中，2结束充电，3未充上电
        :param order_num: 订单号
        :param power: 功率
        :param electricity_quantity:  电量
        :return:
        '''
        try:
            # 1)获取该订单的充电类型，接下来的所有操作，都基于充电类型开展
            order_info = self.get_order_info(order_num)
            # charge_type = SOrderInfo.objects.filter(order_id=order_num)
            # charge_type = charge_type[0].charge_type
            charge_type = order_info.charge_type
            begin_time = order_info.begin_time
            user_id = order_info.user_id
            order_state = order_info.state



            if order_state == '2':
                self.log.info(f'充电桩[{terminal_address}]重复上送订单[{order_num}]状态信息：{electricity_status}')
                SErrorRecord.objects.create(
                    remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                    create_time=datetime.datetime.now()
                )
                return
            if order_state == '-1':
                self.log.info(f'订单状态为-1，充电桩[{terminal_address}]重复上送订单[{order_num}]状态信息：{electricity_status}')
                SErrorRecord.objects.create(
                    remark=f'充电桩[{terminal_address}]重复上送订单[{order_num}]停止信息',
                    create_time=datetime.datetime.now()
                )
                return

            if charge_type == 'auto':
                self.log.info(f'充满自停：{order_num}')
                self.handle_order_auto(user_id, terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity, begin_time)

            if charge_type == 'time':
                self.log.info(f'定时充电：{order_num}')
                self.handle_order_auto(user_id, terminal_address, socket_no, electricity_status, order_num, power,
                                       electricity_quantity, begin_time)


            if charge_type == 'money':
                self.log.info(f'定金额充电：{order_num}')
                self.handle_order_money(terminal_address, socket_no, electricity_status, order_num, power,
                                       electricity_quantity, begin_time)



            if charge_type == 'elec':
                self.log.info(f'定电量充电：{order_num}')
                self.handle_order_elec(terminal_address, socket_no, electricity_status, order_num, power,
                                       electricity_quantity, begin_time)

            if charge_type == 'card':
                self.log.info(f'刷卡充电：{order_num}')
                self.handle_order_card(terminal_address, socket_no, electricity_status, order_num, power,
                                       electricity_quantity, begin_time)

            # # 2)获取订单支付类型，更新费用表需要使用
            # fee_type, fee_no = self.get_fee_type(order_num)
            # # 3)获取订单开始时间
            #
            # # 2)更新电量
            # self.update_electric(order_num, electricity_quantity, fee_type, fee_no)
            # # 4)更新功率
        except Exception as e:
            self.log.error(f'更新订单信息出现错误：{e}')
            raise

    def handle_check_order(self, terminal_address, sockets_info):
        # 处理订单守护
        # 遍历插座：
        from SmartChargeBD.settings import SOCKET_TO_PROCESS
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        # keys_to_process = ['00', '01']  # 需要处理的插座序号
        keys_to_process = SOCKET_TO_PROCESS
        for key in keys_to_process:
            if key in sockets_info:  # 检查插座序号是否存在
                socket_status = sockets_info[key]  # 插座状态：00空闲，01正在使用
                # 1)查询该插座在数据库中的使用状态
                port_info = SEqPort.objects.filter(terminal_address=terminal_address, eq_port=key).first()
                if not port_info:
                    continue
                db_status = port_info.use_state
                self.log.info(f'充电桩：{terminal_address}, 插座：{key}')
                self.log.info(f'上报状态：{socket_status}, 数据库中状态：{db_status}')
                # 2)查询有没有订单在使用该插座
                order_info = SOrderInfo.objects.filter(term_address=terminal_address, eq_port=key, state=1)
                if order_info: # 有订单正在使用
                    if socket_status == '00':  # 订单在进行，插座停了
                        self.log.info(f'订单异常结束{order_info[0].order_id}, {terminal_address}, {key}')
                        # 停止订单
                        self.handle_order_stop(order_info, '订单异常停止')
                        # terminal_address = order_info[0].term_address
                        # eq_port = order_info[0].eq_port
                        # fee_type = order_info[0].fee_type
                        # fee_no = order_info[0].fee_no
                        # use_electric = order_info[0].use_electric
                        # begin_time = order_info[0].begin_time
                        # end_time = datetime.datetime.now()
                        # use_time = end_time - begin_time
                        # if fee_type == '1':  # 时段收费
                        #     order_fee_detail = SOrderFee1.objects.filter(order_id=order_info[0].order_id, fee_no=fee_no)
                        #     use_money_all = decimal.Decimal(0.00)
                        #     for item in order_fee_detail:
                        #         use_money_all = use_money_all + item.use_money
                        #
                        #     SOrderInfo.objects.filter(order_id=order_info[0].order_id).update(
                        #         use_money=use_money_all,
                        #         end_time=end_time,
                        #         use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                        #         end_type='2',
                        #         state='2'
                        #     )
                        # if fee_type == '2':
                        #     # 查询电量梯度
                        #     elec_grads = self.get_elec_grads(order_info[0].order_id, fee_no)
                        #     # 从订单表中查当前使用电量
                        #
                        #     # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
                        #     self.cal_grads_money(elec_grads, use_electric)
                        #     # 更新订单表
                        #     all_money = self.get_all_gards_money(order_info[0].order_id, fee_no)
                        #
                        #     SOrderInfo.objects.filter(order_id=order_info[0].order_id, create_time__gte=dt).update(
                        #         use_money=all_money,
                        #         end_time=end_time,
                        #         use_time=int(use_time.total_seconds() / 60),  # 转换成分钟,
                        #         end_type='2',
                        #         state='2'
                        #     )
                        # # 释放端口
                        # SEqPort.objects.filter(terminal_address=terminal_address, eq_port=eq_port).update(
                        #     use_state='0'
                        # )
                else:  # 没有订单在使用
                    if socket_status == '01':  # 但是插座状态是正在使用
                        # 这种情况几乎不会出现:
                        self.log.info(f'插座异常启动：{terminal_address},{key}')
                        # todo 关闭该插座
                        # todo 异常信息存入数据库


    def freezing_money(self, user_id, freeze_money):
        """
        冻结金额
        :param user_id:  用户id
        :param ice_money:  需要冻结的金额
        :return:
        """
        self.log.info(f'冻结金额：{user_id}, {freeze_money}')
        # 查询用户账户信息
        freeze_money = decimal.Decimal(str(freeze_money))
        user_account_info =ViewUserAccountOk.objects.filter(user_id=user_id).first()
        if not user_account_info:
            return False
        real_money = user_account_info.real_money
        ok_money = user_account_info.ok_money
        ice_money = user_account_info.ice_money


        # 检查需要冻结的金额是否大于可使用金额
        if freeze_money > ok_money:
            return False
        user_account_info.ok_money = ok_money - freeze_money
        user_account_info.ice_money = ice_money + freeze_money
        user_account_info.save()

        return True

    def unfreeze_money(self, user_id, unfreeze_money):
        """
        释放冻结金额
        :param user_id:  用户id
        :param ice_money:  需要冻结的金额
        :return:
        """
        self.log.info(f'解冻金额：{user_id}, {unfreeze_money}')
        unfreeze_money = decimal.Decimal(str(unfreeze_money))
        # 查询用户账户信息
        user_account_info =ViewUserAccountOk.objects.filter(user_id=user_id).first()
        if not user_account_info:
            self.log.info(f'失败--没有用户信息')
            return False
        real_money = user_account_info.real_money
        ok_money = user_account_info.ok_money
        ice_money = user_account_info.ice_money


        # 检查需要解冻的金额是否大于已冻结的金额
        if unfreeze_money > ice_money:
            self.log.info(f'失败--解冻金额大于已冻结金额')
            return False
        user_account_info.ok_money = ok_money + unfreeze_money
        user_account_info.ice_money = ice_money - unfreeze_money
        user_account_info.save()



        return True

    @transaction.atomic()
    def deduct_money(self, user_id, deduct_money):
        """
        扣钱
        :param user_id:
        :param deduct_money:
        :return:
        """
        # 查询用户账户信息
        self.log.info(f'账户扣款：{user_id}, {deduct_money}')
        deduct_money = decimal.Decimal(str(deduct_money))
        try:
            deduct_account = 0
            deduct_giftmoney = 0
            user_account_info = ViewUserAccountOk.objects.filter(user_id=user_id).first()
            user_info = SUserInfo.objects.filter(user_id=user_id, state='0').first()
            real_money = user_account_info.real_money
            ok_money = user_account_info.ok_money
            ice_money = user_account_info.ice_money
            gift_money = user_account_info.gift_money

            if user_account_info.ok_money >= deduct_money:   # 钱包勾扣，优先扣钱包
                user_account_info.real_money = real_money - deduct_money
                user_account_info.ok_money = ok_money - deduct_money

                user_info.account = user_info.account - deduct_money
                deduct_account = deduct_money  # 全部由钱包承担

            else:   # 不够扣，去扣赠送余额
                diff_money = deduct_money - user_account_info.ok_money  # 钱包差值
                if gift_money >= diff_money:  # 赠送余额够扣

                    user_info.account = user_info.account - user_account_info.ok_money
                    
                    user_account_info.real_money = real_money - user_account_info.ok_money
                    user_account_info.ok_money = 0  # 钱包扣完了
                    user_account_info.gift_money = gift_money - diff_money          # 赠送余额扣差值

                    deduct_account = deduct_money - diff_money
                    deduct_giftmoney = diff_money
                else:  # 赠送余额不够扣， 把钱包扣成负的
                    diff_gift_money = diff_money - gift_money  # 赠送余额差值

                    user_info.account = user_info.account - user_account_info.ok_money - diff_gift_money

                    user_account_info.real_money = real_money - user_account_info.ok_money - diff_gift_money
                    user_account_info.ok_money = 0 - diff_gift_money
                    user_account_info.gift_money = 0

                    deduct_account = deduct_money - gift_money
                    deduct_giftmoney = gift_money


            user_account_info.save()


            user_info.save()
            return True, deduct_account, deduct_giftmoney
        except Exception as e:
            self.log.error(f'扣款出现错误:{e}', exc_info=True)
            return False, None, None

    @transaction.atomic()
    def deduct_money_card(self, card_num, deduct_money):
        """
        扣钱
        :param card_num: 卡号
        :param deduct_money:  需要扣的钱
        :return:
        """
        # 查询用户账户信息
        self.log.info(f'电卡扣款：{card_num}, {deduct_money}')
        deduct_money = decimal.Decimal(str(deduct_money))
        try:
            deduct_account = 0
            deduct_giftmoney = 0
            card_account_info = SCardsInfo.objects.filter(card_num=card_num)[0]
            money = card_account_info.money
            gift_money = card_account_info.gift_money

            if money >= deduct_money:  # 钱包勾扣，优先扣钱包
                card_account_info.money = money - deduct_money
                deduct_account = deduct_money  # 全部由钱包承担

            else:  # 不够扣，去扣赠送余额
                diff_money = deduct_money - money  # 钱包差值
                if gift_money >= diff_money:  # 赠送余额够扣

                    card_account_info.money = 0  # 钱包扣完了
                    card_account_info.gift_money = gift_money - diff_money  # 赠送余额扣差值

                    deduct_account = deduct_money - diff_money
                    deduct_giftmoney = diff_money
                else:  # 赠送余额不够扣， 把钱包扣成负的
                    diff_gift_money = diff_money - gift_money  # 赠送余额差值

                    card_account_info.money = 0 - diff_gift_money  # 差值扣钱包

                    card_account_info.gift_money = 0

                    deduct_account = deduct_money - gift_money
                    deduct_giftmoney = gift_money

            card_account_info.save()

            return True, deduct_account, deduct_giftmoney
        except Exception as e:
            self.log.error(f'扣款出现错误:{e}', exc_info=True)
            return False, None, None

    def add_account_record(self, user_id, order_id, money, remark):
        """
        增加账户变动记录
        :param user_id:
        :param money:
        :return:
        """
        self.log.info(f'充电花费账户变动：{user_id}, {order_id}, {money}')
        money = float(money)
        money = abs(money)
        # 查询当前余额
        user_account_info = ViewUserAccountOk.objects.filter(user_id=user_id)[0]
        user_info = SUserInfo.objects.filter(user_id=user_id, state='0')[0]
        now_money = user_account_info.real_money
        # 增加交易记录
        SAccountDetail.objects.create(
            change_type='out',
            change_money=money,
            now_money=now_money,
            order_id=order_id,
            user_id=user_id,
            remark=remark,
            create_time=datetime.datetime.now()
        )


    def add_account_record_card(self, card_num, order_id, money, remark):
        """
        增加账户变动记录
        :param user_id:
        :param money:
        :return:
        """
        self.log.info(f'电卡充电花费账户变动：{card_num}, {order_id}, {money}')
        money = float(money)
        money = abs(money)
        # 查询当前余额
        card_info = SCardsInfo.objects.filter(card_num=card_num)[0]
        card_sn = card_info.card_sn
        tel = card_info.tel
        now_money = card_info.money
        user_id = card_info.user_id

        # 增加交易记录
        SCardConsumeDetail.objects.create(
            card_sn=card_sn,
            card_num=card_num,
            use_money=money,
            now_money=now_money,
            card_tel=tel,
            order_id=order_id,
            user_id=user_id,
            remark=remark,
            create_time=datetime.datetime.now()
        )

    def refund_money_online(self, charge_order, refund_amount, total_money):
        """
        创建退款信息
        :param charge_order:
        :param refund_amount:
        :return:
        """
        self.log.info(f'处理在线支付订单退款: {charge_order}，退款金额：{refund_amount}, 微信订单总金额：{total_money}')
        from app.utils.get_seq import Get_SeqNo
        from app.utils.wx_pay import order_refund
        try:
            # 查询订单退款状态
            order_refund_state = SOrderInfo.objects.get(order_id=charge_order).refund_state
            if order_refund_state == '1':
                self.log.info(f'订单重复退款：{charge_order}')
                SErrorRecord.objects.create(
                    remark=f'订单：{charge_order},请求重复退款,不处理',
                    create_time=datetime.datetime.now()
                )
                return
            refund_no = Get_SeqNo("REFUND_CHARGE_ORDER")
            # 查找充值订单号
            sub_order_info = SOrderNumMap.objects.filter(charge_order=charge_order).first()
            self.log.info(f'sub_order_info: {sub_order_info}')
            if sub_order_info:
                # transaction_id, order_id, out_trade_no, amount
                sub_order = sub_order_info.sub_order
                transaction_id = sub_order_info.transaction_id
                refund_amount_ = int(refund_amount * 100)
                total_money_ = int(total_money * 100)
                user_id = sub_order_info.user_id

                # 创建退款订单
                # 创建充电订单微信交易记录
                SWxTranOrderDetail.objects.create(
                    change_type='out',
                    change_money=float(refund_amount),
                    user_id=user_id,
                    order_id=refund_no,
                    charge_order=charge_order,
                    verify_state='1',
                    verify_time=datetime.datetime.now(),
                    create_time=datetime.datetime.now(),
                    state='1'
                )
                self.log.info(f'开始退款')
                res = order_refund(transaction_id, refund_no, sub_order, refund_amount_, total_money_)
                self.log.info(f'退款结果：{res}')

        except Exception as e:
            self.log.error(f'退款错误：{e}', exc_info=True)

    def handle_order_stop(self, order, remark):
        """
        处理订单停止
        :param order:
        :return:
        """
        self.log.info(f'处理订单停止：{order}, {remark}')
        dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
        OrderNumber = order[0].order_id
        terminal_address = order[0].term_address
        eq_id = order[0].eq_id
        eq_port = order[0].eq_port
        fee_type = order[0].fee_type
        fee_no = order[0].fee_no
        pay_way = order[0].pay_way
        user_id = order[0].user_id
        charge_type = order[0].charge_type
        charge_money = order[0].charge_money
        use_electric = order[0].use_electric
        begin_time = order[0].begin_time
        card_num = order[0].card_num
        end_time = datetime.datetime.now()
        use_time = end_time - begin_time
        end_reason = remark


        if fee_type == '1':  # 时段收费
            order_fee_detail = SOrderFee1.objects.filter(order_id=OrderNumber, fee_no=fee_no, create_time__gte=dt)
            use_money_all = decimal.Decimal(0.00)
            for item in order_fee_detail:
                use_money_all = use_money_all + item.use_money

            state = '2'
            # 判断充电类型
            if charge_type == 'auto' or charge_type == 'time' or charge_type == 'elec' or charge_type == 'card':
                # 这三种模式不需要退钱
                # 金额解冻
                # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                # 扣钱
                if charge_type != 'card':
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=use_money_all)
                else:
                    res2, deduct_account, duduct_giftmoney = self.deduct_money_card(card_num, deduct_money=use_money_all)
                if res2:
                    # 订单消费结构
                    SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )
                    # 创建消费记录
                    if charge_type != 'card':
                        self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')
                    else:
                        self.add_account_record_card(card_num, order_id=OrderNumber, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record_card(card_num, order_id=OrderNumber, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')

                state = '2'
                if not res2:
                    remark = '扣款出现错误'
                    state = '-1'
            elif charge_type == 'money':
                if charge_money > use_money_all:  # 实际使用金额小于用户所选金额，需要退款
                    return_money = charge_money - use_money_all  # 需要返还的金额
                    # 判断支付方式
                    if pay_way == 'online':
                        # 在线支付，需要退款

                        SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt).update(
                            return_money=return_money
                        )
                        self.refund_money_online(charge_order=OrderNumber, refund_amount=return_money, total_money=charge_money)
                        if use_money_all > decimal.Decimal(0.00):
                            self.wx_dis_profit(charge_order=OrderNumber, use_money_all=use_money_all)

                    if pay_way == 'account':
                        # 余额支付，无需退款，扣除实际使用金额即可
                        # 解冻金额
                        # res1 = self.unfreeze_money(user_id, unfreeze_money=charge_money)
                        res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=use_money_all)

                        if res2:
                            # 订单消费结构
                            SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )
                            # 创建消费记录

                            self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                    remark='充电花费-基本余额')

                            self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                    remark='充电花费-赠送余额')

                        if res2:
                            SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt).update(
                                return_money=return_money,
                                refund_state='1'
                            )

                        if not res2:
                            remark = '扣款出现错误'
                            state = '-1'
                else:  # 实际金额大于等于用户所选金额
                    if pay_way == 'online':
                        # 不需要扣款，不需要退款
                        pass
                    if pay_way == 'account':
                        # 余额支付，无需退款，扣除实际使用金额即可
                        # 解冻金额
                        # res1 = self.unfreeze_money(user_id, unfreeze_money=charge_money)
                        res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=use_money_all)

                        if res2:
                            # 订单消费结构
                            SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )                            # 创建消费记录

                            self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                    remark='充电花费-基本余额')

                            self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                    remark='充电花费-赠送余额')

                        if not res2:
                            remark = '扣款出现错误'
                            state = '-1'

            SOrderInfo.objects.filter(order_id=OrderNumber).update(
                use_money=use_money_all,
                end_time=end_time,
                use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                end_type='2',
                state=state,
                remark=remark,
                end_reason=end_reason
            )
            # 分账
            self.dis_profit(order_id=OrderNumber, use_money=use_money_all, eq_id=eq_id)
            # 发送充电结束消息
            if user_id and charge_type != 'card':  # 用户注册过小程序  电卡充电不发消息
                self.log.info(f'发送充电结束消息')
                wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                if wx_open_id:  # 用户关注了公众号
                    data_stop = {
                        'order_id': OrderNumber,
                        'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'use_money': f'{use_money_all}元',
                        'use_electric': str(use_electric)
                    }
                    self.log.info(f'发送的内容：{data_stop}')
                    # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                    SWxTempMsg.objects.create(
                        user_id=user_id,
                        wx_open_id=wx_open_id,
                        xcx_open_id=xcx_open_id,
                        union_id=union_id,
                        msg_type='charge_end',
                        send_data=json.dumps(data_stop),
                        create_time=datetime.datetime.now(),
                        state='0'
                    )


        if fee_type == '2':
            # 查询电量梯度
            elec_grads = self.get_elec_grads(OrderNumber, fee_no)
            # 从订单表中查当前使用电量

            # 计算金额（给每一梯度的金额都计算出来，并更新到详细表中）
            self.cal_grads_money(elec_grads, use_electric)
            # 更新订单表
            all_money = self.get_all_gards_money(OrderNumber, fee_no)
            end_time = datetime.datetime.now()
            use_time = end_time - begin_time


            state = '2'
            # 判断充电类型
            if charge_type == 'auto' or charge_type == 'time' or charge_type == 'elec' or charge_type == 'card':
                # 这三种模式不需要退钱
                # 金额解冻
                # res1 = self.unfreeze_money(user_id, unfreeze_money=1)
                # 扣钱
                if charge_type != 'card':
                    res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)
                else:
                    res2, deduct_account, duduct_giftmoney = self.deduct_money_card(card_num, deduct_money=all_money)

                if res2:
                    # 订单消费结构
                    SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                        account=deduct_account,
                        gift_money=duduct_giftmoney,
                        update_time=datetime.datetime.now()
                    )
                    # 创建消费记录
                    if charge_type != 'card':
                        self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                remark='充电花费-基本余额')

                        self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                remark='充电花费-赠送余额')
                    else:
                        self.add_account_record_card(card_num, order_id=OrderNumber, money=deduct_account,
                                                     remark='充电花费-基本余额')

                        self.add_account_record_card(card_num, order_id=OrderNumber, money=duduct_giftmoney,
                                                     remark='充电花费-赠送余额')


                state = '2'
                if not res2:
                    remark = '扣款出现错误'
                    state = '-1'
            elif charge_type == 'money':
                if charge_money > all_money:  # 实际使用金额小于用户所选金额，需要退款
                    return_money = charge_money - all_money  # 需要返还的金额
                    # 判断支付方式
                    if pay_way == 'online':
                        # 在线支付，需要退款

                        SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt).update(
                            return_money=return_money
                        )
                        self.refund_money_online(charge_order=OrderNumber, refund_amount=return_money, total_money=charge_money)
                        if all_money > decimal.Decimal(0.00):
                            self.wx_dis_profit(charge_order=OrderNumber, use_money_all=all_money)
                    if pay_way == 'account':
                        # 余额支付，无需退款，扣除实际使用金额即可
                        # 解冻金额
                        # res1 = self.unfreeze_money(user_id, unfreeze_money=charge_money)
                        res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)

                        if res2:
                            # 订单消费结构
                            SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )
                            # 创建消费记录

                            self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                    remark='充电花费-基本余额')

                            self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                    remark='充电花费-赠送余额')

                        if res2:
                            SOrderInfo.objects.filter(order_id=OrderNumber, create_time__gte=dt).update(
                                return_money=return_money,
                                refund_state='1'
                            )

                        if not res2:
                            remark = '扣款出现错误'
                            state = '-1'
                else:  # 实际金额大于等于用户所选金额
                    if pay_way == 'online':
                        # 不需要扣款，不需要退款
                        pass
                    if pay_way == 'account':
                        # 余额支付，无需退款，扣除实际使用金额即可
                        # 解冻金额
                        # res1 = self.unfreeze_money(user_id, unfreeze_money=charge_money)
                        res2, deduct_account, duduct_giftmoney = self.deduct_money(user_id, deduct_money=all_money)
                        if res2:
                            # 订单消费结构
                            SOrderUseMoney.objects.filter(order_id=OrderNumber).update(
                                account=deduct_account,
                                gift_money=duduct_giftmoney,
                                update_time=datetime.datetime.now()
                            )
                            # 创建消费记录

                            self.add_account_record(user_id, order_id=OrderNumber, money=deduct_account,
                                                    remark='充电花费-基本余额')

                            self.add_account_record(user_id, order_id=OrderNumber, money=duduct_giftmoney,
                                                    remark='充电花费-赠送余额')


                        if not res2:
                            remark = '扣款出现错误'
                            state = '-1'

            SOrderInfo.objects.filter(order_id=OrderNumber).update(
                use_money=all_money,
                end_time=end_time,
                use_time=int(use_time.total_seconds() / 60),  # 转换成分钟
                end_type='2',
                state=state,
                remark=remark,
                end_reason=end_reason
            )
            self.dis_profit(order_id=OrderNumber, use_money=all_money, eq_id=eq_id)
            # 发送充电结束消息
            if user_id and charge_type != 'card':  # 用户注册过小程序
                self.log.info(f'发送充电结束消息')
                wx_open_id, xcx_open_id, union_id = self.get_oa_open_id(user_id=user_id)
                if wx_open_id:  # 用户关注了公众号
                    data_stop = {
                        'order_id': OrderNumber,
                        'use_time': f'{int(use_time.total_seconds() / 60)}分钟',
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'use_money': f'{all_money}元',
                        'use_electric': str(use_electric)
                    }
                    self.log.info(f'发送的内容：{data_stop}')
                    # wx_temp_msg.send_charge_stop_notice(wx_open_id, data_stop)

                    SWxTempMsg.objects.create(
                        user_id=user_id,
                        wx_open_id=wx_open_id,
                        xcx_open_id=xcx_open_id,
                        union_id=union_id,
                        msg_type='charge_end',
                        send_data=json.dumps(data_stop),
                        create_time=datetime.datetime.now(),
                        state='0'
                    )

        # 释放端口
        self.log.info(f'释放端口')
        SEqPort.objects.filter(terminal_address=terminal_address, eq_port=eq_port).update(
            use_state='0'
        )
        # 更新插座当前功率
        SEqPort.objects.filter(terminal_address=terminal_address, eq_port=eq_port).update(
            power_time=datetime.datetime.now(),
            power=0
        )
        if charge_type == 'card':
            self.log.info(f'释放电卡')
            SCardsInfo.objects.filter(card_num=card_num).update(
                use_state='0'
            )

    def get_oa_open_id(self, user_id):
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
            self.log.error(f'获取open_id失败：{e}', exc_info=True)

    #分账
    def dis_profit(self, order_id, use_money, eq_id):
        """
        分账，通过设备查到所属区域，再查到区域负责人，费率等。
        :param order_id: 订单id
        :param use_money: 使用金额
        :param eq_id: 设备id
        :return:
        """
        # 通过设备id查所属区域
        try:
            self.log.info(f'开始分账---订单：{order_id}, 设备：{eq_id}, 使用金额：{use_money}')
            site_info = SEqInfo.objects.filter(eq_id=eq_id).first()
            site_id = site_info.site_id
            # 查询站点负责人
            admin_users = SDisProfitCfg.objects.filter(site_id=site_id)
            for admin_user in admin_users:
                dis_rate = admin_user.dis_rate
                user_id = admin_user.user_id
                dis_money = use_money * dis_rate
                self.log.info(f'分账详情--分账人：{user_id}, 比例：{dis_rate}, 所分金额：{dis_money}')
                SDisProfitDetail.objects.create(
                    order_id=order_id,
                    eq_id=eq_id,
                    site_id=site_id,
                    user_id=user_id,
                    order_money=use_money,
                    dis_rate=dis_rate,
                    dis_money=dis_money,
                    create_time=datetime.datetime.now(),
                    state='0'
                )
        except Exception as e:
            self.log.error(f'分账错误：{e}', exc_info=True)

    def wx_dis_profit(self, charge_order, use_money_all):
        from app.utils.get_seq import Get_SeqNo
        from app.utils import wx_pay
        sub_order_info = SOrderNumMap.objects.filter(charge_order=charge_order).first()
        self.log.info(f'开始分账：sub_order_info: {sub_order_info}')
        if sub_order_info:
            # transaction_id, order_id, out_trade_no, amount
            sub_order = sub_order_info.sub_order
            transaction_id = sub_order_info.transaction_id

            user_id = sub_order_info.user_id
            source = '订单在线支付'
            receiver_info = SDisProfitReceiver.objects.filter()[0]
            type = receiver_info.type
            account = receiver_info.account
            rate = receiver_info.rate
            description = receiver_info.description
            amount = int(use_money_all * 100 * rate)
            if not (amount > 0):
                self.log.info(f'分账金额不大于0，取消分账')
                return
            dis_order_id = Get_SeqNo('PROFIT_SHARE_WX')
            profit_info = SWxDisProfitOrder.objects.create(
                dis_order_id=dis_order_id,
                tran_order_id=sub_order,
                transaction_id=transaction_id,
                account=account,
                amount=amount / 100,
                source=source,
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
            # time.sleep(10)
            res = wx_pay.wx_profit_share(sub_order, dis_order_id, transaction_id, amount, receivers)
            self.log.info(f'请求分账结果：{res[0]}')
            self.log.info(f'请求分账结果：{res[1]}')
            # profit_info.
            if res[0] == 200:
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
                profit_info.fail_reason = fail_reason if res[0] == 200 else res[1]
                profit_info.finish_time = finish_time_dt
                profit_info.state = state
                profit_info.receiver_type = type
                profit_info.save()
            else:
                profit_info.fail_reason = res[1]
                profit_info.finish_time = datetime.datetime.now()
                profit_info.save()

    def cal_elec_cost(self, eq_id, use_elec):
        use_elec = decimal.Decimal(use_elec)
        eq_info = SEqInfo.objects.filter(eq_id=eq_id)[0]
        elec_price = eq_info.elec_price
        if elec_price is None:
            elec_price = decimal.Decimal(0.00)
        elec_cost = elec_price * use_elec
        return elec_cost

    def handle_card_start_order(self, terminal_address, socket_no, card_sn, deci_card_sn):
        status = '00'
        order_no = '00000000'
        balance = 0
        card_info = SCardsInfo.objects.filter(card_num=deci_card_sn)  # 卡信息
        eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)  #设备信息
        port_info = SEqPort.objects.filter(terminal_address=terminal_address, eq_port=socket_no)  # 插座信息

        state = eq_info[0].state
        eq_conn_state = eq_info[0].conn_state
        eq_state = eq_info[0].eq_state
        eq_id = eq_info[0].eq_id
        port_state = port_info[0].state
        port_use_state = port_info[0].use_state
        port_conn_state = port_info[0].conn_state
        self.log.info(f'设备信息：{terminal_address}-运营状态:{state},连接状态:{eq_conn_state},设备状态:{eq_state}')
        self.log.info(f'插座信息：{socket_no}-插座状态:{port_state},连接状态:{port_conn_state},使用状态:{port_use_state}')

        if state != '1':
            self.log.info(f'设备未运营')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0
        if eq_conn_state != '1':
            self.log.info(f'设备离线')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0
        if eq_state == '-1':
            self.log.info(f'设备异常')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0
        if port_use_state == '1':
            self.log.info(f'插座正在被使用')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0
        if port_conn_state == '0':
            self.log.info(f'插座离线')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0
        if port_state == '-1':
            self.log.info(f'插座异常')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0

        card_use_state = card_info[0].use_state
        card_state = card_info[0].state
        money = card_info[0].money
        gift_money = card_info[0].gift_money
        self.log.info(f'卡信息：{card_sn}-{deci_card_sn},使用状态:{card_use_state},卡状态:{card_state},余额:{money},赠送余额:{gift_money}')
        if card_use_state == '1':
            self.log.info(f'该卡正在使用')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0

        # 查卡状态
        if state != '1':
            self.log.info(f'该卡状态为：{state},非正常状态')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0

        # 查余额
        if money <= 0 and gift_money <= 0:
            self.log.info(f'余额不足')
            status = '01'  # 失败
            order_no = '00000000'
            balance = 0

        # 生成订单号
        # if status == '00':
        #     OrderNumber_ = Get_SeqNo("CHARGE_ORDER")[-10:]
        #     if int(OrderNumber_) >= 4294967295:
        #         self.log.info(f'订单')
        #         status = '01'  # 失败
        #         order_no = '00000000'
        #         balance = 0

        if status == '00':  # 没有以上问题，进行创建订单的一系列操作
            # 定时任务
            self.log.info(f'符合开启条件')
            SOrderCardPre.objects.create(
                terminal_address=terminal_address,
                eq_id=eq_id,
                eq_port=socket_no,
                card_num=deci_card_sn,
                state='0',
                create_time=datetime.datetime.now()
            )
            res = SEqPort.objects.filter(terminal_address=terminal_address, use_state='0', eq_port=socket_no).update(
                use_state='1')
            SCardsInfo.objects.filter(card_num=deci_card_sn).update(
                use_state='1'
            )
            self.log.info(f'锁插座---锁卡')
            # order_no = hex(int(OrderNumber_)).lstrip('0x').zfill(8).upper()
            #
            # # 设备计价规则
            # eq_fee_type = eq_info[0].fee_type
            # eq_fee_no = eq_info[0].fee_no
            #
            #
            # # 创建订单需要的信息
            # site_id = eq_info[0].site_id
            # eq_id = eq_info[0].eq_id
            # user_id = card_info[0].user_id
            #
            # # 创建订单
            # SOrderInfo.objects.create(
            #     site_id=site_id,
            #     eq_id=eq_id,
            #     eq_port=socket_no,
            #     term_address=terminal_address,
            #     card_num=deci_card_sn,
            #     charge_type='card',
            #     pay_way='card',
            #     charge_time=0,
            #     charge_electric=0,
            #     charge_money=0,
            #     fee_type=eq_fee_type,
            #     fee_no=eq_fee_no,
            #     user_id=user_id,
            #     order_id=order_no,
            #     state='1',
            #     error_times=0,
            #     create_time=datetime.datetime.now(),
            #     begin_time=datetime.datetime.now(),
            #     use_electric=0,
            #     use_money=0,
            #     use_time=0,
            #     order_source='用户刷卡'
            # )
            #
            #
            # # 创建计费
            # self.create_fee_detail(order_no, eq_fee_type, eq_fee_no)
            #
            # # 创建费用结构
            # SOrderUseMoney.objects.create(
            #     order_id=order_no,
            #     create_time=datetime.datetime.now()
            # )
            # balance = money + gift_money


        return status, order_no, balance


    def handle_card_stop_order(self, terminal_address, socket_no, card_sn, deci_card_sn):
        try:
            card_info = SCardsInfo.objects.filter(card_num=deci_card_sn)  # 卡信息



            card_use_state = card_info[0].use_state
            card_state = card_info[0].state
            money = card_info[0].money
            gift_money = card_info[0].gift_money
            self.log.info(f'卡信息：{card_sn}-{deci_card_sn},使用状态:{card_use_state},卡状态:{card_state},余额:{money},赠送余额:{gift_money}')



            if card_use_state == '1':  # 卡正在使用，查了余额，让他关闭
                # 查询订单
                cardorder = SOrderInfo.objects.filter(charge_type='card', term_address=terminal_address,
                                                      card_num=deci_card_sn, state='1')
                if cardorder.exists():
                    # 定时任务
                    self.log.info(f'该卡：{deci_card_sn}, 在设备：{terminal_address}上有订单，停止订单')
                    eq_id = cardorder[0].eq_id
                    order_id = cardorder[0].order_id
                    SOrderCardStop.objects.create(
                        terminal_address=terminal_address,
                        eq_id=eq_id,
                        eq_port=socket_no,
                        card_num=deci_card_sn,
                        order_id=order_id,
                        state='0',
                        create_time=datetime.datetime.now()
                    )
        except Exception as e:
            self.log.error(f'刷卡停止充电错误：{e}', exc_info=True)

if __name__ == '__main__':
    from app.utils import MyLog


    file_name = os.path.basename(__file__)[:-3]
    file_path = os.path.dirname(__file__)
    # log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger
    # handle_ = HandleOrder(log)
    # 测试冻结金额
    # user_id = 1
    amount = 0.1
    # res = handle_.freezing_money(user_id, amount)
    # res = handle_.unfreeze_money(user_id, amount)
    # print(res)
    # res = handle_.deduct_money(user_id, amount)
    # print(res)

