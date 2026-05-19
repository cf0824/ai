#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：flask_app 
@File    ：jsonTool.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/7/9 17:02 
'''
#过滤字典中的键
def filter_fields(data, fields_to_keep):
    filtered_data = []
    if type(data) is list:
        for item in data:
            filtered_item = {key: item[key] for key in fields_to_keep if key in item}
            filtered_data.append(filtered_item)
    if type(data) is dict:
        filtered_item = {key: data[key] for key in fields_to_keep if key in data}
        filtered_data.append(filtered_item)

    return filtered_data