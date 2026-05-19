import json
import time
from importlib import import_module
from urllib import parse

from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from admin_app.apps import IrsAdminConfig
from admin_app.utils import Error, wx
from admin_app.utils import MyLog
from admin_app.utils.comm import return_resp, MyJSONEncoder
from admin_app.utils.gm import g
from admin_cfg.settings import NO_AUTH_API, ROOT_API, WEB_API

import urllib.parse

log = MyLog.log


# 用户授权
def user_grant(request, data):
    # referer = request.META.get('HTTP_REFERER', '')
    log.info(data)
    referer = data.get('location', '')
    log.info(referer)
    # redirect_uri = f'{ROOT_API}/wx_login'

    redirect_uri = f'{WEB_API}/wx_login'
    wechat_oauth_url = wx.get_wechat_auth_url(referer, redirect_uri)
    log.info(f'wechat_oauth_url={wechat_oauth_url}')
    resp = {
        'code': 301,
        'msg': '未授权',
        'url': wechat_oauth_url
    }
    return return_resp(resp)


# 去授权
def toGrantUrl(real_url):
    real_url = parse.quote(real_url, safe='')
    log.info(real_url)
    redirect_uri = f'{ROOT_API}/wx_login'
    wechat_oauth_url = wx.get_wechat_auth_url(real_url, redirect_uri)
    log.info(f'wechat_oauth_url={wechat_oauth_url}')
    return wechat_oauth_url


class NoGrantError(Exception):
    pass


@csrf_exempt
def get_api_handle(api_key="wxapi"):
    def api_handle(request):

        log.info("get_api_handle请求path:[%s]" % request)
        log.info("get_api_handle请求path:[%s]" % request.path)
        log.info("get_api_handle请求method:[%s]" % request.method)
        log.info("get_api_handle请求GET:[%s]" % request.GET)

        data = json.loads(request.body.decode())

        if request.method != 'POST':
            return return_resp(Error.REQ_TYPE_ERROR)

        # 获取当前请求的 URL 地址
        current_url = request.build_absolute_uri()
        # 获取请求的接口路径
        path_info = request.path_info.lstrip('/')
        if not path_info:
            return return_resp(Error.API_ERROR)

        # 获取接口所在模块目录
        try:
            api_module = path_info.split('/')[1]
        except:
            return return_resp(Error.API_ERROR)

        # 获取包含{api_module}目录的app的名称
        app_name = IrsAdminConfig.name

        # 将接口路径转换为 Python 模块和方法名
        try:
            module_name, method_name = path_info.split('/')[-2:]
        except:
            return return_resp(Error.API_ERROR)

        try:
            # 导入指定模块
            module = import_module(f'{app_name}.{api_module}.{module_name}')
            # 获取指定方法
            method = getattr(module, method_name)

        except (ImportError, AttributeError):
            # 模块或方法不存在
            return return_resp(Error.API_ERROR)

        # 定义默认返回结构体
        resp = {
            'code': 200,
            'msg': 'success'
        }

        log.info('请求data=%s' % data)
        log.info('请求header=%s' % request.META)
        log.info(f'请求api_module={api_module}，module_name={module_name}，api_name={method_name}')

        # 检查用户是否已登录，如果是不需要token的路由则跳过token验证
        sub_path = path_info.replace(f"{api_key}", '')
        log.info(sub_path)
        # 去鉴权
        try:
            flags, user_id = validate_user(request, sub_path)
        except NoGrantError:
            return user_grant(request, data)

        if not flags:
            return return_resp(Error.USER_CHECK_FAIL)

        begin_time = time.time()
        try:
            g.request = request
            g.data = data
            g.resp = resp
            g.user_id = user_id
            # g.request.session['user_id'] = 65
            api_module_value = import_module(f'{app_name}.{api_module}.{module_name}')
            resp = getattr(api_module_value, method_name)(data, resp)
            log.info('resp=%s' % resp)
        except Exception as e:
            print('error', e)
            log.error('error', exc_info=True)
            return return_resp(Error.SYSTEM_ERROR)
        end_time = time.time()
        use_time = int(end_time * 1000 - begin_time * 1000)
        if use_time > 100:
            log.info(f'函数%s执行完毕，用时{use_time}ms' % method_name)
        if not resp or type(resp) != dict:
            return return_resp(Error.RESP_DATA_ERROR)
        # 执行方法并返回结果
        return HttpResponse(json.dumps(resp, cls=MyJSONEncoder))
        # return method(request)

    return api_handle


# TODO: 验证路由是否需要  验证
def validate_user(request, path_info):
    # user_id = 65
    # request.session['user_id'] = user_id
    # return True, user_id

    user_id = request.session.get('user_id')
    log.info(user_id)
    if not user_id:
        raise NoGrantError
    return True, user_id
