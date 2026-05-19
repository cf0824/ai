#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：redis_tools.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/22 10:16 
@Description : 处理redis键、值
'''
import datetime
import time
# from redisFunc import RedisDb
from app.command.terminal_dict import terminal_dict
import json
class RedisTools:
    def __init__(self):
        pass

    def generate_key(self, head):
        """
        生成key
        :param eq_id: 设备号 str
        :param operation_type: 操作类型 str
        :return: key str
        """
        # time_str = datetime.date.today()
        time_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        key = f'{head}_{time_now}'

        return key



if __name__ == '__main__':
    redis_tools = RedisTools()
    # Rdb = RedisDb()
    json1 = {
        "eq_id": "008",
        "operation_type": "Socket_start_stop"
    }
    eq_id = json1["eq_id"]
    operation_type = json1["operation_type"]

    key = redis_tools.generate_key(eq_id)
    value = {}
    value["operation_type"] = terminal_dict.get(operation_type)
    value = json.dumps(value)
    # Rdb.set_value(key, value)
    print(key)
    print(value)
    print(str(int(time.time() * 1000)))
    print(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d%H%M%S%f'))