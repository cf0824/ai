#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：handle_cmd.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/21 17:17 
@Description :
'''

from utils.redis_package.redisFunc import RedisDb
import json
redis_db = RedisDb()

# 查找 充电桩-->服务器 的消息（不一定是命令，也可能是响应）
def get_cmd_S2T():
    keys = redis_db.get_keys('cmdS2T*')
    return keys   # 每个key，都是一个 充电桩-->服务器  的命令

def get_cmd_detail(cmd):
    cmd_detail = redis_db.get_value(cmd)
    cmd_detail = json.loads(cmd_detail)
    redis_db.del_value(cmd)
    return cmd_detail

def Byte2Hex(data):
    return ''.join(["%02X" % item for item in data]).strip()

def Hex2Byte(hexStr):
    return bytes.fromhex(hexStr)
