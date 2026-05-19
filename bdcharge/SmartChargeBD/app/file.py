import os
import hashlib
from SmartChargeBD.settings import FILE_UPLOAD_DIR, FILE_UPLOAD_RELATIVE_DIR
from django.http.response import HttpResponseBadRequest, HttpResponse
from app.utils import uploadUtil
from app.utils import MyLog
from SmartChargeBD.settings import BASE_DIR
import datetime
import decimal

import asyncio
import json
import time

from app.utils.comm import api_handle
from app.utils import Error
from app.models import *
from app.utils.tools import haversine
from django.db import transaction
from django.db.models import F
import datetime
from django.core.paginator import Paginator
import random
import decimal
from SmartChargeBD.settings import BASE_DIR
from django.shortcuts import HttpResponse
from app.utils.eq_api import tieta_handle2
from app.utils.get_seq import Get_SeqNo
from app.utils.handle import charge_open, charge_stop
from django.db import connection
# from ..utils import MyLog
from app.tcp_socket import TCPHandler
from app.command.hardware_api import HardwareApi
from app.shell import req_term

log = MyLog.MyLog(__file__, 'file.log', BASE_DIR).logger

import json

upload_obj = uploadUtil.TencentCOS()

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

def test(request):
    return HttpResponse('a')

def upload_tencent(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    # token = request.META.get('HTTP_TOKEN')
    # 校验token
    flag = True
    if not flag:
        return HttpResponseBadRequest()
    # print('request.FILES=',request.FILES)
    file = request.FILES.get('file')
    msg = {}
    if not file:
        msg['code'] = 400
        msg['msg'] = "上传的图片不能为空"
        return msg
    print(f'file:{file}')
    print('file.name=',file.name)
    res = upload_obj.tencent_cos_upload(file)
    return HttpResponse(res)
