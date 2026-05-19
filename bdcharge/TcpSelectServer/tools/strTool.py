#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：strTool.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/8/5 9:45 
'''
def split_string(s, length):
    """
    按照指定的长度拆分字符串。

    :param s: 要拆分的字符串
    :param length: 每个子字符串的长度
    :return: 拆分后的字符串列表
    """
    # 使用列表推导式和切片操作来拆分字符串
    return [s[i:i + length] for i in range(0, len(s), length)]


import random


def generate_random_string(length, include_lowercase=True):
    """
    生成一个指定长度的随机字符串，包含数字和字母A到F（可选地包含小写字母）。

    :param length: 字符串的长度
    :param include_lowercase: 是否包含小写字母（默认为True）
    :return: 指定长度的随机字符串
    """
    if length < 1:
        raise ValueError("Length must be greater than 0")

        # 定义字符集
    characters = '0123456789ABCDEF'
    if include_lowercase:
        characters += 'abcdef'

        # 使用 random.choices() 从字符集中随机选择指定数量的字符
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


# 示例
if __name__ == "__main__":
    # 只包含大写字母A到F和数字的随机字符串
    random_str_uppercase_digits = generate_random_string(8, include_lowercase=False)
    print(random_str_uppercase_digits)  # 输出类似 '1A2B3E8D' 的随机字符串

    # 包含大写、小写字母A到F和数字的随机字符串
    random_str_mixedcase_digits = generate_random_string(10, include_lowercase=True)
    print(random_str_mixedcase_digits)  # 输出类似 '3bA5F9eC7d' 的随机字符串





if __name__ == '__main__': #x1489860623610072132560
    print(split_string('143839383630363233363130303732313332353630', 2))
    print(split_string('3B46EAAB78563412', 8))
    print(reversed(split_string('3B46EAAB78563412', 8)))