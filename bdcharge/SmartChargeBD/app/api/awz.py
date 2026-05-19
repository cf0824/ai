"""
示例接口a
"""
# from app.models import SEqPort, SEqInfo, SUserinfo
from app.utils.comm import api_handle
from app.utils import Error
from app.utils import MyLog
from app.models import *
from django.db import transaction
from app.models import SUserInfo


import datetime

log = MyLog.log


# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)




@transaction.atomic
# 示例接口
def test(request, data, resp):
    eq_id=data.get('eq_id')
    user_id = data.get('user_id')
    state = data.get('state')
    charge_electric = data.get('charge_electric')
    charge_money = data.get('charge_money')
    charge_type = data.get('charge_type')
    if not eq_id :
        return Error.REQ_PARAMS_ERROR
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    info_eq = SEqInfo.objects.filter(eq_id = eq_id)
    info_port = SEqPort.objects.filter(eq_id = eq_id)
    info_SUserinfo = SUserInfo.objects.filter(user_id = user_id)
    expenses = 10
    account = info_SUserinfo.account
    bill_rule = 1.1

    if state == 1:
        return Error.REQ_TYPE_ERROR

    if charge_type == 'auto':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - expenses #自动充电
    elif charge_type == 'elec':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_electric * bill_rule
            account = account - out
    elif charge_type == 'money':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_money
            account = account - out
    elif charge_type == 'time':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - 10 #时长算法

    SAccountDetail.objects.create(
        change_type = 'out',
        user_id = data.get('user_id'),
        change_money= data.get('change_money'),
        order_id = data.get('order_id'),
        create_time=datetime.datetime.now()
    )
    SOrderInfo.objects.create(
        eq_id = data.get('eq_id'),
        eq_port = data.get('eq_port'),
        charge_type= charge_type,
        charge_time = data.get('charge_time'),
        charge_money = out,
        account = account,
        user_id = user_id,
        order_id = data.get('order_id'),
        create_time=datetime.datetime.now(),
        state = 1
    )
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp

    #expenses = float(data.get('change_out_money')) expenses = 10

    #判断设备和端口占用情况，设备信息表，设备端口信息表
    #else:
     #   state=2
    #保存点save_id = transaction.savepoint()
    #扣除用户余额
    #增加账户记录
    #创建订单




# 测试错误接口
def test_error(request, data, resp):
    return Error.TEST_ERROR
"""

    eq_id=data.get('eq_id')
    user_id = data.get('user_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    info_eq = SEqInfo.objects.filter(eq_id = eq_id)
    info_port = SEqPort.objects.filter(eq_id = eq_id)
    info_SUserinfo = SUserinfo.object.filter(user_id = user_id)
    state = data.get('state')
    charge_type = data.get('charge_type')
    expenses = 10
    account = info_SUserinfo.account
    bill_rule = 1.1
    charge_electric = data.get('charge_electric')
    charge_money = data.get('charge_money')
    if state == 1:
        return Error.REQ_TYPE_ERROR

    if charge_type == 'auto':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - expenses #自动充电
    elif charge_type == 'elec':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_electric * bill_rule
            account = account - out
    elif charge_type == 'money':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_money
            account = account - out
    elif charge_type == 'time':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - 10 #时长算法

    SAccountDetail.objects.create(
        change_type = 'out',
        user_id = data.get('user_id'),
        change_money= data.get('change_money'),
        order_id = data.get('order_id'),
        create_time=datetime.datetime.now()
    )
    SOrderInfo.objects.create(
        eq_id = data.get('eq_id'),
        eq_port = data.get('eq_port'),
        charge_type= charge_type,
        charge_time = data.get('charge_time'),
        charge_money = out,
        account = account,
        user_id = user_id,
        order_id = data.get('order_id'),
        create_time=datetime.datetime.now(),
        state = 1
    )
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp





site_id=data.get('site_id')
    list = SSiteInfo.objects.filter(site_id=site_id)
    list_all=[]
    for i in list:
        list_all.append(
            {
                'site_id':i.site_id,
                'site_name':i.site_name,
                'site_address':i.site_address,
                'site_gps':i.site_gps,
                'site_desc':i.site_desc
            }
        )
        # data_A['site_id']=i.site_id
        # data_A['site_name']=i.site_name
        # list_all.append(data_A)
    resp['list_all']=list_all
    return resp
    
    
     eq_id=data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    list_eq = SEqInfo.objects.filter(eq_id=eq_id)
        #SSiteInfo.objects().all()
    list_pa=[]
    for i in list_eq:
        list_pa.append(
            {
                'eq_code':i.eq_code,
                'state':i.state,
                'eq_state':i.eq_state
            }
        )
        # data_A['site_id']=i.site_id
        # data_A['site_name']=i.site_name
        # list_all.append(data_A)
    resp['list_pa']=list_pa
    return resp
    
    
    details = {}
    details['eq_id'] = infor_eq.eq_id
    details['rated_power'] = infor_eq.rated_power
    details['state'] = infor_eq.state
    details['eq_state']=infor_eq.eq_state
    details['soft_version'] = infor_eq.soft_version
    details['agree_version'] = infor_eq.agree_version
    
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    info_eq = SEqInfo.objects.get(eq_id = eq_id)
    detail_eq = {}
    detail_eq['eq_id'] = info_eq.eq_id
    detail_eq['rated_power'] = info_eq.rated_power
    detail_eq['state'] = info_eq.state
    detail_eq['eq_state'] = info_eq.eq_state
    detail_eq['soft_version'] = info_eq.soft_version
    detail_eq['agree_version'] = info_eq.agree_version
    resp['detail_eq'] = detail_eq
    return resp
    
    
    
    
    
    
    order_id=data.get('order_id')
    if not order_id:
        return Error.REQ_PARAMS_ERROR
    info_order = SOrderInfo.objects.filter(order_id=order_id)
    detail_order = {}
    detail_order['order_id'] = info_order.order_id
    detail_order['eq_id'] = info_order.eq_id
    detail_order['user_id'] = info_order.user_id
    detail_order['eq_port'] = info_order.eq_port
    detail_order['charge_type'] = info_order.charge_type
    detail_order['charge_time'] = info_order.charge_time
    detail_order['use_money'] = info_order.use_money
    resp['detail_order']=detail_order
    return resp
    
    order_id = data.get('order_id')
    if not order_id:
        return Error['REQ_PARAMS_ERROR']
    try:
        info_order = SOrderInfo.objects.get(order_id=order_id)
    except:
        return Error['NOT_FOUND']
    detail_order = {}
    detail_order['order_id'] = info_order.order_id
    detail_order['eq_id'] = info_order.eq_id
    detail_order['user_id'] = info_order.user_id
    detail_order['eq_port'] = info_order.eq_port
    detail_order['charge_type'] = info_order.charge_type
    detail_order['charge_time'] = info_order.charge_time
    detail_order['use_money'] = info_order.use_money
    resp['detail_order']=detail_order
    return resp
    
    
    detail_eq = {}
    detail_eq['site_id'] = info_eq.site_id
    detail_eq['eq_id'] = info_eq.eq_id
    detail_eq['state'] = info_eq.state
    detail_eq['bill_rule'] = info_eq.bill_rule
    detail_eq['eq_state'] = info_eq.eq_state
    
    if state == 0:
        if :#自动充电
            if account < expenses :

            else:
                account = account - expenses
        elif :#定电量充电
            if account < expenses :

            else:
                account = account - expenses
        elif :#定金额充电
            if account < expenses :

            else:
                account = account - expenses
        elif :#定时充电
            if account < expenses :

            else:
                account = account - expenses
    elif state == 1:
        state == 1
    
    
    
       eq_id=data.get('eq_id')
    user_id = data.get('user_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    info_eq = SEqInfo.objects.filter(eq_id = eq_id)
    info_port = SEqPort.objects.filter(eq_id = eq_id)
    info_SUserinfo = SUserinfo.object.filter(user_id = user_id)
    state = data.get('state')
    charge_type = data.get('charge_type')
    expenses = 10
    account = info_SUserinfo.account
    bill_rule = 1.1
    charge_electric = data.get('charge_electric')
    charge_money = data.get('charge_money')
    if state == 1:
        return Error.REQ_TYPE_ERROR

    if charge_type == 'auto':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - expenses #自动充电
    elif charge_type == 'elec':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_electric * bill_rule
            account = account - out
    elif charge_type == 'money':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = charge_money
            account = account - out
    elif charge_type == 'time':
        if account < expenses :
            return Error.REQ_PARAMS_ERROR
        else:
            out = 10
            account = account - 10 #时长算法

    SAccountDetail.objects.create(
        id = data.get('user_id'),
        change_out_money = out,
        order_id = data.get('order_id'),
        user_id = user_id,
        create_time=datetime.datetime.now()
    )
    SOrderInfo.objects.create(
        eq_id = data.get('eq_id'),
        eq_port = data.get('eq_port'),
        charge_type= charge_type,
        charge_time = data.get('charge_time'),
        charge_money = out,
        account = account,
        user_id = user_id,
        order_id = data.get('order_id'),
        create_time=datetime.datetime.now(),
        state = 1
    )
    resp['success'] = True
    resp['tip'] = '提交成功'
    return resp
    #expenses = float(data.get('change_out_money'))
    expenses = 10
    #判断设备和端口占用情况，设备信息表，设备端口信息表
    #else:
     #   state=2
    #保存点save_id = transaction.savepoint()
    #扣除用户余额
    #增加账户记录
    #创建订单

    """




