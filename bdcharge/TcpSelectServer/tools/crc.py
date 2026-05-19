#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：crc.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/8/1 16:17 
'''


def calculate_crc16_modbus(hex_string):
    byte_array = bytes.fromhex(hex_string)
    crc = 0xFFFF
    for byte in byte_array:
        crc = crc ^ byte
        for _ in range(0, 8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc

# 示例
if __name__ == '__main__':
    hex_string = '8A08080010AB0A6F0002000011626463647A2E70696E6D6169742E636F6D571B'
    crc = calculate_crc16_modbus(hex_string)
    print(crc)
    print(hex(crc))  # 以十六进制输出CRC值


# 示例
# data = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
# datahex = 'C9 08 08 00 10 00 02 60 00 01 00'
# crc = calculate_crc16_modbus(data)
#
# print(hex(crc))  # 以十六进制输出CRC值
