#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：api_func.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/24 11:39 
@Description :  组包接口
'''
import copy

from tools.ApiTool import ApiTool
# from logUtils import log
from tools.strTool import split_string, generate_random_string
from tools.crc import calculate_crc16_modbus

# from utils import publog, pubpara
# log, fh = publog.loger_init(pubpara.log_name_tran)



# from utils.blog.handle import JaeLogManager
#
# log = JaeLogManager('api').get_logger_and_add_handlers(
#     log_filename='api', log_file_handler_type=2,
# )


class ApiFunc:
    def __init__(self, log):
        self.apitool = ApiTool(log)
        self.log = log
        self.head = '68'
        self.tail = '16'
        self.MSA = 'AB'
        self.address_term = ''  #终端地址
        self.app_head_para_format = {
            'control_json': {
                'DIR': 'S2T',   # 传输方向
                'PRM': 'active',   # 是主动站还是被动站：passive
                'feature_code': '10'  # 功能码，用到的很少，写死
            },
            'address_json': {
                'terminal_address': '10000808',  # 终端地址，8位，正序，高位在前，低位在后
                'MSA': 'AB'                      # 先写死
            },
            'AFN': '02',                        # 功能码，一共四类 02、04、0A、0E
            'SEQ': {
                'is_PR_SEQ': '0',
                'PR_SEQ': '',
                'is_TPV': True  # 是否带时间标签
            },
            'data_unit_json': {
                'DA_Pn': '00',                  # 不知道有啥用，0表示终端本身，非0表示具体的设备
                'DT_Fn': '04'                   # 接口码
            }
        }

    # （1）链路接口——登录
    def Link_interface_resp_login(self, recv_data, special_data):
        self.log.info(f'登录')
        self.log.info(f'Link_interface_resp_login接收的数据：{recv_data}')
        try:
            # # s2c、从动站、功能码和与终端发送的保持一致
            # control_area = '0000' + recv_data['control_region'].get('control_region_bin', '')[4:]
            # control_region = hex(int(control_area, 2)).replace('0x', '').zfill(2).upper()
            # address_region = recv_data['address_region'].get('address_term', '') + self.MSA
            # AFN = recv_data['app_region'].get('app_region_function_code', '')
            #
            # #帧序列域
            # SEQ_bin = self.apitool.generate_SEQ(is_TPV=True) # 响应的报文，是否有时间标签
            # SEQ = hex(int(SEQ_bin, 2)).replace('0x', '').upper() # 先把二进制转换成十进制，再 转成十六进制
            # # 数据单元标识
            # Data_unit_identification = recv_data['app_region']['Data_unit_identification'].get('Data_unit_identification_', '')

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, True)
            app_head = self.apitool.generate_app_head(app_head_paras)

            # 从传入参数中获取密码
            # original_password = special_data.get('password')
            # 密码
            original_password = '0x30201228'
            terminal_address = recv_data['address_region'].get('address_term', '')
            # random_number = '0x' + generate_random_string(8, include_lowercase=False) #生成随机数
            random_number = "0x12345678"
            password_string = self.apitool.encrypt_password(original_password, terminal_address, random_number)
            terminal_clock_bcd, terminal_clock_hex = self.apitool.current_time_bcd()
            self.log.info(f"app_head:{app_head}, password_string:{password_string}, terminal_clock_bcd:{terminal_clock_hex.get('完整时间', '')}")
            user_data_area = app_head + password_string + terminal_clock_hex.get('完整时间', '')
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            #转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （2）链路接口——退出登录
    def Link_interface_resp_logout(self, recv_data, special_data):
        try:
            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （3）链路接口——心跳
    def Link_interface_resp_heartbeat(self, recv_data, special_data):
        try:
            # 45秒心跳一次
            self.log.info(f'心跳')
            self.log.info(f'Link_interface_resp_login_verify接收的数据：{recv_data}')
            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, True)
            app_head = self.apitool.generate_app_head(app_head_paras)

            terminal_clock_bcd, terminal_clock_hex = self.apitool.current_time_bcd()
            user_data_area = app_head + terminal_clock_hex.get('完整时间', '')

            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （4）链路接口——登录验证
    def Link_interface_resp_login_verify(self, recv_data, special_data):
        try:
            self.log.info(f'登录验证')
            self.log.info(f'Link_interface_resp_login_verify接收的数据：{recv_data}')
            Specific_data = recv_data['app_region'].get('Specific_data', '')
            self.log.info(f'Specific_data密码段:{Specific_data}')
            if Specific_data is None or len(Specific_data) != 16: # 如果应用层数据中 没有特殊数据，就返回none
                self.log.info(f'无密码，或密码段长度不对，报文错误')
                return None, False

            # 解析出原密码
            str_list = split_string(Specific_data, 8) # 把密码端分成两部分，加密和随机数
            term_addr = recv_data['address_region'].get('address_term', '')
            password = self.apitool.decrypt_password(str_list[0], term_addr, str_list[1])
            self.log.info(f'password:{password}')

            # app_head = self.apitool.generate_data_app_head(recv_data, True)

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, True)
            app_head = self.apitool.generate_app_head(app_head_paras)

            # Specific_data：
            terminal_clock_bcd, terminal_clock_hex = self.apitool.current_time_bcd()
            # 整个用户数据
            user_data_area = app_head + terminal_clock_hex.get('完整时间', '')
            self.log.info(f'user_data_area:{user_data_area}')
            # 三步：计算长度、计算crc、组装
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （1）设置参数——七合一  设置的结果
    def Set_parameters_resp(self, recv_data):
        """
        设置参数的接口，服务器作为启动站，接收到的报文是一个参数设置结果的状态
        数据区内容固定为：1字节
        确认状态：0表示确认成功，1表示不支持此功能，2表示设备忙
        :param recv_data:
        :return: 执行结果成功与否的信息
        """
        self.log.info(f'参数设置结果')
        self.log.info(f'Set_parameters接收的数据:{recv_data}')
        try:
            # 先判断是哪个接口
            AFN = recv_data['app_region'].get('app_region_function_code')

            Fn = recv_data['app_region']['Data_unit_identification'].get('Fn', '')
            data = {
                '01': '通信参数',
                '02': '域名端口',
                '17': '插座功率阈值',
                '18': '结算配置',
                '19': '充电桩启停',
                '20': '插座远程启停',
                '21': '二维码'
            }
            api_name = data.get(Fn, '')
            if AFN != '04' or api_name == '':
                self.log.error(f'AFN = {AFN}中,没有Fn = {Fn}的接口！')
                return None, False

            result = int(recv_data['app_region'].get('Specific_data'), 16)
            if result == 0:
                self.log.info(f'******{api_name}******：执行成功！')
            if result == 1:
                self.log.info(f'******{api_name}******：不支持此功能！')
            if result == 3:
                self.log.info(f'******{api_name}******：设备忙！')
            return result, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # 查询的结果
    # (1)查询参数——通信参数 F1   查询的结果
    def Query_parameters_Commu_para(self, recv_data):
        self.log.info(f'查询参数——通信参数')
        self.log.info(f'Query_parameters_Commu_para接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 14: # 七个字节，即七个十六进制，其字符串长度为14
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 心跳周期 # 十六进制转成十进制
            heart_cycle = int(result[2:6], 16)
            # (3) 上送周期 # 十六进制转成十进制
            up_cycle = int(result[6:10], 16)
            # (4) 充满延时 # 十六进制转成十进制
            delay_time = int(result[10:14], 16)

            result_dict = {
                'status': status,
                'heart_cycle': heart_cycle,
                'up_cycle': up_cycle,
                'delay_time': delay_time
            }
            self.log.info(f'查询参数：通信参数result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (2)查询参数——域名端口 F2
    def Query_parameters_Domain_port(self, recv_data):
        self.log.info(f'查询参数——域名端口')
        self.log.info(f'Query_parameters_Domain_port接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            # 这个因为域名长度不定，所不能判断长度

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 域名长度 # 十六进制转成十进制
            domain_len = int(result[2:4], 16)
            # (3) 域名信息 # ASCII码
            domain = result[4:-4]
            # (4) 端口号
            port = result[-4:]
            port_hex = self.apitool.str_reverse(port)
            port = int(port_hex, 16)

            result_dict = {
                'status': status,
                'domain_len': domain_len,
                'domain': domain,
                'port': port
            }
            self.log.info(f'查询参数：域名端口result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (3)查询参数——信号强度 F3
    def Query_parameters_Signal_strength(self, recv_data):
        self.log.info(f'查询参数——信号强度')
        self.log.info(f'Query_parameters_Signal_strength接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 4:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 信号强度值 # 十六进制转成十进制
            Signal_strength = int(result[2:4], 16)

            result_dict = {
                'status': status,
                'Signal_strength': Signal_strength,
            }
            self.log.info(f'查询参数：信号强度result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (4)查询参数——插座功率阈值 F17
    def Query_parameters_Power_threshold(self, recv_data):
        self.log.info(f'查询参数——插座功率阈值')
        self.log.info(f'Query_parameters_Power_threshold接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 10:  # 五个字节
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 最小功率 # 十六进制转成十进制
            min_power = result[2:6]
            min_power = self.apitool.str_reverse(min_power)
            min_power = int(min_power, 16)
            # (3) 最大功率 # 十六进制转成十进制
            max_power = result[6:10]
            max_power = self.apitool.str_reverse(max_power)
            max_power = int(max_power, 16)

            result_dict = {
                'status': status,
                'min_power': min_power,
                'max_power': max_power,
            }
            self.log.info(f'查询参数：插座功率阈值result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (5)查询参数——结算配置 F18
    def Query_parameters_Settle_allocation(self, recv_data):
        self.log.info(f'查询参数——结算配置')
        self.log.info(f'Query_parameters_Settle_allocation接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 12:  # 四个字节
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 计量模式 # 十六进制转成十进制
            measure_model = int(result[2:4], 16)
            # (3) 小时电价 # 十六进制转成十进制
            Hourly_price = result[4:8]
            Hourly_price = self.apitool.str_reverse(Hourly_price)
            Hourly_price = int(Hourly_price, 16)
            # (4) 费率时长 # 十六进制转成十进制
            Rate_duration = result[8:12]
            Rate_duration = self.apitool.str_reverse(Rate_duration)
            Rate_duration = int(Rate_duration, 16)

            result_dict = {
                'status': status,
                'measure_model': measure_model,
                'Hourly_price': Hourly_price,
                'Rate_duration': Rate_duration,
            }
            self.log.info(f'查询参数：插座功率阈值result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (6)查询参数——充电桩状态 F19
    def Query_parameters_Pile_status(self, recv_data):
        self.log.info(f'查询参数——结算配置')
        self.log.info(f'Query_parameters_Pile_status接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 4:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 状态 # 十六进制转成十进制
            pile_status = result[2:4]

            result_dict = {
                'status': status,
                'pile_status': pile_status,
            }
            self.log.info(f'查询参数：充电桩状态result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (7)查询参数——插座状态 F20
    def Query_parameters_Socket_status(self, recv_data):
        self.log.info(f'查询参数——插座状态')
        self.log.info(f'Query_parameters_Socket_status接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 插座数量 # 十六进制转成十进制
            count = int(result[2:4], 16)
            # 获取到数量后，判断长度
            byte_len = 2 + count
            if len(result) != byte_len * 2:
                self.log.info(f'数据单元长度不正确')
                return None, False
            socket_status = result[4:]
            socket_list = split_string(socket_status, 2)

            result_dict = {
                'status': status,
                'count': count
            }
            i = 0
            for socket in socket_list:
                i = i + 1
                result_dict[i] = int(socket, 16)

            self.log.info(f'查询参数：插座状态result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (8)查询参数——二维码 F21
    def Query_parameters_QRcode(self, recv_data):
        self.log.info(f'查询参数——二维码')
        self.log.info(f'Query_parameters_QRcode接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')


            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 二维码长度 # 十六进制转成十进制
            QR_len = result[2:4]
            # (3) 二维码内容 # ASCII编码
            QR_data = result[4:]

            result_dict = {
                'status': status,
                'QR_len': QR_len,
                'QR_data': QR_data
            }
            self.log.info(f'查询参数：二维码result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (8)查询参数——充电桩累计电量 F41
    def Query_parameters_Total_electricity(self, recv_data):
        self.log.info(f'查询参数——充电桩累计电量')
        self.log.info(f'Query_parameters_Total_electricity接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            # 检查长度
            if len(result) != 10:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None, False

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 二维码长度 # 十六进制转成十进制
            total_electricity = result[2:10]

            result_dict = {
                'status': status,
                'total_electricity': total_electricity
            }
            self.log.info(f'查询参数：充电桩累计电量result_dict{result_dict}')

            return result_dict, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)


    # 数据上报
    def Data_report_name_name(self):
        pass


    def Data_report_resp_SIM_card_data(self, recv_data, special_data):
        self.log.info(f'SIM卡信息数据')
        self.log.info(f'Data_report_resp_SIM_card_data接收的数据:{recv_data}')
        try:
            # 对卡号进行处理
            card_data = recv_data['app_region'].get('Specific_data', '')
            byte_card_data = self.apitool.HexToByte(card_data)
            card_length = byte_card_data[0]
            card_number = int(byte_card_data[1:])
            self.log.info(f'card_length:{card_length},\ncard_number:{card_number}')

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, True

        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    def Data_report_resp_Socket_Status(self, recv_data, special_data):
        self.log.info(f'插座实时状态')
        self.log.info(f'Data_report_resp_Socket_Status接收的数据:{recv_data}')
        try:
            # 对插座进行处理
            sockets_data = recv_data['app_region'].get('Specific_data', '')
            # 插座数量
            socket_counts = sockets_data[0:2]
            self.log.info(f'插座数量:{int(socket_counts, 16)}')
            socket_str = sockets_data[2:] # 这是去掉插座数量后的插座信息字符串。
            # 每条插座信息由10个字节组成， 即20个十六进制位
            socket_list = split_string(socket_str, 20)
            self.log.info(f'插座列表:{socket_list}')
            sockets_dict = {}
            for item in socket_list:
                socket_num = item[0:2]
                electricity_status = item[2:4] # 0起始，1充电中，2结束充电，3未充上电
                order_num = item[4:12]
                power = item[12:16]
                electric_quantity = item[16:]
                dict = {
                    'electricity_status': electricity_status,
                    'order_num': order_num,
                    'power': power,
                    'electricity_quantity': electric_quantity
                }
                sockets_dict[socket_num] = dict
            self.log.info(f'插座状态sockets_dict:{sockets_dict}')

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False

            # return b'report Socket Status is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)


    def Data_report_resp_Geog_posi(self, recv_data, special_data):
        self.log.info(f'地理位置')
        self.log.info(f'Data_report_resp_Geog_posi接收的数据:{recv_data}')
        try:

            geography_data = recv_data['app_region'].get('Specific_data', '')
            # 坐标类型
            coordinate_type = geography_data[0:2]
            self.log.info(f'坐标类型(0:GPS,1:基站定位):{int(coordinate_type, 16)}')
            longitude_len = geography_data[2:4] # 经度长度
            longitude = geography_data[4:4 + longitude_len]
            latitude_len = geography_data[4 + longitude_len, 6 + longitude_len]
            latitude = geography_data[6 + longitude_len, 6 + longitude_len + latitude_len]

            geography_dict = {
                'coordinate_type': coordinate_type,
                'longitude_len': longitude_len,
                'longitude': longitude,
                'latitude_len': latitude_len,
                'latitude': latitude
            }

            self.log.info(f'地理位置信息geography_dict:{geography_dict}')

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False

            # return b'Data_report_resp_Geog_posi is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)


    def Data_report_resp_Card_record(self, recv_data, special_data):
        self.log.info(f'刷卡用电记录')
        self.log.info(f'Data_report_resp_Card_record接收的数据:{recv_data}')
        try:
            # app_head = self.apitool.generate_data_app_head(recv_data, True)
            record_data = recv_data['app_region'].get('Specific_data', '')
            # 坐标类型
            business_type = record_data[0:2]
            self.log.info(f'业务类型(1:用电,2:查询,3:停电):{int(business_type, 16)}')
            socket_no = record_data[2:4] # 插座序号
            card_sn = record_data[4:12] # 卡序列号

            record_dict = {
                'socket_no': socket_no,
                'card_sn': card_sn
            }

            self.log.info(f'刷卡用电记录record_dict:{record_dict}')

            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            # special_data,在这里获取、计算Specific_data_json中的所有键值

            # 数据单元
            Specific_data_json = {
                'status': '01',  # 确认状态,1字节
                'buiness_type': business_type,  # 业务类型,1字节
                'socket_no': socket_no,  # 插座序号
                'order_no': '01020304',  # 订单号,4字节
                'balance': '01020304'  # 卡余额,4字节
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            self.log.info(f'user_data_area:{user_data_area}')
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, False

        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)


    def Data_report_resp_Breakdown_record(self, recv_data, special_data):
        self.log.info(f'故障记录')
        self.log.info(f'Data_report_resp_Breakdown_record接收的数据:{recv_data}')
        try:

            record_data = recv_data['app_region'].get('Specific_data', '')
            # 插座序号
            socket_no = record_data[0:2]
            breakdown_type = record_data[2:4] # 卡序列号

            record_dict = {
                'socket_no': socket_no,
                'breakdown_type': breakdown_type
            }

            self.log.info(f'故障记录record_dict:{record_dict}')
            # 生成头部报文，终端为主动站，直接通过它的报文生成
            app_head_paras = self.apitool.get_app_head_paras_from_recv_dict(recv_data, False)
            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False

            # return b'Data_report_resp_Breakdown_record is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    '''
        json_data = {
            'number': '0A02',
            'terminal_address': '10000808',
            'Special_data': {}
        }
    '''
    # (1)设置参数——插座启停 F20
    def Set_parameters_req_Socket_start_stop(self, json):
        try:
            self.log.info(f'主动发送：设置参数——插座启停:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})  # 获取完还要计算

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)

            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',  # 随便写的
            #     'AFN': '04', # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001 PSEQ:1001
            #     'Data_unit_identification': '001400', # DA:00, DT:20 00  F20 # 这里DA：00表示终端本身，不太明白
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            # Specific_data_json = {
            #     'SocketNumber': '00',
            #     'OrderNumber': '00FE1F00',
            #     'electrovalence': '0050',
            #     'type': '00', # 00：金额，01：时间
            #     'DurationOrAmount': '0050', #
            #     # 'Unknown': '0023292022E522'
            # }
            # 特殊数据
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # data = 'C9080800100C04EE00140000FE1F0000820001050023292022E522'
            # data = 'C9080080010AB044900200000CD0000EF0050'
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （2）设置参数——通信参数 F1
    def Set_parameters_req_Commu_para(self, json):
        try:
            self.log.info(f'主动发送：设置参数——通信参数:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)
            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04',  # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '000100', # DA:00, DT:01 00  F1
            # }
            # app_head = ''.join(app_head_json.values())
            #
            # # 数据单元
            # heart_cycle = hex(5).replace('0x', '').zfill(4).upper()
            #
            # Specific_data_json = {
            #     'heart_cycle': heart_cycle,  # 心跳周期
            #     'uplink_interval': heart_cycle, # 上送间隔
            #     'delay_time': heart_cycle,
            # }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data

            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)


    # (3) 设置参数——域名端口 F2
    def Set_parameters_req_Domain_port(self, json):
        try:
            self.log.info(f'主动发送：设置参数——域名端口:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)
            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04', # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '000200', # DA:00, DT:02 00  F2
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            # todo 端口反转,端口长度待验证
            # 已处理：长度不包括端口、端口要先转成十六进制，再反转
            # 为了Speciafic_data里的数据统一--接口的所有特殊数据，把长度也传进去
            # 1)域名
            domain = Specific_data_json.get('domian')
            domain_hex = self.apitool.string_to_hex(domain)
            # 2)长度
            length = Specific_data_json.get('length')
            domain_len = hex(length).replace('0x', '').zfill(2).upper()
            # 3)端口
            port = Specific_data_json.get('port')
            port = hex(port).replace('0x', '').zfill(4).upper()
            reversed_port = self.apitool.str_reverse(port)

            Specific_data_json = {
                'domain_len': domain_len,  # 域名长度
                'domain_data': domain_hex,  # 域名信息
                'port': reversed_port,  # 端口号
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (4) 设置参数——功率阈值 F17
    def Set_parameters_req_Power_threshold(self, json):
        try:
            self.log.info(f'主动发送：设置参数——功率阈值:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)
            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04',  # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '001100',  # DA:00, DT:11 00  F17
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            min_power = Specific_data_json.get('min_power')
            max_power = Specific_data_json.get('max_power')
            # todo 功率值是两个十六进制位，是否需要反转
            # 已处理：需要反转
            min_power = hex(min_power).replace('0x', '').zfill(4).upper()
            max_power = hex(max_power).replace('0x', '').zfill(4).upper()

            min_power = self.apitool.str_reverse(min_power)
            max_power = self.apitool.str_reverse(max_power)

            Specific_data_json = {
                'min_power': min_power,  # 最小功率
                'max_power': max_power,  # 最大功率
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (4) 设置参数——结算配置 F18
    def Set_parameters_req_Settle_allocation(self, json):
        try:
            self.log.info(f'主动发送：设置参数——结算配置:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)

            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04',  # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '001200',  # DA:00, DT:12 00  F18
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            Hourly_price = Specific_data_json.get('Hourly_price')
            Rate_duration = Specific_data_json.get('Rate_duration')
            # todo 两个十六进制位，是否需要反转
            # 已处理：需要反转
            Hourly_price = self.apitool.str_reverse(Hourly_price)
            Rate_duration = self.apitool.str_reverse(Rate_duration)
            Hourly_price = hex(Hourly_price).replace('0x', '').zfill(2).upper()
            Rate_duration = hex(Rate_duration).replace('0x', '').zfill(4).upper()

            Specific_data_json = {
                'Hourly_price': Hourly_price,  # 小时电价
                'Rate_duration': Rate_duration,  # 费率时长
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (4) 设置参数——充电桩启停 F19
    def Set_parameters_req_Pile_start_stop(self, json):
        try:
            self.log.info(f'主动发送：设置参数——充电桩启停:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)

            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04',  # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '001300',  # DA:00, DT:13 00  F19
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            # todo 这个状态占一个字节，是否需要填充成两位字符串
            # fixme 这个接口有问题
            status = Specific_data_json.get('status')  # 0停用，1启用

            Specific_data_json = {
                'status': status  # 启停状态
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # (4) 设置参数——二维码下发 F21
    def Set_parameters_req_QRcode_down(self, json):
        try:
            self.log.info(f'主动发送：设置参数——二维码下发:')
            self.log.info(f'{json}')
            # 这个是这个接口固定的json数据

            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            Specific_data_json = json.get('Special_data', {})

            app_head_paras = copy.deepcopy(self.app_head_para_format)  # 获取头部参数模板
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['data_unit_json']['DT_Fn'] = code
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False

            # 生成头部
            app_head = self.apitool.generate_app_head(app_head_paras)

            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '04',  # 设置参数  这个大类接口的功能码 的 AFN 就是04
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '001500',  # DA:00, DT:15 00  F21
            # }
            # app_head = ''.join(app_head_json.values())

            # 数据单元
            RQ_len = Specific_data_json.get('QR_len')
            # todo 字符串转十六进制可能会报错
            # 已处理，不会报错
            QR_len = hex(RQ_len).replace('0x', '').zfill(2).upper()
            QR_data = ''

            Specific_data_json = {
                'QR_len': QR_len,  # 二维码长度
                'QR_data': QR_data  # 二维码内容
            }
            Specific_data = ''.join(Specific_data_json.values())
            user_data_area = app_head + Specific_data
            # 三步：计算长度、计算crc、组合所有片段
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')

            return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # （1）查询参数——九合一
    def Query_parameters_req(self, json):
        try:
            self.log.info(f'此时的终端地址：{self.address_term}')
            number = json.get('number')
            terminal_address = json.get('terminal_address')  # 终端地址
            AFN = number[0:2]
            code = number[2:]
            hex_code = hex(int(code)).replace('0x', '').zfill(2).upper() # 用于组 数据单元标识
            data = {
                '01': '通信参数',
                '02': '域名端口',
                '03': '信号强度',
                '17': '插座功率阈值',
                '18': '结算配置',
                '19': '充电桩状态',
                '20': '插座状态',
                '21': '二维码',
                '41': '充电桩累计电量'
            }
            api_name = data.get(code)
            self.log.info(f'查村参数api_name:{api_name}')

            app_head_paras = copy.deepcopy(self.app_head_para_format)
            app_head_paras['address_json']['terminal_address'] = terminal_address
            app_head_paras['AFN'] = AFN
            app_head_paras['SEQ']['is_TPV'] = False
            app_head_paras['data_unit_json']['DT_Fn'] = code

            app_head = self.apitool.generate_app_head(app_head_paras)

            user_data_area = app_head
            self.log.info(f"user_data_area:{user_data_area}")
            length = self.apitool.length_with_hex(user_data_area)
            crc_decimal = calculate_crc16_modbus(user_data_area)
            crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            self.log.info(f'即将发送的十六进制数据：{resp_data}')

            # 转成字节格式：
            byte_resp_data = self.apitool.HexToByte(resp_data)
            self.log.info(f'byte_resp_data:{byte_resp_data}')
            return byte_resp_data, False

            # app_head_json = {
            #     'control_region': '4A',  # 0100 1010 ：s2c、主动站、请求一级数据
            #     'address_term': self.address_term,
            #     'address_MSA': 'AB',
            #     'AFN': '0A',  # 查询参数  这个大类接口的功能码 的 AFN 就是0A
            #     'SEQ': '69',  # 0110 1001
            #     'Data_unit_identification': '00' + f'{hex_code}' + '00',  # DA:00, DT:15 00  F1
            # }
            # app_head = ''.join(app_head_json.values())
            # log.info(f'app_head:{app_head}')
            #
            # # 数据单元 无
            # Specific_data_json = {
            #
            # }
            # Specific_data = ''.join(Specific_data_json.values())
            # user_data_area = app_head + Specific_data
            # log.info(f'user_data_area:{user_data_area}')
            # # 三步：计算长度、计算crc、组合所有片段
            # length = self.apitool.length_with_hex(user_data_area)
            # crc_decimal = calculate_crc16_modbus(user_data_area)
            # crc = hex(crc_decimal).replace('0x', '').zfill(4).upper()
            # resp_data = self.head + length + self.head + user_data_area + crc + self.tail
            # log.info(f'即将发送的十六进制数据：{resp_data}')
            #
            # # 转成字节格式：
            # byte_resp_data = self.apitool.HexToByte(resp_data)
            # log.info(f'byte_resp_data:{byte_resp_data}')
            #
            # return byte_resp_data, True
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)

    # 服务器作为启动站，接口入口
    # ·todo  传入的json_data 应该包含 终端地址

    """
        json_data = {
            'number': '0A02',
            'terminal_address': '10000808',
            'Special_data': {}
        }
    """
    def get_active_send_data(self, json_data):

        self.log.info(f'主动发报文')
        self.log.info(f'get_avtive_send_data: {json_data}')
        number = json_data.get('number')
        if number is None or len(number) != 4:
            self.log.error("接收的参数为空或有误")
            return None

        Function_mapping = {
            '04': {    # 设置参数
                '01': self.Set_parameters_req_Commu_para,
                '20': self.Set_parameters_req_Socket_start_stop
            },
            '0A': {    # 查询参数
                '01': self.Query_parameters_req,
                '02': self.Query_parameters_req,
                '03': self.Query_parameters_req,
                '17': self.Query_parameters_req,
                '18': self.Query_parameters_req,
                '19': self.Query_parameters_req,
                '20': self.Query_parameters_req,
                '21': self.Query_parameters_req,
                '41': self.Query_parameters_req
            }
        }
        func = Function_mapping[number[0:2]].get(number[2:])
        # json中，除了number(接口代码)，如果有其他参数，也需要填上
        # 改进：在get_active_send_data里，接收一个json,里面包含接口代码和所需参数
        # 普配完接口后，直接把整个json传到相应接口中
        data, status = func(json_data)
        self.log.info(f'type:{type(data)}')
        return data


