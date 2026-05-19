#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  MyCode -> params_validate.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   params_validate.py
@Time    :   2024/4/11 9:56
@Desc    :
             ┏┓       ┏┓
            ┏┛┻━━━━━━━┛┻┓
            ┃    ☃      ┃
            ┃  ┳┛   ┗┳  ┃
            ┃     ┻     ┃
            ┗━┓       ┏━┛
              ┃       ┗━━━━┓
              ┃ 神兽保佑     ┣┓
              ┃　永无BUG！   ┏┛
              ┗┓┓┏━━━┳┓┏━━━┛
               ┃┫┫   ┃┫┫
               ┗┻┛   ┗┻┛
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
=================================================="""
"""
 接口参数验证配置
 接口名：[参数列表]
 参数列表： [参数名，参数类型，是否必传]
validate_params 方法参数说明： params_rule: 接口名参数验证规则，params: 参数（json）
 返回说明：lack_params：缺少必传参数列表; empty_params: 值为空的参数列表; error_params：数据类型错误参数列表;
           error_api_lists: 参数验证配置错误
"""


# 非必传参数值为（int: 0, float:0, str: "", list: [], dict: {}）处理
def value_is_null_process(params_value, params_type):
    validate_value = False
    if isinstance(params_value, params_type):
        if params_value == 0 or params_value == "" or params_value == [] or params_value == {}:
            validate_value = True
    return validate_value


# 必传参数值为（str: "", list: [], dict: {}）处理
def value_not_null_process(params_value, param_not_null):
    validate_value = True
    if param_not_null:
        if params_value == "" or params_value == [] or params_value == {} or params_value is None:
            validate_value = False
    return validate_value


# 移除多余参数
def remove_redundant_params(req_params, api_params):
    api_keys = [i[0] for i in api_params]
    param_keys = list(req_params)
    new_params_keys = list(set(param_keys).intersection(set(api_keys)))#交集

    new_params = {}
    for k in new_params_keys:
        new_params[k] = req_params.get(k)
    return new_params


def validate_params(params_rule, params):
    if not isinstance(params, dict):
        return False, "参数类型错误"
    if not params_rule:
        return True, f"验证通过 参数信息 {params}"
    lack_params, empty_params, error_params, error_api_lists = [], [], [], []
    for i in params_rule:
        if len(i) == 4:
            param_name, param_type, param_not_null, param_attr_name = i
            param_value = params.get(param_name)
            if param_name not in params and param_not_null:
                lack_params.append(param_attr_name)
            else:
                if not value_not_null_process(param_value, param_not_null):
                    empty_params.append(param_attr_name)
                validate_value = value_is_null_process(param_value, param_type)
                if not validate_value and not isinstance(param_value, param_type):
                    if param_name in params:
                        if param_value or (not param_value and not param_not_null):
                            error_params.append(param_attr_name)
        else:
            error_api_lists.append(i)

    if error_api_lists:
        return False, f"{error_api_lists}参数验证配置错误!"
    if lack_params or empty_params or error_params:
        data = {"缺少必传参数": lack_params, "值为空参数": empty_params, "错误参数": error_params}
        return False, f"参数信息验证失败{data}"
    new_params = remove_redundant_params(params, params_rule)
    return True, f"验证通过 参数信息 {new_params}"


def validate_string(s):
    if not s:
        raise ValueError("字符串不能为空")
    parts = s.split(';')
    for part in parts:
        if part:
            if len(part) != 2:
                return False, f"插座 '{part}' 长度不是两位"
            if not part.isdigit():
                return False, f"插座 '{part}' 包含非数字字符"
    return True, 'success'


def check_ports_existence(list1, list2):
    # 提取列表2中所有eq_port的值并转换为集合
    existing_ports = {d['eq_port'] for d in list2}
    # 找出列表1中存在于集合的元素
    existing_values = [port for port in list1 if port in existing_ports]
    # 根据是否存在返回结果
    if existing_values:
        return False, existing_values
    else:
        return True, existing_values


if __name__ == '__main__':
    # str = '01;'
    # print(str.split(';'))
    # print(validate_string(str))

    list1 = ['01', '06']
    list2 = [{'eq_port': '00'}, {'eq_port': '01'}, {'eq_port': '06'}, {'eq_port': '07'}]

    # 调用函数
    result_flag, existing_values = check_ports_existence(list1, list2)

    print(result_flag)  # 输出: False
    print(existing_values)  # 输出: ['01']
