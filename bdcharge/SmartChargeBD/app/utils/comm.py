import time

from django.shortcuts import render, HttpResponse, redirect
import json
import decimal
import datetime
from . import Error
from . import MyLog
from SmartChargeBD.settings import NO_AUTH_API
from app.utils import token_handle

log = MyLog.log


# 将date datetime decimal类型转换为json
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


# 返回格式化的json
def return_resp(resp):
    s = json.dumps(resp, cls=MyJSONEncoder)
    log.info(f's:{s}')
    return HttpResponse(s)


# 校验用户权限
def check_user(request, api):
    # return True,1
    # token = request.META.get('HTTP_AUTHORIZATION')
    token = request.META.get('HTTP_TOKEN')
    # if token == 'f2882e9f099ffbd833b98f733cb2308b':  # 测试用户token
    #     return True, 3
    # if token == 'Sf2882e9f099ffbd833b98f733cb2308bS':  # 测试用户token
    #     return True, 5
    if token == 'Sf2882e9f099ffbd833b98f733cb2308bS':  # 测试用户token
        return True, 1
    is_pass, token_data = token_handle.verify_token(token)
    # print('验证token=%s,is_pass=%s,token_data=%s' % (token, is_pass, token_data))
    log.info('验证token=%s,is_pass=%s,token_data=%s' % (token, is_pass, token_data))
    if not is_pass:
        return False, 0
    # token_type = token_data.get('token_type')
    # if token_type != 'grant':
    #     return False, 0
    grant_api = token_data.get('grant_api',[])
    if api not in grant_api:
        return False, 0
    user_id = token_data.get('user_id', 0)
    return True, user_id


# 统一处理函数.
def api_handle(request, gb):
    log.info(f'request={request}')
    if request.method != 'POST':
        return return_resp(Error.REQ_TYPE_ERROR)
    # log.info(f'gb = {gb}')
    # log.info(f'META={request.META}')
    # log.info(f'POST={request.POST}')
    # log.info(f'GET={request.GET}')
    # log.info(f'body={request.body}')
    data = json.loads(request.body.decode())
    log.info(f'data={data}')
    tran_type = data.get('tran_type')
    log.info('tran_type=%s' % tran_type)
    # 定义默认返回结构体
    resp = {
        'code': 0,
        'msg': 'success',
        'tran_type': tran_type
    }
    names = gb.get('__name__', '')
    api = names.split('.')[-1]
    log.info(f'api={api}')
    # 校验用户
    flag, user_id = check_user(request, api)
    # 不需要授权接口
    not_auth_tran_type_list = NO_AUTH_API.get(api, [])
    if tran_type in not_auth_tran_type_list:
        flag = True
    # if api == 'devops':
    #     flag = True
    #     user_id = 1
    # 未授权提示
    if not flag:
        return return_resp(Error.USER_CHECK_FAIL)
    data['user_id'] = user_id
    if gb.get(tran_type):
        # 执行处理函数
        log.info('请求data=%s' % data)
        begin_time = time.time()
        log.info('函数%s开始执行' % tran_type)
        try:
            resp = gb[tran_type](request, data, resp)
            log.info(f'response={resp}')
        except Exception as e:
            log.error('系统错误：%s' % e, exc_info=True)
            return return_resp(Error.SYSTEM_ERROR)
        end_time = time.time()
        log.info(f'函数{tran_type}执行完毕，用时{int(end_time*1000 - begin_time*1000)}毫秒')
    else:
        # 函数不存在
        resp = Error.API_ERROR
    return return_resp(resp)
