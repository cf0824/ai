import base64
import sys
from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR



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



# 获取订单功率曲线
def get_order_p_line(request, data, resp):
    form_data = data.get('form_data',{})
    order_id = form_data.get('order_id')
    if not order_id:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()

    def get_data_kv(data_k):
        _data_kv = {}
        sql = "select attr_value,DATE_FORMAT(create_time,'%%m/%%d %%H:%%i') from s_eq_attr_data where order_id=%s and attr_key=%s order by id"
        cursor.execute(sql, (order_id, data_k))
        rows = cursor.fetchall()
        for v, time in rows:
            _data_kv[time] = v
        return _data_kv

    def merge_set_list(*arglist):
        _tmp = []
        for item in arglist:
            _tmp += item
        return list(set(_tmp))

    v_data_kv = get_data_kv('_charge_v')
    a_data_kv = get_data_kv('_charge_a')
    elec_data_kv = get_data_kv('_charge_elect')
    money_data_kv = get_data_kv('_charge_money')


    labels = merge_set_list(v_data_kv.keys(),a_data_kv.keys(),elec_data_kv.keys(),money_data_kv.keys())
    labels.sort()
    v_data = []
    a_data = []
    elec_data = []
    money_data = []
    # todo
    for label in labels:
        v_data.append(v_data_kv.get(label,0))
        a_data.append(a_data_kv.get(label,0))
        elec_data.append(elec_data_kv.get(label,0))
        money_data.append(money_data_kv.get(label,0))

    p_data = []
    for i, v in enumerate(v_data):
        p = round(float(v) * float(a_data[i]), 2)
        p_data.append(p)

    form_var = {}
    form_var['chartdata1'] = {
        'data':[
            {
                'name': '电压',
                'type': 'line',
                'data': v_data,
                'color':'#5470c6'
            },
            {
                'name': '电流',
                'type': 'line',
                'data': a_data,
                'color':'#91cc75'
            },
            {
                'name': '功率',
                'type': 'line',
                'data': p_data,
                'color': '#fac858'
            },
            {
                'name': '电量',
                'type': 'line',
                'data': elec_data,
                'color':'#ee6666'
            },
            {
                'name': '消费金额',
                'type': 'line',
                'data': money_data,
                'color':'#909399'
            }
        ],
        'labels': labels,
        'legend': ['电压', '电流', '功率', '电量', '消费金额']
    }
    resp['form_var'] = form_var
    return resp
