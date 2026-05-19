#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：handle_sim.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/5/13 11:44 
@Description :
'''
import os
import hashlib
import datetime
import requests
from admin_cfg.settings import USERNAME, PASSWORD, URL
from admin_app.utils import MyLog

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

url = URL
def md5_hash(text):
    # 创建MD5哈希对象并传入编码后的字节
    hash_object = hashlib.md5(text.encode('utf-8'))
    # 返回十六进制哈希字符串
    return hash_object.hexdigest()


def query_card_info(iccid):
    time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    passWord = md5_hash(md5_hash(PASSWORD) + time_str)
    data = {
        "userName": USERNAME,
        "passWord": passWord,
        "tKey": time_str,
        "iccid": iccid
    }
    r = requests.post(url, json=data)
    log.info(f'物联网卡查询结果：{r}')
    log.info(f'response: {r.json()}')
    return r.json()

# # 示例使用
# text = "5I2@J4@u"
# print("MD5哈希值:", md5_hash(text))
# # time_str = '20160315120530'
# time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
# print(time_str)
# print("密码串：:", md5_hash(md5_hash(text) + time_str))