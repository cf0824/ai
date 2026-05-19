import base64
import sys
from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from admin_app.tranapp import gfcrc
from admin_app.tools.bank import make_word



# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


# 测试
def test(request, data, resp):
    log = public.logger
    log.info('test begin')
    resp['detail'] = {'a': 1, 'b': 2}
    return resp



def download_test(request, data, resp):
    with open(public.localhome+"fileup/e0c2a4f8201e160f0e7fa5f4db88024d.jpg", 'rb') as f:
        base64_data = base64.b64encode(f.read())
        file_base64 = base64_data.decode()
        resp['respcode'] = '125800'
        resp['filename'] = 'test.jpg'
        resp['filetype'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        resp['filedata'] = file_base64
        return resp


def download_quota_res(request, data, resp):
    filename = '指标评价结果_20210606_2.docx'
    make_word.make_word(filename)
    with open(public.localhome+"rmbank/%s"%filename, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        file_base64 = base64_data.decode()
        resp['respcode'] = '125800'
        resp['filename'] = filename
        resp['filetype'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        resp['filedata'] = file_base64
        return resp