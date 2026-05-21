#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：充电桩通讯机 
@File    ：config.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/25 11:25 
@Description :
'''
import os
import sys

pwd = os.path.dirname(os.path.realpath(__file__))
print(pwd)
print(sys.path)
sys.path.append(pwd)
print(sys.path)

REDISConfig_local = {
    "host": os.environ.get('REDIS_HOST', 'redis'),
    "port": int(os.environ.get('REDIS_PORT', 6379)),
    "password": os.environ.get('REDIS_PASSWORD', '11223344root'),
    "db": 1
}

REDISConfig_dev = {
    "host": os.environ.get('REDIS_HOST', 'redis'),
    "port": int(os.environ.get('REDIS_PORT', 6379)),
    "password": os.environ.get('REDIS_PASSWORD', '11223344root'),
    "db": 1
}
