#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：充电桩通讯机 
@File    ：MessageReparseFunc.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/19 16:11 
@Description : 报文二次解析接口
'''

from ApiTool import ApiTool
from strTool import split_string, generate_random_string
from crc import calculate_crc16_modbus

# from utils import publog, pubpara
# log, fh = publog.loger_init(pubpara.log_name_tran)

# from utils.blog.handle import JaeLogManager
#
# log = JaeLogManager('api').get_logger_and_add_handlers(
#     log_filename='api', log_file_handler_type=2,
# )


class ReParseFunc:
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
    def Link_interface_login_parse(self, recv_data):
        try:
            self.log.info(f'登录')
            # self.log.info(f'Link_interface_resp_login, 接收的数据：{recv_data}')
            dict_data = {
                'login': "登录无数据体"
            }
            return dict_data
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None
    # （2）链路接口——退出登录
    def Link_interface_logout_parse(self, recv_data):
        try:
            self.log.info(f'退出登录')
            # self.log.info(f'Link_interface_resp_logout：{recv_data}')
            dict_data = {
                'logout': "退出登录无数据体"
            }
            return dict_data
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # （3）链路接口——心跳
    def Link_interface_heartbeat_parse(self, recv_data):
        try:
            # 45秒心跳一次
            self.log.info(f'心跳')
            # self.log.info(f'Link_interface_resp_login_verify, 接收的数据：{recv_data}')
            dict_data = {
                'heartbeat': "心跳无数据体"
            }

            return dict_data
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # （4）链路接口——登录验证
    def Link_interface_login_verify_parse(self, recv_data):
        try:
            self.log.info(f'登录验证')
            # self.log.info(f'Link_interface_login_verify_parse, 接收的数据：{recv_data}')
            Specific_data = recv_data['app_region'].get('Specific_data', '')
            if Specific_data is None or len(Specific_data) != 16: # 如果应用层数据中 没有特殊数据，就返回none
                self.log.info(f'Specific_data密码段:{Specific_data}')
                self.log.info(f'无密码，或密码段长度不对，报文错误')
                return None

            # 解析出原密码
            str_list = split_string(Specific_data, 8) # 把密码端分成两部分，加密和随机数
            term_addr = recv_data['address_region'].get('address_term', '')
            password = self.apitool.decrypt_password(str_list[0], term_addr, str_list[1])
            self.log.info(f'password:{password}, random_num:{str_list[1]}')
            dict_data = {
                'password': password,
                'random_num': str_list[1]
            }
            return dict_data

        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # （1）设置参数——七合一  设置的结果
    def Set_parameters_parse(self, recv_data):
        """
        设置参数的接口，服务器作为启动站，接收到的报文是一个参数设置结果的状态
        数据区内容固定为：1字节
        确认状态：0表示确认成功，1表示不支持此功能，2表示设备忙
        :param recv_data:
        :return: 执行结果成功与否的信息
        """
        self.log.info(f'参数设置结果')
        # self.log.info(f'Set_parameters_parse, 接收的数据:{recv_data}')
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
                return None

            result = int(recv_data['app_region'].get('Specific_data'), 16)
            dict_data = {
                'set_param_result': result
            }
            if result == 0:
                self.log.info(f'******{api_name}******：执行成功！')
            if result == 1:
                self.log.info(f'******{api_name}******：不支持此功能！')
            if result == 3:
                self.log.info(f'******{api_name}******：设备忙！')

            return dict_data
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None


    # 查询的结果
    # (1)查询参数——通信参数 F1   查询的结果
    def Query_parameters_Commu_para_parse(self, recv_data):
        self.log.info(f'查询参数——通信参数')
        # self.log.info(f'Query_parameters_Commu_para_parse, 接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 14: # 七个字节，即七个十六进制，其字符串长度为14
                self.log.error(f'数据单元长度不正确')
                return None

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 心跳周期 # 十六进制转成十进制
            # 反转一下
            heart_cycle_ = self.apitool.str_reverse(result[2:6])
            heart_cycle = int(heart_cycle_, 16)
            # (3) 上送周期 # 十六进制转成十进制
            up_cycle_ = self.apitool.str_reverse(result[6:10])
            up_cycle = int(up_cycle_, 16)
            # (4) 充满延时 # 十六进制转成十进制
            delay_time_ = self.apitool.str_reverse(result[10:14])
            delay_time = int(delay_time_, 16)

            result_dict = {
                'status': status,
                'heart_cycle': heart_cycle,
                'up_cycle': up_cycle,
                'delay_time': delay_time
            }
            self.log.info(f'查询参数：通信参数result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (2)查询参数——域名端口 F2
    def Query_parameters_Domain_port_parse(self, recv_data):
        self.log.info(f'查询参数——域名端口')
        # self.log.info(f'Query_parameters_Domain_port接收的数据:{recv_data}')
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
            domain = self.apitool.hex_to_str(domain)
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

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (3)查询参数——信号强度 F3
    def Query_parameters_Signal_strength_parse(self, recv_data):
        self.log.info(f'查询参数——信号强度')
        # self.log.info(f'Query_parameters_Signal_strength接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 4:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 信号强度值 # 十六进制转成十进制
            Signal_strength = int(result[2:4], 16)

            result_dict = {
                'status': status,
                'Signal_strength': Signal_strength,
            }
            self.log.info(f'查询参数：信号强度result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (4)查询参数——插座功率阈值 F17
    def Query_parameters_Power_threshold_parse(self, recv_data):
        self.log.info(f'查询参数——插座功率阈值')
        # self.log.info(f'Query_parameters_Power_threshold接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 10:  # 五个字节
                self.log.error(f'数据单元长度不正确')
                return None

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

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (5)查询参数——结算配置 F18
    def Query_parameters_Settle_allocation_parse(self, recv_data):
        self.log.info(f'查询参数——结算配置')
        # self.log.info(f'Query_parameters_Settle_allocation接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 12:  # 四个字节
                self.log.error(f'数据单元长度不正确')
                return None

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

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (6)查询参数——充电桩状态 F19
    def Query_parameters_Pile_status_parse(self, recv_data):
        self.log.info(f'查询参数——结算配置')
        # self.log.info(f'Query_parameters_Pile_status接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            if len(result) != 4:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 状态 # 十六进制转成十进制
            pile_status = result[2:4]

            result_dict = {
                'status': status,
                'pile_status': pile_status,
            }
            self.log.info(f'查询参数：充电桩状态result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (7)查询参数——插座状态 F20
    def Query_parameters_Socket_status_parse(self, recv_data):
        self.log.info(f'查询参数——插座状态')
        # self.log.info(f'Query_parameters_Socket_status接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 插座数量 # 十六进制转成十进制
            count = int(result[2:4], 16)
            # 获取到数量后，判断长度
            byte_len = 1 + count
            if len(result) != byte_len * 4:
                self.log.info(f'数据单元长度不正确')
                return None
            socket_status = result[4:]
            socket_list = split_string(socket_status, 4)

            result_dict = {
                'status': f'{status}',
                'count': count
            }
            for socket in socket_list:

                result_dict[socket[0:2]] = socket[2:4]

            self.log.info(f'查询参数：插座状态result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (8)查询参数——二维码 F21
    def Query_parameters_QRcode_parse(self, recv_data):
        self.log.info(f'查询参数——二维码')
        # self.log.info(f'Query_parameters_QRcode接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 二维码长度 # 十六进制转成十进制
            QR_len = result[2:4]
            # (3) 二维码内容 # ASCII编码
            QR_data = result[4:]
            QR_data = self.apitool.hex_to_str(QR_data)

            result_dict = {
                'status': status,
                'QR_len': QR_len,
                'QR_data': QR_data
            }
            self.log.info(f'查询参数：二维码result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    # (8)查询参数——充电桩累计电量 F41
    def Query_parameters_Total_electricity_parse(self, recv_data):
        self.log.info(f'查询参数——充电桩累计电量')
        # self.log.info(f'Query_parameters_Total_electricity接收的数据:{recv_data}')
        try:
            # 先获取查询的结果
            result = recv_data['app_region'].get('Specific_data')
            # 检查长度
            if len(result) != 12:  # 两个字节
                self.log.error(f'数据单元长度不正确')
                return None

            # (1) 查询状态
            status = int(result[0:2])  # 一个字节
            # (2) 二维码长度 # 十六进制转成十进制
            total_electricity = result[2:12]

            result_dict = {
                'status': status,
                'total_electricity': total_electricity
            }
            self.log.info(f'查询参数：充电桩累计电量result_dict{result_dict}')

            return result_dict
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)





    def Data_report_SIM_card_data_parse(self, recv_data):
        self.log.info(f'SIM卡信息数据')
        # self.log.info(f'Data_report_resp_SIM_card_data接收的数据:{recv_data}')
        try:
            # 对卡号进行处理
            card_data = recv_data['app_region'].get('Specific_data', '')
            byte_card_data = self.apitool.HexToByte(card_data)
            card_length = byte_card_data[0]
            card_number = byte_card_data[1:].decode('utf-8')
            self.log.info(f'card_length:{card_length},\ncard_number:{card_number}')
            SIM_card_info = {
                'card_length': card_length,
                'card_number': card_number
            }
            self.log.info(f'SIM_card_info:{SIM_card_info}')
            return SIM_card_info

        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None

    def Data_report_Socket_Status_parse(self, recv_data):
        self.log.info(f'插座实时状态')
        # self.log.info(f'Data_report_resp_Socket_Status接收的数据:{recv_data}')
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
            sockets_dict = {
                'socket_counts': socket_counts
            }
            for item in socket_list:
                socket_num = item[0:2]
                electricity_status = item[2:4] # 0起始，1充电中，2结束充电，3未充上电
                order_num = item[4:12]
                power_ = item[12:16]
                power_reverse = self.apitool.str_reverse(power_)
                power_int = int(power_reverse, 16)
                power = f'{power_int:.1f}'
                electric_quantity_ = item[16:]
                electric_quantity_reverse = self.apitool.str_reverse(electric_quantity_)
                electric_quantity_int = int(electric_quantity_reverse, 16) / 100
                electric_quantity = f'{electric_quantity_int:.2f}'
                dict = {
                    'electricity_status': electricity_status,
                    'order_num': order_num,
                    'power': power,
                    'electricity_quantity': electric_quantity
                }
                sockets_dict[socket_num] = dict
            self.log.info(f'插座状态sockets_dict:{sockets_dict}')


            return sockets_dict

            # return b'report Socket Status is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None


    def Data_report_Geog_posi_parse(self, recv_data):
        self.log.info(f'地理位置')
        # self.log.info(f'Data_report_resp_Geog_posi接收的数据:{recv_data}')
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


            return geography_dict

            # return b'Data_report_resp_Geog_posi is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None


    def Data_report_Card_record_parse(self, recv_data):
        self.log.info(f'刷卡用电记录')
        # self.log.info(f'Data_report_resp_Card_record接收的数据:{recv_data}')
        try:
            # app_head = self.apitool.generate_data_app_head(recv_data, True)
            record_data = recv_data['app_region'].get('Specific_data', '')
            # 坐标类型
            business_type = record_data[0:2]
            self.log.info(f'业务类型(1:用电,2:查询,3:停电):{int(business_type, 16)}')
            socket_no = record_data[2:4] # 插座序号
            card_sn = record_data[4:12] # 卡序列号
            card_sn_rev = self.apitool.str_reverse(card_sn)


            record_dict = {
                'business_type': business_type,
                'socket_no': socket_no,
                'card_sn': card_sn_rev
            }

            self.log.info(f'刷卡用电记录record_dict:{record_dict}')

            return record_dict

        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None


    def Data_report_Breakdown_record_parse(self, recv_data):
        self.log.info(f'故障记录')
        # self.log.info(f'Data_report_resp_Breakdown_record接收的数据:{recv_data}')
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

            return record_dict

            # return b'Data_report_resp_Breakdown_record is OK', False
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return None


    def crc16_verify(self, dict_data):
        """
        crc校验
        :param dict_data:
        :return:
        """
        user_data_region = dict_data['user_data_region']
        crc16_ = calculate_crc16_modbus(user_data_region)
        crc16 = hex(crc16_)[2:].upper().zfill(4)
        # self.log.info(f'CRC16: {crc16}')
        if not (crc16 == dict_data.get('real_crc') or crc16 == dict_data.get('crc_str')):
            self.log.error(f"crc校验失败：计算crc:{crc16}, 接收crc:{dict_data.get('real_crc')}")
            return False
        # self.log.info(f"crc校验通过：计算crc:{crc16}, 接收crc:{dict_data.get('real_crc')}")
        return True

    def get_parse_func(self, AFN, Fn):
        """
        匹配接口
        :param dict_data: 解包后的数据
        :return: 对应的接口
        对于服务器为主动站的情况，终端发过来的数据，还用原来的方式，通过api_func来返回
        这里只用来解析终端主动上报的数据
        """
        Function_mapping = {
            '02': {
                '01': self.Link_interface_login_parse,
                '02': self.Link_interface_logout_parse,
                '03': self.Link_interface_heartbeat_parse,
                '04': self.Link_interface_login_verify_parse
            },
            '04': {
                '01': self.Set_parameters_parse,
                '02': self.Set_parameters_parse,
                '17': self.Set_parameters_parse,
                '18': self.Set_parameters_parse,
                '19': self.Set_parameters_parse,
                '20': self.Set_parameters_parse,
                '21': self.Set_parameters_parse

            },
            '0A': {
                '01': self.Query_parameters_Commu_para_parse,
                '02': self.Query_parameters_Domain_port_parse,
                '03': self.Query_parameters_Signal_strength_parse,
                '17': self.Query_parameters_Power_threshold_parse,
                '18': self.Query_parameters_Settle_allocation_parse,
                '19': self.Query_parameters_Pile_status_parse,
                '20': self.Query_parameters_Socket_status_parse,
                '21': self.Query_parameters_QRcode_parse,
                '41': self.Query_parameters_Total_electricity_parse
            },
            '0E': {
                '01': self.Data_report_SIM_card_data_parse,
                '02': self.Data_report_Geog_posi_parse,
                '03': self.Data_report_Socket_Status_parse,
                '04': self.Data_report_Card_record_parse,
                '05': self.Data_report_Breakdown_record_parse
            }
        }

        func = Function_mapping[AFN].get(Fn)
        if func:
            # self.log.info(f"接口匹配成功！")
            return func
        elif func is None:
            self.log.error(f"接口匹配失败，找不到接口！ AFN={AFN},Fn={Fn}")
            return None


    def Message_Reparsing(self, dict_data):
        '''
        用来解析特殊数据
        :param dict_data: 初步解析后的报文
        :return:
        '''
        try:
            # self.log.info(f'*************二次解包************')
            #  crc校验
            crc_result = self.crc16_verify(dict_data)
            if not crc_result:
                # self.log.error(f'crc校验失败')
                return False

            # 匹配接口
            AFN = dict_data['app_region'].get('app_region_function_code')
            Fn = dict_data['app_region']['Data_unit_identification'].get('Fn')
            terminal_address = dict_data['address_region'].get('address_term_r', '')
            if not all([AFN, Fn]):
                self.log.error(f'报文缺少AFN或Fn')
            func = self.get_parse_func(AFN, Fn)

            resp_data = func(dict_data)
            # self.log.info(f'二次解析接口{func}返回的结果:{resp_data}')
            return terminal_address, resp_data

        except Exception as e:
            self.log.error("二次解包失败! %s" % str(e), exc_info=True)
            return False







