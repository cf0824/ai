import base64
import sys
from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from admin_cfg.settings import APP_API
from admin_app.sys.public_db import Get_SeqNo



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


# 获取计费策略配置
def get_price_mode_cfg(request, data, resp):
    form_data = data.get('form_data', {})
    mode_id = form_data.get('mode_id')
    if not mode_id:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()
    sql = "select begin_time,end_time,price from s_price_mode_detail where mode_id=%s"
    cursor.execute(sql, mode_id)
    rows = cursor.fetchall()
    priceMode = []
    for begin_time,end_time,price in rows:
        priceMode.append({
            'begin_time': begin_time,
            'end_time': end_time,
            'price': price
        })
    resp['form_var'] = {
        'mode_id': mode_id,
        'priceMode': priceMode
    }
    return resp


# 设置费率
@transaction.atomic
def set_price_mode(request, data, resp):
    form_var = data.get('form_var', {})
    mode_id = form_var.get('mode_id')
    priceMode = form_var.get('priceMode')
    if not mode_id or not priceMode:
        return ERROR['REQ_PARAMS_ERROR']
    if len(priceMode) == 0:
        resp = {
            'respcode': '800001',
            'respmsg': '费率设置不能为空'
        }
        return resp
    cursor = connection.cursor()
    sql = "delete from s_price_mode_detail where mode_id=%s"
    cursor.execute(sql, mode_id)
    for cfg in priceMode:
        sql = "insert into s_price_mode_detail(begin_time,end_time,price,mode_id,create_time,state) value(%s,%s,%s,%s,now(),'1')"
        begin_time = cfg.get('begin_time')
        end_time = cfg.get('end_time')
        price = cfg.get('price')
        cursor.execute(sql,(begin_time, end_time, price, mode_id))
    return resp


def str_img2img_list(str_img):
    if not str_img:
        return []
    try:
        _img_list = eval(str_img)
    except:
        return []
    _img_list = [f"{APP_API}{item}" for item in _img_list]
    return _img_list


# 获取运维任务详情
def get_devops_task_detail(request, data, resp):
    form_data = data.get('form_data', {})
    task_id = form_data.get('task_id')
    if not task_id:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()
    sql = "select A.user_id,B.user_name,A.fault_reason,A.repair_way,A.repair_img,A.report_reason,A.create_time,A.finish_time,A.state from s_devops_task_recv A left join s_devops_user_info B on A.user_id=B.user_id where task_id=%s order by recv_id desc limit 1"
    cursor.execute(sql, task_id)
    row = cursor.fetchone()

    if row:
        user_id,user_name,fault_reason,repair_way,repair_img,report_reason,create_time,finish_time,state = row
        detail = {
            'user_id': user_id,
            'user_name': user_name,
            'fault_reason': fault_reason,
            'repair_way': repair_way,
            'repair_img': str_img2img_list(repair_img),
            'report_reason': report_reason,
            'create_time': create_time,
            'finish_time': finish_time,
            'state': state
        }
        form_data.update(detail)
    form_data['state_options'] = [
        {
            "key": "1",
            "value": "处理中"
        },
        {
            "key": "2",
            "value": "已完成"
        },
        {
            "key": "9",
            "value": "已上报"
        }
    ]
    resp['form_var'] = form_data
    return resp


# 上报任务处理
def task_report_handle(request, data, resp):
    form_var = data.get('form_var', {})
    report_id = form_var.get('id')
    task_id = form_var.get('task_id')
    button = request.GET.get('button', '1')
    cursor = connection.cursor()
    if button == '1':
        # 释放任务
        task_state = '0'
        report_state = '1'
    else:
        # 结束任务
        task_state = '9'
        report_state = '9'
    with transaction.atomic():
        sql = "update s_devops_task_info set state=%s where task_id=%s and state='1'"
        row = cursor.execute(sql, (task_state, task_id))
        if not row:
            return ERROR['OPERA_FAIL']
        sql = "update s_devops_task_report set handle_time=now(),state=%s where id=%s and state='0'"
        cursor.execute(sql, (report_state, report_id))
    return resp


# 管理充值(管理员通过管理台给用户充值)
def charge_money_by_admin(request, data, resp):
    form_var = data.get('form_var', {})
    user_id = form_var.get('user_id')
    charge_money = form_var.get('charge_money')
    charge_remark = form_var.get('charge_remark','')
    if not user_id or not charge_money:
        return ERROR['REQ_PARAMS_ERROR']
    try:
        charge_money = float(charge_money)
    except:
        return {
            'respcode':'500101',
            'respmsg':'金额不合法'
        }
    if charge_money <=0:
        return {
            'respcode': '500101',
            'respmsg': '金额不合法'
        }
    cursor = connection.cursor()
    order_id = Get_SeqNo("PAY_ORDER")
    with transaction.atomic():
        sql = "update s_user_info set account=account+%s where user_id=%s"
        row = cursor.execute(sql, (charge_money, user_id))
        if not row:
            return ERROR['OPERA_FAIL']
        sql = "insert into s_account_detail(change_type,change_money,order_id,user_id,remark,create_time) value('in',%s,%s,%s,%s,now())"
        cursor.execute(sql, (charge_money, order_id, user_id, f'[管理充值]{charge_remark}'))
    return resp


# 公告开关
def notice_open(request, data, resp):
    form_var = data.get('form_var', {})
    id = form_var.get('id')
    open_state = request.GET.get('state')
    if not id:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()
    sql = "update s_notice_info set state=%s where id=%s"
    cursor.execute(sql, (open_state, id))
    return resp
