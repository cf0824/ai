#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：upload_file.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/4/1 16:50 
@Description :
'''
import os
from admin_app.utils import MyLog

import hashlib
from admin_cfg.settings import FILE_UPLOAD_DIR, FILE_UPLOAD_RELATIVE_DIR
from django.http.response import HttpResponseBadRequest, HttpResponse
from admin_app.utils import uploadUtil

# from SmartChargeBD.settings import BASE_DIR
from django.shortcuts import HttpResponse

import decimal
import datetime


import json

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

upload_obj = uploadUtil.TencentCOS(log)

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        super(MyJSONEncoder, self).default(o)

def return_resp(resp):
    s = json.dumps(resp, cls=MyJSONEncoder)
    log.info(f'resp:{s}')
    return HttpResponse(s)

def upload(request):
    token = request.META.get('HTTP_TOKEN')
    # 校验token
    flag = True
    if not flag:
        return HttpResponseBadRequest()
    # print('request.FILES=',request.FILES)
    file = request.FILES.get('file')
    print(f'file:{file}')
    print('file.name=',file.name)
    # 文件后缀
    filename_ext = file.name.split('.')[-1]
    # 获取文件内容到变量中
    b_data = b''
    for line in file.chunks():
        b_data = b_data + line

    # 生成md5值的文件名
    m2 = hashlib.md5()
    m2.update(b_data)
    md5filename = m2.hexdigest() + '.' + filename_ext
    del file
    # 判断文件是否存在,存在不处理，不存在则写处
    if not os.path.exists(FILE_UPLOAD_DIR + md5filename):
        # 写入本地指定目录
        with open(FILE_UPLOAD_DIR + md5filename, 'wb') as f:
            f.write(b_data)
        f.close()

    # 相对链接
    relative_url = f'{FILE_UPLOAD_RELATIVE_DIR}{md5filename}'
    return HttpResponse(relative_url)

def upload_tencent(request):
    log.info(f'---------腾讯云上传文件-------')
    if request.method != 'POST':
        return HttpResponseBadRequest()
    # token = request.META.get('HTTP_TOKEN')
    # 校验token
    # print('request.FILES=',request.FILES)
    file = request.FILES.get('file')
    log.info(f'file:{file}')
    res = {}
    if file is None:
        res['code'] = 400
        res['msg'] = "上传的图片不能为空"
        return return_resp(res)
    log.info(f'file:{file}')
    log.info(f'file.name={file.name}')
    log.info(f'file.size={file.size}')
    try:
        res = upload_obj.tencent_cos_upload(file)
    except Exception as e:
        log.error(f'上传失败：{e}', exc_info=True)
    return return_resp(res)
