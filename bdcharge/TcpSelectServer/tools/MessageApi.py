#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：MessageApi.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/23 18:02 
@Description : 解包、组包
'''
import json

from tools.ApiTool import ApiTool
from tools.strTool import split_string, generate_random_string
from tools.crc import calculate_crc16_modbus
from tools.api_func import ApiFunc
from utils import publog, pubpara


class Message:
    def __init__(self, log):
        self.log = log
        self.apitool = ApiTool(log)
        self.apifunc = ApiFunc(log)
        self.head = '68'
        self.tail = '16'
        self.MSA = 'AB'
        self.address_term = ''  #终端地址

    def get_first_message(self, recv_data):
        """
        接收的数据里，可能会有多条报文连在了一起，只取第一条
        :param recv_data: 接收的报文
        :return: true 第一条报文  or  false "获取失败"
        """
        # self.log.info(f'接收的数据：{recv_data}')
        hex_data = self.apitool.ByteToHex(recv_data)
        # self.log.info(f'十六进制：{hex_data}')
        split_data = self.apitool.ByteToHexWithSplit(recv_data)
        # self.log.info(f'split_data:{split_data}')
        # 截取接收数据中第一条报文
        if hex_data[0:2] != self.head:  # 接收的数据头 不正确，舍弃
            self.log.error(f'报文头部错误')
            return "head error", False
        length = hex_data[2:6]
        length_list = split_string(length, 2)  # 把长度分割成列表，用于做反转
        reversed_length_list = length_list[::-1]
        length_decimal = int(''.join(reversed_length_list), 16)
        # self.log.info(f'length_decimal:{length_decimal}')
        # 报文真正的长度应该是 长度 + 7（头部长度为4，CRC校验位长度为2，尾部长度为1）
        str_length = (length_decimal + 7) * 2  # *2 是因为这里的长度是 字节的数量，一个字节由两个16进制位表示
        if hex_data[str_length-2:str_length] != self.tail:  # 尾部不正确
            self.log.error(f'报文尾部错误')
            return "tail error", False
        hex_data = hex_data[0:str_length]  # 如果一次性接受了很长的报文，就提取出第一个作为接收报文

        return hex_data, True

    def crc16_verify(self, dict_data):
        """
        crc校验
        :param dict_data:
        :return:
        """
        user_data_region = dict_data['user_data_region']
        crc16 = calculate_crc16_modbus(user_data_region)
        self.log.info(f'CRC16: {hex(crc16)[2:].upper()}')
        if not (hex(crc16)[2:].upper() == dict_data.get('real_crc') or hex(crc16)[2:].upper() == dict_data.get('crc_str')):
            self.log.error(f"crc校验失败：计算crc:{hex(crc16)[2:].upper()}, 接收crc:{dict_data.get('real_crc')}")
            return False
        self.log.info(f"crc校验通过：计算crc:{hex(crc16)[2:].upper()}, 接收crc:{dict_data.get('real_crc')}")
        return True

    def get_func(self, AFN, Fn):
        """
        匹配接口
        :param dict_data: 解包后的数据
        :return: 对应的接口
        """
        Function_mapping = {
            '02': {   # 充电桩主动发送，需要返回
                '01': self.apifunc.Link_interface_resp_login,
                '02': self.apifunc.Link_interface_resp_logout,
                '03': self.apifunc.Link_interface_resp_heartbeat,
                '04': self.apifunc.Link_interface_resp_login_verify
            },
            # '04': {  # 设置参数的结果，不需要返回
            #     '20': self.apifunc.Set_parameters_resp,
            #
            # },
            # '0A': {  # 查询参数的结果，不需要返回
            #     '01': self.apifunc.Query_parameters_Commu_para,
            #     '02': self.apifunc.Query_parameters_Domain_port,
            #     '03': self.apifunc.Query_parameters_Signal_strength,
            #     '17': self.apifunc.Query_parameters_Power_threshold,
            #     '18': self.apifunc.Query_parameters_Settle_allocation,
            #     '19': self.apifunc.Query_parameters_Pile_status,
            #     '20': self.apifunc.Query_parameters_Socket_status,
            #     '21': self.apifunc.Query_parameters_QRcode,
            #     '41': self.apifunc.Query_parameters_Total_electricity
            # },
            '0E': {  # 充电桩主动数据上报
                '01': self.apifunc.Data_report_resp_SIM_card_data,
                '03': self.apifunc.Data_report_resp_Socket_Status,
                '04': self.apifunc.Data_report_resp_Card_record
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


    def Message_parsing(self, recv_data):
        try:
            # self.log.info(f'*************一次解包************')
            # 获取第一条报文
            hex_data, status = self.get_first_message(recv_data)

            if status is False:
                return False
            # 开始解包
            head_str = hex_data[0:8]
            length = head_str[2:6]
            length_list = split_string(length, 2)
            reversed_length_list = length_list[::-1]
            length_decimal = int(''.join(reversed_length_list), 16)

            tail_str = hex_data[-2:]
            crc_str = hex_data[-6:-2]
            crc_list = split_string(crc_str, 2)
            reversed_crc_list = crc_list[::-1]
            real_crc = ''.join(reversed_crc_list)

            user_data_region = hex_data[8:-6]  # 用来计算crc
            # 控制域
            control_region = hex_data[8:10]

            control_region_bin = self.apitool.hex_to_bin(control_region).zfill(8)  # 转为二进制，查看详细内容
            DIR = control_region_bin[0]
            PRM = control_region_bin[1]
            function_code = int(control_region_bin[4:], 2)  # 转为十进制，查看功能码
            # 地址域
            address_region = hex_data[10:20]
            address_term = address_region[0:8]
            address_MSA = address_region[8:]
            # 应用层
            app_region = hex_data[20:-6]
            app_region_function_code = hex_data[20:22]
            # 帧序列域
            app_region_SEQ = hex_data[22:24]
            app_region_SEQ_bin = self.apitool.hex_to_bin(app_region_SEQ).zfill(8)  # 转为二进制，查看详细内容
            SEQ_TPV = app_region_SEQ_bin[0]
            SEQ_FIR = app_region_SEQ_bin[1]
            SEQ_FIN = app_region_SEQ_bin[2]
            PSEQ_RSEQ = app_region_SEQ_bin[4:]
            # 数据单元标识
            Data_unit_identification = hex_data[24:30]
            DA_Pn = Data_unit_identification[0:2]
            DT_Fn = Data_unit_identification[2:]
            # 把Fn处理成十进制字符串
            Fn_list = split_string(DT_Fn, 2)
            Fn_list_reverse = Fn_list[::-1]
            Fn_str = ''.join(Fn_list_reverse)
            Fn = str(int(Fn_str, 16)).zfill(2)  # 填充成两位
            # 每个报文的特有数据
            Specific_data = hex_data[30:-6]

            dict_data = {
                'head_str': {
                    'head_str_': head_str,
                    'head1': head_str[0:2],
                    'length': length_decimal,
                    'head2': head_str[6:]
                },
                'user_data_region': user_data_region,
                'control_region': {
                    'control_region_': control_region,
                    'control_region_bin': control_region_bin,
                    'DIR': DIR,
                    'PRM': PRM,
                    'function_code': function_code
                },
                'address_region': {
                    'address_region_': address_region,
                    'address_term': address_term,
                    'address_term_r': self.apitool.str_reverse(address_term),
                    'address_MSA': address_MSA
                },
                'app_region': {
                    'app_region_': app_region,
                    'app_region_function_code': app_region_function_code,
                    'app_region_SEQ': {
                        'app_region_SEQ': app_region_SEQ,
                        'app_region_SEQ_bin': app_region_SEQ_bin,
                        'SEQ_TPV': SEQ_TPV,
                        'SEQ_FIR': SEQ_FIR,
                        'SEQ_FIN': SEQ_FIN,
                        'PSEQ_RSEQ': PSEQ_RSEQ,
                    },
                    'Data_unit_identification': {
                        'Data_unit_identification_': Data_unit_identification,
                        'DA_Pn': DA_Pn,
                        'DT_Fn': DT_Fn,
                        'Fn': Fn
                    },
                    'Specific_data': Specific_data
                },
                'crc_str': crc_str,
                'real_crc': real_crc,
                'tail_str': tail_str,
            }
            # self.log.info(f'数据解析：{dict_data}')

            return dict_data
        except Exception as e:
            self.log.error("system error. %s" % str(e), exc_info=True)
            return False

    def message_pack1(self, recv_data, special_data):
        """
        组装报文1，
        场景：接收终端发送的报文->组装响应报文
        :param recv_data: 终端发送的数据
        :return: 响应报文
        """

        # self.log.info(f'**************************pack1 begin*****************************')
        # 解包
        try:
            dict_data = self.Message_parsing(recv_data)
            if not dict_data:
                self.log.error(f'解析报文出错', exc_info=True)
            #  crc校验
            crc_result = self.crc16_verify(dict_data)
            if not crc_result:
                self.log.error(f'crc校验失败', exc_info=True)
                return False

            # 匹配接口
            AFN = dict_data['app_region'].get('app_region_function_code')
            Fn = dict_data['app_region']['Data_unit_identification'].get('Fn')
            terminal_address = dict_data['address_region'].get('address_term_r', '')
            if not all([AFN, Fn]):
                self.log.error(f'报文缺少AFN或Fn')
                return False
            func = self.get_func(AFN, Fn)
            resp_data, status = func(dict_data, special_data)
            self.log.info(f'接口{func}返回的结果:{resp_data},{status}')
            self.log.info(f'**************************pack1 end*****************************')
            return terminal_address, resp_data

        except Exception as e:
            self.log.info(f'**************************pack1 error***************************')
            self.log.error("system error. %s" % str(e), exc_info=True)
            return False


    def massage_pack2(self):
        """
        组装报文2，定时任务，每秒执行
        从数据库中读取命令
        :return:
        """


        pass



if __name__ == '__main__':
    apitool = ApiTool()
    recv_data = '68110068 60 02 00 88 88 02 0E 60 00 04 00 02 00 C6 56 B9 FA C5 50 16'
    d = b'h\x16\x00h`\x08\x08\x00\x10\x01\x0e`\x00\x03\x00\x01\x01\x01\x00\xab\xab\x00\x05\x00\x00\x00\x8a\xba\x16h\x16'
    log, fh = publog.loger_init(pubpara.log_name)
    msg = Message(log)
    byte = apitool.HexToByte(recv_data)
    send_ = msg.message_pack1(byte)
    # print(send_)
    # msgtool = Message()
    a = msg.Message_parsing(d)
    print(a)



