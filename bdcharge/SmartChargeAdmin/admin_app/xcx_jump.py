#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：xcx_jump.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/12/9 11:20 
@Description :
'''
import requests
from django.core.cache import cache
import hashlib
import json
import time

from admin_app.utils import MyLog

log = MyLog.log
# settings.py
WECHAT_CONFIG = {
    'APP_ID': 'wxed9559c9c99d2798',
    'APP_SECRET': '4ec18fab1cc7a47e3b99cec2ea0d7a43',
    'SCHEME_URL': 'https://api.weixin.qq.com/wxa/generatescheme',
}
# utils/wx_tool.py
import requests
from django.core.cache import cache


def get_access_token():
    """获取微信access_token"""
    token = cache.get('wx_token')
    if token:
        return token

    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type': 'client_credential',
        'appid': WECHAT_CONFIG['APP_ID'],
        'secret': WECHAT_CONFIG['APP_SECRET'],
    }

    resp = requests.get(url, params=params).json()
    log.info(f'获取token结果：{resp}')
    token = resp.get('access_token')
    if token:
        cache.set('wx_token', token, 7000)  # 缓存2小时
    return token


def generate_scheme(path, **kwargs):
    """生成小程序scheme"""
    token = get_access_token()
    log.info(f'获取token:{token}')
    if not token:
        return None

    url = f"{WECHAT_CONFIG['SCHEME_URL']}?access_token={token}"

    # 构建query字符串
    query = '&'.join([f"{k}={v}" for k, v in kwargs.items()])

    data = {
        "jump_wxa": {
            "path": path,
            "query": query,
        }
    }

    resp = requests.post(url, json=data).json()
    log.info(f'获取scheme的结果：{resp}')
    return resp.get('openlink') if resp.get('errcode') == 0 else None


# views.py
from django.shortcuts import render


def jump_to_mini(request):
    """
    中转跳转页面
    参数：?path=小程序页面路径&其他参数
    """
    path = request.GET.get('path', 'pages/Charge/Choosepile')
    log.info(f'跳转小程序')

    # 获取其他参数
    params = {}
    log.info(f'request: {request}')
    log.info(f'request.get: {request.GET}')
    for key in request.GET:
        if key != 'path':
            params[key] = request.GET.get(key)

    # 判断是否微信环境
    is_wechat = 'MicroMessenger' in request.META.get('HTTP_USER_AGENT', '')
    log.info(f'is_wechat: {is_wechat}')

    # 生成scheme
    scheme = generate_scheme(path, **params) if is_wechat else None
    log.info(f'scheme: {scheme}')

    return render(request, 'jump.html', {
        'is_wechat': is_wechat,
        'scheme': scheme,
        'path': path,
        'params': params,
    })