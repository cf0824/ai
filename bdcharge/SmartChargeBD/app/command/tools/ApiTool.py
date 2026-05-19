#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：ApiTool.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/8/2 10:23

'''
import json
from datetime import datetime
import random
import os
import sys
pwd = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(pwd)
print(pwd)
print(parent_dir)
print(sys.path)
sys.path.append(pwd)
sys.path.append(parent_dir)
print(sys.path)

# from logUtils import log
# from tools.strTool import split_string, generate_random_string
# from tools.calculate import Calculator

from strTool import split_string, generate_random_string
from calculate import Calculator
from redis_package.redisFunc import RedisDb



# log, fh = publog.loger_init(pubpara.log_name_tran)

# from utils.blog.handle import JaeLogManager
#
# log = JaeLogManager('ApiTool').get_logger_and_add_handlers(
#     log_filename='ApiTool', log_file_handler_type=2,
# )


class ApiTool():
    def __init__(self, log):
        self.log = log
        self.redis_db = RedisDb()

    # ByteToHex的转换
    def ByteToHex(self, data):
        """
        字节转十六进制
        :param data:
        :return:
        """
        return ''.join(["%02X" % item for item in data]).strip()

    def ByteToHexWithSplit(self, data):
        """
        字节转十六进制，每两个用空格分开，便于阅读
        :param data:
        :return:
        """
        return ''.join(["%02X " % item for item in data]).strip()

    # HexToByte的转换
    def HexToByte(self, hexStr):
        """
        十六进制转字节，给终端发送数据时使用
        :param hexStr:
        :return:
        """
        return bytes.fromhex(hexStr)

    def split_string(self, str):
        """
        分割字符串，用空格分割，没啥用
        :param str:
        :return:
        """
        return str.split()

    def hex_to_bin(self, hex_str):
        """
        十六进制转二进制，用于解析报文，查看每个bit代表的意思
        :param hex_str:
        :return:
        """
        decimal_int = int(hex_str, 16)
        # 使用切片操作去除前缀'0b'
        binary_str = bin(decimal_int)[2:]

        return binary_str

    def string_to_hex(self, s):
        """
        字符串转十六进制
        :param s:
        :return:
        """
        # 使用列表推导式遍历字符串中的每个字符，将其转换为十六进制表示，并去掉'0x'前缀
        hex_chars = [format(ord(char), '02x') for char in s]
        # 将十六进制字符列表连接成一个字符串
        hex_string = ''.join(hex_chars).upper()
        return hex_string

    def hex_to_str(self, hex_string):
        """
        十六进制转字符串
        :param hex_string:
        :return:
        """
        # 十六进制字符串的长度必须是偶数，因为每两个十六进制字符表示一个字节
        if len(hex_string) % 2 != 0:
            raise ValueError("Hex string length must be even")

            # 使用bytes.fromhex()方法将十六进制字符串转换为字节对象
        byte_data = bytes.fromhex(hex_string)

        # 将字节对象解码为字符串，默认使用UTF-8编码（也可以根据需要指定其他编码）
        # 如果原始数据是ASCII编码的，也可以指定'ascii'作为解码方式
        decoded_string = byte_data.decode('utf-8')

        return decoded_string

    def length_with_hex(self, string):
        """
        专门用来计算发送报文中的长度，低位在前，高为在后

        计算十六进制的字符串，先将其转换为字节格式，
        再计算其长度，把长度转换成两个字节的十六进制，
        最后反转这个十六进制的长度，将结果返回
        :param string: 需要计算长度的字符串
        :return: 字符串的十六进制反转长度
        """
        byte_data = bytes.fromhex(string) # 将字符串转换成字节格式
        length_decimal = len(byte_data) # 十进制长度
        length_hex = hex(length_decimal).replace('0x', '').zfill(4) # 转换成十六进制，去除‘0x’，补到4位
        length_list = split_string(length_hex, 2) # 分割成列表，方便做倒置
        length_list_reverse = length_list[::-1] # 倒置
        length = ''.join(length_list_reverse)
        return length

    def generate_SEQ(self, SEQ_json, address_json):
        """
        'SEQ':{
                'is_PR_SEQ': '1',
                'PR_SEQ': PR_SEQ,
                'is_TPV': is_TPV  # 是否带时间标签
            },
        address_json = {
            'terminal_address': '10000808',
            'MSA': 'AB'
        }
        生成SEQ
        [0]表示时间标签
        [1、2]表示首帧、末帧
        [3]没什么用，一直为0
        [4、5、6、7]表示启动帧、响应帧，不太理解，应该没啥用
        :param :
        :return:

        """
        # 首帧标志FIR、末帧标志FIN
        self.log.info(f'******生成SEQ函数begin******')
        FIR = '1'
        FIN = '1'
        TPV = '0'
        is_PR_SEQ = SEQ_json.get('is_PR_SEQ')
        is_TPV = SEQ_json.get('is_TPV')
        if is_TPV == True:
            TPV = '1'

        if is_PR_SEQ == '1': # 服务端是从动站，PR_SEQ要从启动站获取
            PR_SEQ = SEQ_json.get('PR_SEQ')
        else:
            # characters = ['0', '1']
            # PR_SEQ = ''.join(random.choice(characters) for _ in range(4))
            key = 'PR_SEQ'
            terminal_address = address_json.get('terminal_address')
            value = self.redis_db.get_value(key)
            self.log.info(f'PR_SEQ:{value}')
            if value == None:  # redis里没有SPR_SEQ，就设置一个，值为 空字典
                value = {}
                value[terminal_address] = '0000'
                self.redis_db.set_value(key, json.dumps(value), permanent=True)
                PR_SEQ = '0000'
            else:  # 如果有这个键，就获取里边具体的值
                value = json.loads(value)
                term_SEQ = value.get(terminal_address)
                if term_SEQ == None:  #如果字典里没有这个终端地址
                    value[terminal_address] = '0000'
                    self.redis_db.set_value(key, json.dumps(value), permanent=True)
                    PR_SEQ = '0000'
                else:  # 如果有
                    PR_SEQ = term_SEQ
                    term_SEQ_int = int(term_SEQ, 2)  # 转成十进制，加1，保存
                    if term_SEQ_int == 15:  # 到了临界值，就重新置为0
                        value[terminal_address] = '0000'
                        self.redis_db.set_value(key, json.dumps(value), permanent=True)
                    else:  # 没到临界值，就加1
                        term_SEQ_int = term_SEQ_int + 1
                        term_SEQ_int = bin(term_SEQ_int)[2:].zfill(4)
                        value[terminal_address] = term_SEQ_int
                        self.redis_db.set_value(key, json.dumps(value), permanent=True)

        SEQ_bin = TPV + FIR + FIN + '0' + PR_SEQ
        SEQ = hex(int(SEQ_bin, 2)).replace('0x', '').upper().zfill(2)  # 转成十六进制
        self.log.info(f'SEQ二进制字符串: {SEQ_bin}，SEQ十六进制字符串: {SEQ}')
        self.log.info(f'******生成SEQ函数end******')
        return SEQ

    def decimal_to_bcd(self, decimal_number):
        """
        十进制转bcd码
        :param decimal_number:
        :return:
        """
        # 将十进制数转换为字符串，方便处理
        decimal_str = str(decimal_number)

        # 初始化BCD码字符串
        bcd_str = ""

        # 遍历十进制数的每一位
        for digit in decimal_str:
            # 将每一位十进制数转换为对应的四位二进制数（前面补零）
            bcd_digit = format(int(digit), '04b')
            # 将转换后的四位二进制数添加到BCD码字符串中
            bcd_str += bcd_digit + " "

            # 去除末尾的空格（如果有的话）
        bcd_str = bcd_str.rstrip()

        return bcd_str

    def bcd_to_decimal(self, bcd_string):
        """
        BCD码转十进制
        :param bcd_string:
        :return:
        """
        # if len(bcd_string) % 4 != 0:
        #     raise ValueError("BCD string length must be a multiple of 4")

        decimal_number = 0
        power = 0  # 用于计算每个十进制位的权重（10的幂）

        # 从BCD字符串的末尾开始遍历，因为BCD码是从最低位开始的
        for i in range(len(bcd_string) - 1, -1, -4):
            # 截取4位二进制数
            binary_str = bcd_string[max(0, i - 3):i + 1]
            # 将二进制字符串转换为十进制数
            decimal_digit = int(binary_str, 2)
            # 将这个十进制数添加到最终结果中，考虑其权重
            decimal_number += decimal_digit * (10 ** power)
            power += 1

        return decimal_number

    def encrypt_password(self, original_password, terminal_address, random_number):
        """

        :param original_password: 原始密码
        :param terminal_address: 终端地址
        :param random_number: 随机数
        :return: 密码串
        """

        #把三个参数串中的‘0x’删除
        original_password = original_password.replace("0x", "")
        terminal_address = terminal_address.replace("0x", "")
        random_number = random_number.replace("0x", "")

        if not len(original_password) == len(terminal_address) == len(random_number):
            return ValueError("原始密码、终端地址、随机数的长度必须相等！")

        #把三个参数串以长度2分割
        new_password = split_string(original_password, 2)
        new_address = split_string(terminal_address, 2)
        new_random_number = split_string(random_number, 2)


        #创建一个计算器对象
        calculator = Calculator(16)
        list = []
        for item1, item2, item3 in zip(new_password, new_address, new_random_number):
            # print('元素值：')
            # print(item1, item2, item3)
            result = calculator.add(calculator.add(item1, item2), item3)
            list.append(result)
        # print(f'list:{list}')
        self.log.info(f'list:{list}')
        reversed_list = list[::-1] #把list倒置
        reversed_random_number = new_random_number[::-1]  # 把随机数列表中的元素倒置
        message_list = reversed_list + reversed_random_number

        full_str = ''.join(message_list)
        self.log.info(f'密码段:{full_str}')
        return full_str


    def decrypt_password(self, encrypted_password, terminal_address, random_number):
        """

        :param encrypted_password: 加密后的密码串
        :param terminal_address: 终端地址
        :param random_number: 随机数
        :return:
        """
        #把三个数据进行分割成列表
        new_password = split_string(encrypted_password, 2)[::-1]  #把password列表倒置
        new_address = split_string(terminal_address, 2)
        new_random_number = split_string(random_number, 2)
        # 创建一个计算器对象
        calculator = Calculator(16)
        list = []
        for item1, item2, item3 in zip(new_password, new_address, new_random_number):
            # print('元素值：')
            # print(item1, item2, item3)
            result = calculator.subtract(calculator.subtract(item1, item2), item3)
            list.append(result)
        self.log.info(f'list:{list}')

        original_password = ''.join(list)
        return original_password
    # 暂时没用上
    def generate_data_app_head(self, recv_data, is_TPV):
        """
        应用层头部信息非常相似
        控制域 + 地址域 + AFN(应用层功能码) + SEQ + 数据单元标识
        通过接收的数据，生成应用层的头部信息
        :param recv_data: 接收的报文（解析后的）
        :param is_TPV: 是否有时间标签
        :return: 返回应用层头部
        """
        # 这里后续可能要改成‘0000’，我对启动站从动站的理解貌似有点错误。
        # 充电桩主动给服务器发，服务器应答时，服务器应该是从动站，PRM应该是0，即'0000'
        # 2024.09.25 将‘0100’修改为‘0000’，后边的功能码 和 终端发送的保持一致
        control_area = '0000' + recv_data['control_region'].get('control_region_bin', '')[4:]
        control_region = hex(int(control_area, 2)).replace('0x', '').zfill(2).upper()
        MSA = 'AB'
        address_region = recv_data['address_region'].get('address_term', '') + MSA
        AFN = recv_data['app_region'].get('app_region_function_code', '')

        # 帧序列域
        SEQ_bin = self.generate_SEQ(is_TPV)
        SEQ = hex(int(SEQ_bin, 2)).replace('0x', '').upper()  # 转成十六进制
        # 数据单元标识
        Data_unit_identification = recv_data['app_region']['Data_unit_identification'].get('Data_unit_identification_', '')

        print(f"control_region:{control_region}\naddress_region:{address_region}\nAFN:{AFN}\nSEQ:{SEQ}\nData_unit_identification:{Data_unit_identification}\n")
        app_head = control_region + address_region + AFN + SEQ + Data_unit_identification
        print(f'应用层头部: {app_head}\n')
        return app_head




    def generate_control_area(self, control_json):
        """
        示例
        control_json = {
            'DIR': 'S2T',
            'PRM': 'active',
            'feature_code': '10'
        }
        :param control_json:
        :return:
        """
        self.log.info(f'******生成控制域函数begin******')
        DIR = control_json.get('DIR')
        PRM = control_json.get('PRM')
        feature_code = control_json.get('feature_code')
        dir = '0'
        prm = '1'

        if DIR == 'S2T':
            dir = dir
        elif DIR == 'T2S':
            dir = '1'
        if PRM == 'active':   # 主动站
            prm = prm
        elif PRM == 'passive':  # 被动站
            prm = '0'
        feature_code = bin(int(feature_code))[2:].zfill(4)
        control_area_bin = dir + prm + '00' + feature_code
        control_area = hex(int(control_area_bin, 2)).replace('0x', '').upper().zfill(2)
        self.log.info(f'控制域二进制字符串: {control_area_bin}，控制域十六进制字符串: {control_area}')
        self.log.info(f'******生成控制域函数end******')
        return control_area

    def generate_address_area(self, address_json):
        """
        示例
        address_json = {
            'terminal_address': '10000808',
            'MSA': 'AB'
        }
        :param address_json:
        :return:
        """
        self.log.info(f'******生成地址域函数begin******')
        terminal_address = address_json.get('terminal_address')  # 默认接收的终端地址都是正常的顺序的
        MSA = address_json.get('MSA')
        terminal_address = self.str_reverse(terminal_address)
        address_area = terminal_address + MSA
        self.log.info(f'地址域十六进制字符串: {address_area}')
        self.log.info(f'******生成控制域函数end******')
        return address_area

    def generate_data_unit_identify(self, data_unit_json):
        """
        示例
        data_unit_json = {
            'DA_Pn': '00',
            'DT_Fn': '04'
        }
        :param data_unit_json:
        :return:
        """
        self.log.info(f'******生成数据单元标识函数begin******')
        DA_Pn = data_unit_json.get('DA_Pn')
        DT_Fn = data_unit_json.get('DT_Fn')
        DT_Fn_hex = hex(int(DT_Fn)).replace('0x', '').zfill(4).upper()

        DT_Fn = self.str_reverse(DT_Fn_hex)
        data_unit_identify = DA_Pn + DT_Fn
        self.log.info(f'数据单元标识十六进制字符串: {data_unit_identify}')
        self.log.info(f'******生成数据单元标识函数end******')
        return data_unit_identify



    def generate_app_head(self, paras):
        """
        生成报文头部
        示例
        paras = {
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
            'SEQ':{
                'is_PR_SEQ': '0',
                'PR_SEQ': '',
                'is_TPV': True  # 是否带时间标签
            },
            'data_unit_json': {
                'DA_Pn': '00',                  # 不知道有啥用，0表示终端本身，非0表示具体的设备
                'DT_Fn': '04'                   # 接口码
            }
        }
        :param paras: 所需参数
        :return:
        """
        self.log.info(f'************生成报文头部函数begin************')
        # 1)控制域：传输方向、启动标志位、功能码
        control_json = paras.get('control_json')
        control_area = self.generate_control_area(control_json)
        # 2)地址域：终端地址、MSA
        address_json = paras.get('address_json')
        address_area = self.generate_address_area(address_json)
        # 3)AFN
        AFN = paras.get('AFN')
        # 4)SEQ
        SEQ_json = paras.get('SEQ')
        SEQ = self.generate_SEQ(SEQ_json, address_json)
        # 5)数据单元标识
        data_unit_json = paras.get('data_unit_json')
        data_unit_identify = self.generate_data_unit_identify(data_unit_json)

        app_head = control_area + address_area + AFN + SEQ + data_unit_identify
        self.log.info(f'app_head十六进制字符串: {app_head}')

        self.log.info(f'************生成报文头部函数end************')
        return app_head

    def get_app_head_paras_from_recv_dict(self, recv_dict, is_TPV):
        self.log.info(f'******从接收数据中生成app_head参数begin******')
        terminal_address = recv_dict['address_region'].get('address_term_r', '')
        AFN = recv_dict['app_region'].get('app_region_function_code', '')
        DA_Pn = recv_dict['app_region']['Data_unit_identification'].get('DA_Pn', '')
        DT_Fn = recv_dict['app_region']['Data_unit_identification'].get('Fn', '')
        PR_SEQ = recv_dict['app_region']['app_region_SEQ'].get('PSEQ_RSEQ', '')
        paras = {
            'control_json': {
                'DIR': 'S2T',  # 传输方向
                'PRM': 'passive',  # 是主动站还是被动站：passive
                'feature_code': '10'  # 功能码，用到的很少，写死
            },
            'address_json': {
                'terminal_address': terminal_address,  # 终端地址，8位，正序，高位在前，低位在后
                'MSA': 'AB'  # 先写死
            },
            'AFN': AFN,  # 功能码，一共四类 02、04、0A、0E
            'SEQ':{
                'is_PR_SEQ': '1',
                'PR_SEQ': PR_SEQ,
                'is_TPV': is_TPV  # 是否带时间标签
            },
            'data_unit_json': {
                'DA_Pn': DA_Pn,  # 不知道有啥用，0表示终端本身，非0表示具体的设备
                'DT_Fn': DT_Fn  # 接口码
            }
        }
        self.log.info(f'******从接收数据中生成app_head参数end******')
        return paras

    def current_time_bcd(self):
        """
        生成终端时钟
        :return:
        """
        # 获取当前时间
        now = datetime.now()

        # 提取时间的各个组成部分
        year = now.year % 100  # 取最后两位
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second

        # 计算星期几
        weekday = now.weekday() + 1  # 0是周一，需要加1以匹配星期五为5的情况

        # 转换为BCD编码
        def to_bcd(decimal):
            # return (decimal // 10) * 16 + (decimal % 10)
            return self.decimal_to_bcd(decimal).zfill(8)
        # 十进制转二进制，高位的0不省略
        def decimal_to_fixed_width_binary(decimal, width):
            # 使用bin()获取二进制字符串，并去掉前缀'0b'
            binary_str = bin(decimal)[2:]
            # 使用zfill()填充前导零，直到达到指定的宽度
            return binary_str.zfill(width)

        def binary_to_hex(binary_str):
            """
            将二进制字符串转换为不带前缀的16进制字符串。
            参数:
            binary_str (str): 二进制字符串。
            返回:
            str: 不带前缀的16进制字符串。
            """
            binary_str_clean = binary_str.replace(" ", "")
            # 将二进制字符串转换为整数
            decimal_value = int(binary_str_clean, 2)

            # 将整数转换为16进制字符串，并去掉前缀'0x'
            hex_str = hex(decimal_value)[2:]

            return hex_str.zfill(2)

        # 创建终端时钟数据
        time_bcd_str = {
            '秒': to_bcd(second),
            '分': to_bcd(minute),
            '时': to_bcd(hour),
            '日': to_bcd(day),
            '周-月': decimal_to_fixed_width_binary(((weekday) << 5 | month//10 << 4 | month%10), 8),  # 星期在高位，月份在低位
            '年': to_bcd(year),
        }

        # 创建一个十六进制的字典
        time_hex_str = {}
        for key, value in time_bcd_str.items():
            # 将计算后的键值对添加到新字典中
            time_hex_str[key] = binary_to_hex(value)
        full_time_bcd_str = ''
        full_time_hex_str = ''

        # 遍历字典，拼接所有值
        for value in time_bcd_str.values():
            full_time_bcd_str  += value.replace(" ", "")  # 或者使用full_time_str = full_time_str + value来拼接

        for value in time_hex_str.values():
            full_time_hex_str  += value.replace(" ", "")  # 或者使用full_time_str = full_time_str + value来拼接
        # 创建一个新的键值对，并添加到字典中
        time_bcd_str['完整时间'] = full_time_bcd_str
        time_hex_str['完整时间'] = full_time_hex_str


            # 返回BCD格式的时间数据
        return time_bcd_str, time_hex_str


    def str_reverse(self, str, num=2):
        """
        字符串倒置
        :param str:
        :param num:
        :return:
        """
        str_list = split_string(str, num)
        reversed_list = str_list[::-1]
        reversed_str = ''.join(reversed_list)
        return reversed_str


# 测试函数
if __name__ == "__main__":
    apitool = ApiTool()
    # bcd_time, hex_time = apitool.current_time_bcd()
    # print("Current Time in BCD format:", bcd_time)
    # print("Current Time in HEX format:", hex_time)
    # #
    # decimal_number = 165
    # bcd_code = apitool.decimal_to_bcd(decimal_number)
    # print(f"Decimal: {decimal_number}, BCD: {bcd_code}")
    #
    #     # 示例
    #
    # bcd_code = "1011000"
    # bcd_code_clean = bcd_code.replace(" ", "")
    # decimal_number = apitool.bcd_to_decimal(bcd_code_clean)
    # print(f"BCD: {bcd_code_clean}, Decimal: {decimal_number}")
    # print(5 << 5 | 11//10 << 4 | 11%10)

    # 加密
    # original_password = "0x30201228"
    # terminal_address = "0x03740001"
    # random_number = "0x12345678"
    # message_str = apitool.encrypt_password(original_password, terminal_address, random_number)
    # print(message_str)

    #解密
    # encrypted_password = '424E76B8'
    # terminal_address = '10000808'
    # random_number = '78563412'
    # message_str = apitool.decrypt_password(encrypted_password, terminal_address, random_number)
    # print(message_str)

    # print(apitool.hex_to_bin('C9'))
    #
    # print(apitool.length_with_hex('C9080800100002600004003A2C537A3A33120A'))
    #
    # print(apitool.generate_SEQ(is_TPV=False))

    # recv_data = {'head_str': {'head_str': '68130068', 'head1': '68', 'length': 19, 'head2': '68'}, 'user_data_region': 'C908080010000260000400424E76B878563412', 'control_region': {'control_region': 'C9', 'control_region_bin': '11001001', 'DIR': '1', 'PRM': '1', 'function_code': 9}, 'address_region': '08080010', 'app_region': {'app_region': '000260000400424E76B878563412', 'app_region_function_code': '0002', 'app_region_SEQ': {'app_region_SEQ': '60', 'app_region_SEQ_bin': '01100000', 'SEQ_TPV': '0', 'SEQ_FIR': '1', 'SEQ_FIN': '1', 'PSEQ_RSEQ': '0000'}, 'Data_unit_identification': {'Data_unit_identification': '000400', 'DA_Pn': '00', 'DT_Fn': '0400'}, 'Specific_data': '424E76B878563412'}, 'crc_str': 'FACE', 'real_crc': 'CEFA', 'tail_str': '16'}

    # app_head = apitool.generate_data_app_head(recv_data, False)
    #
    # byte = b'\x1489860623610072132560'
    # print(apitool.HexToByte('C9080800100002600004003A2C537A3A33120A'))
    # print(byte[1:])
    # number_int = int(byte[1:])
    # print(number_int)
    # 将整数转换为字符串
    # number_str = str(number_int)
    #
    # print(number_str)  #
    #
    # print('6999'.encode())
    # print(apitool.ByteToHex(b'W'))
    # try:
    #     my_string = "bdcdz.pinmait.com"
    #     my_bytes_ascii = my_string.encode('ascii')
    #     print(my_bytes_ascii)  # 如果字符串只包含ASCII字符，这将成功
    # except UnicodeEncodeError:
    #     print("字符串包含非ASCII字符，无法使用'ascii'编码")


    str = '12345678'
    reversed_str = apitool.str_reverse(str, 1)
    print(reversed_str)
    #
    # print(apitool.generate_SEQ(is_TPV=True))
    # paras = {
    #     'control_json': {
    #         'DIR': 'S2T',  # 传输方向
    #         'PRM': 'active',  # 是主动站还是被动站：passive
    #         'feature_code': '10'  # 功能码，用到的很少，写死
    #     },
    #     'address_json': {
    #         'terminal_address': '10000808',  # 终端地址，8位，正序，高位在前，低位在后
    #         'MSA': 'AB'  # 先写死
    #     },
    #     'AFN': '02',  # 功能码，一共四类 02、04、0A、0E
    #     'is_TPV': True,  # 是否带时间标签
    #     'data_unit_json': {
    #         'DA_Pn': '00',  # 不知道有啥用，0表示终端本身，非0表示具体的设备
    #         'DT_Fn': '04'  # 接口码
    #     }
    # }
    # app_head = apitool.generate_app_head(paras)
    # print(app_head)
