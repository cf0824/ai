"""
示例接口
"""
from app.models import SUserInfo
from app.utils.comm import api_handle
from app.utils import Error
from app.utils import MyLog
from app.models import *

log = MyLog.log


# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


# 示例接口
def test(request, data, resp):
    log.info('请求信息=%s' % data)
    log.info('demo test')
    resp['tip'] = 'demo test'
    return resp


# 测试错误接口
def test_error(request, data, resp):
    return Error.TEST_ERROR



# 测试错误接口
def test_model(request, data, resp):
    a = SUserInfo.objects.filter()
    log.info('a=%s'%a)
    b = a
    a = a.filter(user_id=2)
    log.info('a=%s,b=%s'%(a,b))
    return resp


global_vars = globals()
print(global_vars)


