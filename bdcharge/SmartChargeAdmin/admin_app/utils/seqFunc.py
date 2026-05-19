#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  SchoolConsumeBackend -> seqFunc.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   seqFunc.py
@Time    :   2024/5/14 17:20
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
import datetime
from admin_app.utils.redisFunc import RedisDb as redis


class SerialNumberGenerator:
    def __init__(self, default_length=6):
        self.r = redis()
        self.default_length = default_length

    # 设置流水号前缀和长度
    def set_prefix_and_length(self, prefix, length):
        self.r.set_value(f'{prefix}', length)

    def exists_prefix_and_length(self, prefix):
        return self.r.check_key_exists(f'{prefix}')

    def set_expires_prefix_and_length(self, prefix, ex=24 * 60 * 60):
        self.r.expire_key(prefix, ex)  # 设置过期时间为24小时

    # 获取今天的流水号
    def get_today_serial_number(self, prefix='', length=None):
        # 获取今天的日期（YYYYMMDD格式）作为流水号前缀
        today_prefix = datetime.date.today().strftime('%Y%m%d')
        if prefix:
            today_prefix = prefix + today_prefix

        final_length = length if length is not None else self.default_length
        initial_value = '0' * final_length

        final_today_prefix = today_prefix + initial_value
        # # 检查是否存在今天的流水号键
        if not self.exists_prefix_and_length(final_today_prefix):
            self.set_prefix_and_length(final_today_prefix, 0)
            self.set_expires_prefix_and_length(final_today_prefix)

        # 递增流水号，并确保其长度
        serial_number = int(self.r.increment_value(final_today_prefix))

        formatted_serial_number = f"{serial_number:0{final_length}d}"

        return formatted_serial_number


# 使用示例
generator = SerialNumberGenerator()

