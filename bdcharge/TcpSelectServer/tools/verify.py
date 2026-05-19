#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：verify.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/9/26 16:06
暂时没用
'''


def validate_variable(para, required_length, required_type):
    # 初始化结果字典
    result_dict = {
        'result': True,
        'para': para,
        'required_length': required_length,
        'required_type': required_type,
        'actual_length': '',
        'actual_type': ''
    }

    # 检查类型
    actual_type = type(para).__name__
    result_dict['actual_type'] = actual_type

    # 对于可迭代类型（假设我们检查这些类型的长度）
    if isinstance(para, (str, list, tuple, dict, set)):
        actual_length = len(para)
        result_dict['actual_length'] = actual_length

        # 如果需要长度且实际长度与所需长度不匹配
        if required_length is not None and actual_length != required_length:
            result_dict['result'] = False

            # 检查类型是否匹配
    if actual_type != required_type:
        result_dict['result'] = False

    return result_dict


# 示例使用
print(validate_variable("hello", 5, "str"))  # 应该返回类型匹配但长度不匹配的结果
print(validate_variable(123, 5, "int"))  # 应该返回类型和长度都匹配的结果（因为不需要长度）
print(validate_variable([1, 2, 3], 3, "list"))  # 应该返回完全匹配的结果
print(validate_variable(123, 3, "str"))  # 应该返回类型不匹配的结果