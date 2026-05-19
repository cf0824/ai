#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：calculate.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/8/3 17:39 
'''


class Calculator:
    def __init__(self, numeration):
        self.numeration = numeration
        if self.numeration == 16:
            self.replace_str = '0x'
    def add(self, hex_num1, hex_num2):
        # 加法
        # 移除可能的'0x'前缀，并将字符串转换为整数
        num1 = int(hex_num1.replace(self.replace_str, ''), self.numeration)
        num2 = int(hex_num2.replace(self.replace_str, ''), self.numeration)
        # 执行加法运算
        result = num1 + num2
        # 返回结果的16进制字符串表示，不带'0x'前缀
        return format(result, 'X')

    def subtract(self, hex_num1, hex_num2):
        # 减法
        # 移除可能的'0x'前缀，并将字符串转换为整数
        num1 = int(hex_num1.replace(self.replace_str, ''), self.numeration)
        num2 = int(hex_num2.replace(self.replace_str, ''), self.numeration)
        # 执行减法运算
        result = num1 - num2
        # 如果结果为负，这里可以选择抛出异常、返回绝对值或其他处理方式
        # 这里简单处理为返回绝对值（注意：这通常不是处理负数的最佳方式）
        if result < 0:
            return format(abs(result), 'X')
            # 返回结果的16进制字符串表示，不带'0x'前缀
        return format(result, 'X')

        # 可选：添加方法来获取带'0x'前缀的结果

    def add_with_prefix(self, hex_num1, hex_num2):
        return self.replace_str + self.add(hex_num1, hex_num2)

    def subtract_with_prefix(self, hex_num1, hex_num2):
        return self.replace_str + self.subtract(hex_num1, hex_num2)

if __name__ == '__main__':
    calculator = Calculator(16)
    print(calculator.add('20', '74'))

    a = calculator.add('94', '34')
    print(hex(int(calculator.add('7b', '01'), 16) % 256).replace('0x', '').upper(), type(a))