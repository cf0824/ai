"""
示例接口
"""
from django.db import transaction

from app.models import *

from app.models import SUserInfo
from app.utils.comm import api_handle
from app.utils import Error
from app.utils import MyLog
from app.utils import Error
import datetime
from django.db.models import F

log = MyLog.log


# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


# 示例接口
@transaction.atomic
def test(request, data, resp):
    if not data.get('ur_id'):
        return Error.REQ_PARAMS_ERROR

    # 提取金额
    retail_out = float(data.get('change_out_money'))
    # 设置回滚点
    sid = transaction.savepoint()
    # 先查询
    for i in range(0, 3):
        list_data = SUserInfo.objects.filter(user_id=data.get('ur_id'))
        if not list_data.exists():
            resp['tip'] = '账户不存在'
            return resp
        old = float(list_data[0].account)
        if old < retail_out:
            transaction.savepoint_rollback(sid)
            resp['tip'] = '余额不足'
            return resp
        result = SUserInfo.objects.filter(user_id=data.get('ur_id'),
                                          account__gte=retail_out).update(
            account=F('account') - retail_out)
        if result == 0:
            if i == 2:
                transaction.savepoint_rollback(sid)
                resp['tip'] = '提取失败'
                return resp
            continue
        break
    SAccountDetail.objects.create(
        change_type='out',
        change_money=data.get('change_out_money'),
        user_id=data.get('ur_id'),
        create_time=datetime.datetime.now(),
        # todo 关联订单号

    )
    transaction.savepoint_commit(sid)


    resp['tip'] = '提交成功'
    return resp

    # nowout = float(data.get('change_money'))
    # # 求和
    # list_data = SUserInfo.objects.filter(user_id=data.get('ur_id')).first()
    # money = float(list_data.account)
    # money -= nowout
    # if money>0:
    #     resp['tip'] = '余额不足'
    #     return resp
    # # todo 向微信添加数据
    # # list_data = SWxTranDetail()
    #
    # # 保存点
    # sid = transaction.savepoint()
    #
    # list_data_a = SAccountDetail(
    #     change_type='out',
    #     change_money=data.get('change_money'),
    #     user_id=data.get('ur_id'),
    #     create_time=datetime.datetime.now(),
    #     # todo 关联订单号
    #
    # )
    # try:
    #     money ==
    #     list_data_a.save()
    # except:
    #     resp['tip'] = '提交失败'
    #     return resp
    #
    # resp['success'] = True
    # resp['tip'] = '提现订单提交成功!'
    # return resp


# 测试错误接口
def test_error(request, data, resp):
    return Error.TEST_ERROR
