#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：timeTool.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/4/26 16:38 
@Description :
'''
from datetime import datetime

def compare_time(time_str1, time_str2):
    try:
        t1 = datetime.strptime(time_str1, "%H:%M:%S").time()
        t2 = datetime.strptime(time_str2, "%H:%M:%S").time()
        if t1 < t2:
            return True
        elif t1 > t2:
            return False
        else:
            return "时间相同"
    except ValueError as e:
        return f"格式错误: {e}"