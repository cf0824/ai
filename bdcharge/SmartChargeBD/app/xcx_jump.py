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

import os
from app.utils import MyLog
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

# settings.py
WECHAT_CONFIG = {
    'APP_ID': 'wxed9559c9c99d2798',
    'APP_SECRET': '4ec18fab1cc7a47e3b99cec2ea0d7a43',
    'SCHEME_URL': 'https://api.weixin.qq.com/wxa/generatescheme',
}
# utils/wx_tool.py
import requests
from django.core.cache import cache

import time


def get_access_token():
    """获取微信access_token"""
    # 尝试从缓存获取token
    token = cache.get('wx_token')
    log.info(f'缓存catch:{cache}')

    if token:
        # 检查token有效性（通过调用一个简单的微信API）
        test_url = f'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={token}'
        try:
            resp = requests.get(test_url, timeout=5).json()
            if 'errcode' in resp and resp['errcode'] in [40001, 42001]:  # token无效或过期
                log.info(f'缓存中的token已过期: {resp}')
                token = None
            else:
                log.info(f'缓存中的token有效:{token}')
                return token
        except Exception as e:
            log.error(f'检查token有效性时出错: {e}')
            # 如果检查失败，保守起见重新获取
            token = None

    # 重新获取token
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
        # 设置缓存，使用微信返回的expires_in（默认7200秒）
        expires_in = resp.get('expires_in', 7200)
        cache.set('wx_token', token, expires_in - 60)  # 提前60秒过期

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