#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：cmdFunc.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/22 15:00 
@Description :
'''
import json
from utils.redis_package.redisFunc import RedisDb
from utils.redis_package.redis_tools import RedisTools

redis_tools = RedisTools()
Rdb = RedisDb()

def add_command(key_json, value_json):
    """
    向redis里添加命令
    :param ket_json: 需要包含设备id:eq_id, 操作类型：operation_type
    :param value_json: 该操作下终端需要的值
    :return:
    """
    # eq_id = key_json["eq_id"]
    # operation_type = key_json["operation_type"]
    head = key_json["head"]
    key = redis_tools.generate_key(head)
    # value_json["operation_type"] = terminal_dict.get(operation_type)
    # value_json["status"] = 0  # 执行状态
    value = json.dumps(value_json)
    Rdb.set_value(key, value)

def add_last_term_cmd(key, value):
    """
    添加终端最新的cmd
    :param key_json:
    :param value_json:
    :return:
    """
    Rdb.set_value(key, value, ex=20)

def get_last_term_cmd(key):
    value = Rdb.get_value(key)
    return value

def get_command(key):
    """
    通过key获取命令
    :param key:
    :return:
    """
    value = Rdb.get_value(key)
    return value

def expire_command(key):
    """
    把执行过的命令过期时间置为0
    :param key: 命令键值
    :return:
    """
    result = Rdb.expire_key(key, ex=0)
    return result




if __name__ == '__main__':
    key_json = {
        "head": "cmdT2S"
    }
    data = b'h\x0b\x00h\xc9\x08\x08\x00\x10\x00\x02`\x00\x01\x00E\xc0\x16'
    cmd = ''.join(["%02X" % item for item in data]).strip()

    value_json = {
        "term_no": "10000808",
        "order_num": "20241022",
        "cmd": cmd,
    }
    add_command(key_json, value_json)


    # key = redis_tools.generate_key(key_json["eq_id"], key_json["operation_type"])
    # result = expire_command(key)
    # # result = get_command(key)
    # print(result, type(result))

