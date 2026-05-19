#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：bd_api.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/23 10:00 
@Description : 和数据库相关的操作
'''
import datetime
import json

from app.models import *
import os
import sys

pwd = os.path.dirname(os.path.realpath(__file__))
# print('litz',pwd)
# print(sys.path)
sys.path.append(pwd)
# print(sys.path)
from app.utils.handle_order import HandleOrder
from app.command.tools.ApiTool import ApiTool

class BDAPI:
    def __init__(self, log):
        self.log = log
        self.handleorder = HandleOrder(log)
        self.apitool = ApiTool(log)

    def login_(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            is_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
            if is_exist:
                SEqInfo.objects.filter(terminal_address=terminal_address).update(conn_state='1', last_conn_time=datetime.datetime.now())
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def logout_(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            is_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
            if is_exist:
                SEqInfo.objects.filter(terminal_address=terminal_address).update(conn_state='0', last_conn_time=datetime.datetime.now())
                SEqPort.objects.filter(terminal_address=terminal_address).update(
                    conn_state='0'  # 插座离线
                )
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def heartbeat_(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            is_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
            if is_exist:
                # 更新设备状态
                SEqInfo.objects.filter(terminal_address=terminal_address).update(conn_state='1', last_conn_time=datetime.datetime.now())
                # 更新插座连接状态
                SEqPort.objects.filter(terminal_address=terminal_address).update(conn_state='1')
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def login_verify_(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')
        password = recv_data['app_region']['Specific_data_detail'].get('password')
        if terminal_address:
            is_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
            if is_exist:
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    conn_state='1',
                    last_conn_time=datetime.datetime.now(),
                    password=password
                )
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def set_params_(self, recv_data):  # 设置参数的结果,这里边还要再分一级匹配函数
        from app.shell import is_save_cmd_db
        self.log.info(f'设置参数')
        # 这里对设置参数不进行处理，只把响应的内容存到数据库中
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            is_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
            if is_exist:
                PR_SEQ = recv_data['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')
                AFN = recv_data['app_region'].get('app_region_function_code')
                Fn = recv_data['app_region']['Data_unit_identification'].get('Fn')
                set_param_result = recv_data['app_region']['Specific_data_detail'].get('set_param_result')
                api_code = AFN + Fn

                is_save, cmd_type = is_save_cmd_db(AFN, Fn)
                if is_save:
                    self.log.info(f'保存到数据库中...')
                    SCmdInfo.objects.filter(term_address=terminal_address, PR_SEQ=PR_SEQ, api_code=api_code, resp_status='0').update(
                        resp_cmd=json.dumps(recv_data),
                        resp_status='1',
                        operate_result=set_param_result,
                        resp_time=datetime.datetime.now()
                    )
                else:
                    self.log.info(f'不保存数据库')
                # 更新设备通信状态
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    conn_state='1',
                    last_conn_time=datetime.datetime.now()
                )
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    # 查询参数
    def query_para_(self, recv_data):
        from app.shell import is_save_cmd_db
        # 这里对设置参数不进行处理，只把响应的内容存到数据库中
        # 1）查询设备
        terminal_address = recv_data['address_region'].get('address_term_r')

        if terminal_address:
            eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
            is_exist = eq_info.exists()
            if is_exist:
                PR_SEQ = recv_data['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')
                AFN = recv_data['app_region'].get('app_region_function_code')
                Fn = recv_data['app_region']['Data_unit_identification'].get('Fn')
                api_code = AFN + Fn

                status = recv_data['app_region']['Specific_data_detail'].get('status')  # 查询状态
                is_save, cmd_type = is_save_cmd_db(AFN, Fn)
                if is_save:  # 是否保存到数据库里

                    SCmdInfo.objects.filter(term_address=terminal_address, PR_SEQ=PR_SEQ, api_code=api_code, resp_status='0').update(
                        resp_cmd=json.dumps(recv_data),
                        resp_status='1',
                        operate_result=status,
                        resp_time=datetime.datetime.now()
                    )
                # 更新设备通信状态
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    conn_state='1',
                    last_conn_time=datetime.datetime.now()
                )
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')


    def query_socket_status(self, recv_data):
        # 查询插座状态，涉及订单守护，数据量大，不走[存储命令--》接收响应命令--》定时任务处理]的路线，
        # 单独写一个处理方法，不进行存储
        self.log.info(f'查询插座状态')
        # 1）查询设备
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
            is_exist = eq_info.exists()
            if is_exist:

                sockets_info = recv_data['app_region']['Specific_data_detail']
                status = sockets_info.get('status')  # 查询状态
                socket_counts = sockets_info.get('count')  # 插座数量
                self.log.info(f'查询插座状态：{status}, 插座数量：{socket_counts}')
                # 判断查询状态
                if status == '0':  # 查询成功
                    self.handleorder.handle_check_order(terminal_address, sockets_info)

                elif status == '1':
                    self.log.error(f'查询插座状态失败：不支持此功能')
                else:
                    self.log.error(f'查询插座状态失败：未知原因')
                # 更新设备通信状态
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    conn_state='1',
                    last_conn_time=datetime.datetime.now()
                )
            elif not is_exist:
                self.log.error(f'查询插座状态失败：设备{terminal_address}未注册！')

    def report_SIM_card(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')

        if terminal_address:
            eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
            is_exist = eq_info.exists()
            if is_exist:
                card_number = recv_data['app_region']['Specific_data_detail'].get('card_number')
                card_length = recv_data['app_region']['Specific_data_detail'].get('card_length')
                # 更新设备通信状态、sim信息
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    sim_card=card_number,
                    sim_card_len=card_length,
                    conn_state='1',
                    last_conn_time=datetime.datetime.now()
                )
                card_info = SEqSimCard.objects.filter(terminal_address=terminal_address)
                if card_info:
                    card_info.update(sim_card=card_number)
                else:
                    eq_id = SEqInfo.objects.filter(terminal_address=terminal_address)[0].eq_id
                    SEqSimCard.objects.create(
                        terminal_address=terminal_address,
                        eq_id=eq_id,
                        sim_card=card_number,
                        create_time=datetime.datetime.now()
                    )
            elif not is_exist:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def update_order(self, electricity_status, order_num, power, electricity_quantity):
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


    # 插座实时状态，涉及到订单
    def report_Socket_Status(self, recv_data):
        terminal_address = recv_data['address_region'].get('address_term_r')
        self.log.info(f'插座状态')
        if terminal_address:
            eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
            if eq_info.exists():
                # 更新设备通信状态
                SEqInfo.objects.filter(terminal_address=terminal_address).update(
                    conn_state='1',
                    last_conn_time=datetime.datetime.now()
                )

                orders_info = recv_data['app_region']['Specific_data_detail']
                self.log.info(f'插座订单信息:{terminal_address}，{orders_info}')

                socket_counts = orders_info.pop('socket_counts')

                for socket_no in orders_info:
                    # self.log.info(socket_no)
                    electricity_status = orders_info[socket_no].get('electricity_status')
                    order_num = orders_info[socket_no].get('order_num')
                    power = orders_info[socket_no].get('power')
                    electricity_quantity = orders_info[socket_no].get('electricity_quantity')

                    # 查询订单状态
                    dt = datetime.datetime.now() - datetime.timedelta(days=30)  # 订单创建时间要在30天内，防止订单号重复
                    self.log.info(f'order_num={order_num}')
                    order_state = SOrderInfo.objects.get(order_id=order_num, create_time__gte=dt).state
                    if order_state == '2' or order_state == '-1':
                        self.log.info(f'订单状态为：{order_state},充电桩[{terminal_address}]重复上送订单[{order_num}]状态信息：{electricity_status}')
                        SErrorRecord.objects.create(
                            remark=f'订单状态为：{order_state},充电桩[{terminal_address}]重复上送订单[{order_num}]状态信息：{electricity_status}',
                            create_time=datetime.datetime.now()
                        )
                        return

                    self.handleorder.update_order(terminal_address, socket_no, electricity_status, order_num, power, electricity_quantity)

            else:
                self.log.error(f'设备{terminal_address}未注册，登录失败！')

    def report_Card_record(self, recv_data):  # 处理刷卡充电
        pass

    def get_func1(self, AFN, Fn):
        """
        匹配接口
        :param dict_data: 解包后的数据
        :return: 对应的接口
        """
        Function_mapping = {
            '02': {   # 充电桩主动发送，需要返回
                '01': self.login_,
                '02': self.logout_,
                '03': self.heartbeat_,
                '04': self.login_verify_
            },
            '04': {  # 设置参数的结果，
                '20': self.set_params_,    # 这个比较特殊，设置参数的结果，放进一个相当于命令表的数据库表中
                '01': self.set_params_,
                '02': self.set_params_,
                '17': self.set_params_,
                '18': self.set_params_,
                '19': self.set_params_,
                '21': self.set_params_,
            },
            '0A': {  # 查询参数的结果，  这个由于
                '01': self.query_para_,
                '02': self.query_para_,
                '03': self.query_para_,
                '17': self.query_para_,
                '18': self.query_para_,
                '19': self.query_para_,
                '20': self.query_socket_status,  # 查询插座状态，不用统一入口
                '21': self.query_para_,
                '41': self.query_para_,
                # '02': self.domain_port_,
                # '03': self.apifunc.Query_parameters_Signal_strength,
                # '17': self.apifunc.Query_parameters_Power_threshold,
                # '18': self.apifunc.Query_parameters_Settle_allocation,
                # '19': self.apifunc.Query_parameters_Pile_status,
                # '20': self.apifunc.Query_parameters_Socket_status,
                # '21': self.apifunc.Query_parameters_QRcode,
                # '41': self.apifunc.Query_parameters_Total_electricity
            },
            '0E': {  # 充电桩主动数据上报
                '01': self.report_SIM_card,
                '03': self.report_Socket_Status,
                '04': self.report_Card_record
            }
        }
        try:
            func = Function_mapping[AFN].get(Fn)
        except KeyError:
            self.log.error(f"接口匹配失败，找不到接口！", exc_info=True)
            return None

        if func:
            self.log.info(f"接口匹配成功！")
            return func
        elif func is None:
            self.log.error(f"接口匹配失败，找不到接口！")
            return None

    def handle_special_data(self, recv_dict):  # 对充电桩上报信息中的special——data进行处理
        # 这里要进行匹配接口
        # 匹配接口
        AFN = recv_dict['app_region'].get('app_region_function_code')
        Fn = recv_dict['app_region']['Data_unit_identification'].get('Fn')
        # terminal_address = recv_dict['address_region'].get('address_term_r', '')
        if not all([AFN, Fn]):
            self.log.error(f'报文缺少AFN或Fn')
        func = self.get_func1(AFN, Fn)

        resp_data = func(recv_dict)
        self.log.info(f'二次解析接口{func}返回的结果:{resp_data}')



    def login_special_data(self, recv_data):
        return 'special_data'


    def report_Card_record_special_data(self, recv_data):
        self.log.info(f'special_data组包--刷卡')
        terminal_address = recv_data['address_region'].get('address_term_r')
        if terminal_address:
            eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
            is_exist = eq_info.exists()
            if is_exist:

                Card_record_info = recv_data['app_region']['Specific_data_detail']
                business_type = Card_record_info.get('business_type')  # 业务类型
                socket_no = Card_record_info.get('socket_no')  # 插座序号
                card_sn = Card_record_info.get('card_sn')
                deci_card_sn = str(int(card_sn, 16)).zfill(10)
                self.log.info(f'业务类型：{business_type}, 插座序号：{socket_no}, 卡号：{card_sn}--{deci_card_sn}')
                Specific_data_json = {
                    'status': '01',  # 确认状态,1字节
                    'buiness_type': business_type,  # 业务类型,1字节
                    'socket_no': socket_no,  # 插座序号
                    'order_no': '',  # 订单号,4字节
                    'balance': ''  # 卡余额,4字节
                }
                # 查卡信息
                card_info = SCardsInfo.objects.filter(card_num=deci_card_sn)
                if not card_info:
                    self.log.info(f'卡号不存在/未绑定')
                    Specific_data_json['status'] = '01' # 失败
                else:
                    if business_type == '01':  # 用电
                        self.log.info(f'用电')
                        status, order_no, balance = self.handleorder.handle_card_start_order(terminal_address, socket_no, card_sn, deci_card_sn)

                        hex_money = hex(int(balance) * 100)[2:].zfill(8)
                        reverse_hex_money = self.apitool.str_reverse(hex_money)
                        Specific_data_json['status'] = status
                        Specific_data_json['order_no'] = '00000000'
                        Specific_data_json['balance'] = reverse_hex_money

                    elif business_type == '02': # 查余额
                        self.log.info(f'查余额')
                        money = card_info[0].money
                        gift_money = card_info[0].gift_money
                        money = int((money + gift_money) * 100)
                        hex_money = hex(money)[2:].zfill(8)
                        reverse_hex_money = self.apitool.str_reverse(hex_money)

                        self.handleorder.handle_card_stop_order(terminal_address, socket_no, card_sn, deci_card_sn)

                        Specific_data_json['status'] = '00'
                        Specific_data_json['order_no'] = '00000000'
                        Specific_data_json['balance'] = reverse_hex_money

                    elif business_type == '03':  # 停
                        pass
                    else:
                        self.log.error(f'失败：未知原因')
                    return Specific_data_json
            elif not is_exist:
                self.log.error(f'失败：设备{terminal_address}未注册！')
                return None
        else:
            return None
    def get_func2(self, AFN, Fn):
        """
        匹配接口
        :param dict_data: 解包后的数据
        :return: 对应的接口
        """
        Function_mapping = {
            '02': {   # 充电桩主动发送，需要返回
                '01': self.login_special_data
            },
            '0E': {  # 充电桩主动数据上报
                '04': self.report_Card_record_special_data
            }
        }
        try:
            func = Function_mapping[AFN].get(Fn)
        except KeyError:
            self.log.error(f"接口匹配失败，找不到接口！", exc_info=True)
            return None

        if func:
            self.log.info(f"接口匹配成功！")
            return func
        elif func is None:
            self.log.error(f"special_data接口匹配失败，找不到接口！")
            return None


    def get_special_data(self, recv_dict):  # 目前只有登录密码值、数据上报的刷卡用电记录 这两个需要
        AFN = recv_dict['app_region'].get('app_region_function_code')
        Fn = recv_dict['app_region']['Data_unit_identification'].get('Fn')
        # terminal_address = recv_dict['address_region'].get('address_term_r', '')
        if not all([AFN, Fn]):
            self.log.error(f'报文缺少AFN或Fn')
        func = self.get_func2(AFN, Fn)
        if func is None:
            return 'special_data'
        special_data = func(recv_dict)
        self.log.info(f'special_data组包{func}返回的结果:{special_data}')
        return special_data

    # 是否把命令保存到数据库中
    # def is_save_cmd_db(self, AFN, Fn):
    #     map_dict = {
    #         '0420': '插座启停',
    #         '0401': '设置通信参数',
    #         '0402': '设置域名端口',
    #         '0417': '设置功率阈值',
    #         '0418': '设置结算配置',
    #         '0419': '设置充电桩启停',
    #         '0421': '二维码下发',
    #         '0A01': '查询通信参数',
    #         '0A02': '查询域名端口',
    #         '0A03': '查询信号强度',
    #         '0A17': '查询功率阈值',
    #         '0A18': '查询结算配置',
    #         '0A19': '查询充电桩状态',
    #         '0A20': '查询插座状态',
    #         '0A21': '查询二维码',
    #         '0A41': '查询充电桩累计电量',
    #     }
    #     AFN_Fn = AFN + Fn
    #     if AFN_Fn in map_dict:
    #         return True, map_dict[AFN_Fn]
    #     else:
    #         return False, None
    #
    # def save_cmd_db(self, active_station, req_cmd, AFN, Fn, cmd_type):
    #     term_address = req_cmd['address_region'].get('address_term_r')
    #     PR_SEQ = req_cmd['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')
    #     api_code = AFN + Fn
    #     SCmdInfo.objects.create(
    #         term_address=term_address,
    #         PR_SEQ=PR_SEQ,
    #         active_station=active_station,
    #         api_code=api_code,
    #         cmd_type=cmd_type,
    #         req_cmd=json.dumps(req_cmd),
    #         resp_status='0',
    #         update_status='0',
    #         req_time=datetime.datetime.now()
    #     )

    # def upd_online_info(self, ):
