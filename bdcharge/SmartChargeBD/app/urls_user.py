#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeLQ-master 
@File    ：urls_user.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/14 15:54 
'''
from django.urls import path

from app.api import user

urlpatterns = [
    path('test', user.test),
    path('get_account_info', user.get_account_info),
    # path('v2/Accounts/FaceSyncTasks', charge.get_users_info),
    # path('v2/Accounts/FaceSyncTasks', charge.get_users_info),
]