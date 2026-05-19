#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：ts1.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/21 17:35 
'''
from redis import StrictRedis
from SmartChargeBD.settings import REDISConfig
import json

redis = StrictRedis(**REDISConfig, max_connections=2000, decode_responses=True)

json1 = {
    "a": 123,
    "b": '123',
    "c": {
        "1": 1,
        "2": "2"
    }
}

json1 = json.dumps(json1)

redis.set('test', json1)
