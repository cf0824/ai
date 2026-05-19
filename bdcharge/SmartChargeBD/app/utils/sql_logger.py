#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：sql_logger.py.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/6/7 17:27 
@Description :
'''
# app/utils/sql_logger.py
import logging
import inspect
import os
from django.conf import settings


class ORMSourceFormatter(logging.Formatter):
    """可靠的自定义SQL日志格式化器"""

    def format(self, record):
        # 确保记录原始SQL
        original = super().format(record)

        # 获取调用堆栈
        stack = inspect.stack()
        try:
            # 查找用户代码位置
            for frame_info in stack:
                filepath = frame_info.filename
                # 排除Django内部文件
                if 'django' not in filepath and 'site-packages' not in filepath:
                    # 获取相对路径
                    try:
                        rel_path = os.path.relpath(filepath, settings.BASE_DIR)
                        func_name = frame_info.function

                        # 返回带有源位置的格式化字符串
                        return f"[{record.asctime}] [{rel_path}:{frame_info.lineno}] - {func_name}()\n  ↳ SQL: {record.message}"
                    except Exception:
                        # 发生错误时回退
                        break
        finally:
            del stack

        # 默认格式化
        return original