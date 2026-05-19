#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：time_range.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/3/20 10:32 
@Description :
'''
import calendar
from datetime import datetime, time, timedelta
from itertools import chain
# import pytz
from django.utils import timezone


def generate_time_ranges(granularity, year=None, month=None, day=None):
    """生成完整时间维度列表（支持年-月、日-小时）"""
    if granularity == 'year_months':
        # 生成某年所有月份列表 [1月, 2月...12月]
        return [datetime(year, m, 1).date() for m in range(1, 13)]

    elif granularity == 'month_days':
        # 生成某月所有日期列表 [1号, 2号...月末]
        _, num_days = calendar.monthrange(year, month)
        return [datetime(year, month, day).date() for day in range(1, num_days + 1)]

    elif granularity == 'day_hours':
        # 生成某天24小时列表 [00:00, 01:00...23:00]
        base_date = datetime(year, month, day)
        return [datetime.combine(base_date, time(hour=h)) for h in range(24)]

    # 时区敏感版本（当 USE_TZ=True 时使用）
    elif granularity == 'day_hours_aware':
        tz = timezone.get_current_timezone()
        base_date = tz.localize(datetime(year, month, day))
        return [base_date + timedelta(hours=h) for h in range(24)]