"""
系统消息通知
"""
from django.db import connection
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from django.db.utils import IntegrityError


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


def _get_disable_msg_types(cursor, user_id):
    sql = "select distinct msg_type from (select msg_type from sys_msg_cfg where state='0' union select msg_type from sys_msg_user_cfg where user_id=%s and state='0') tmp"
    cursor.execute(sql, user_id)
    rows = cursor.fetchall()
    res = []
    for msg_type, in rows:
        res.append(msg_type)
    res_str = "','".join(res)
    res_str = "'" + res_str + "'"
    return res_str


# 获取消息数量
def get_msg_count(request, data, resp):
    cursor = connection.cursor()
    msg_types = _get_disable_msg_types(cursor, public.user_id)
    sql = f"select count(*) from sys_msg where user_id=%s and state='0' and msg_type not in ({msg_types})"
    cursor.execute(sql, public.user_id)
    row = cursor.fetchone()
    if not row or not row[0]:
        res = 0
    else:
        res = row[0]

    resp['count'] = res
    return resp


# 获取消息列表
def get_msg_list(request, data, resp):
    page = data.get('page', 1)
    size = data.get('size', 8)
    cursor = connection.cursor()
    msg_types = _get_disable_msg_types(cursor, public.user_id)
    sql = "select dict_code,dict_target from sys_ywty_dict where dict_name='SYS_MSG_TYPE'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    msg_type_kv = {}
    for dict_code, dict_target in rows:
        msg_type_kv[dict_code] = dict_target
    sql = f"select msg_id,msg_type,msg_text,to_url,click_read,create_time from sys_msg where user_id=%s and state='0' and msg_type not in ({msg_types}) order by msg_id desc limit %s,%s"
    begin = (page - 1) * size
    cursor.execute(sql, (public.user_id, begin, size))
    rows = cursor.fetchall()
    detail = []
    for msg_id, msg_type, msg_text, to_url, click_read, create_time in rows:
        detail.append({
            'msg_id': msg_id,
            'msg_type': msg_type_kv.get(msg_type, msg_type),
            'content': msg_text,
            'color': 'primary',
            'click_read': click_read,
            'to_url': to_url,
            'time': create_time
        })
    sql = "select count(*) from sys_msg where user_id=%s and state='0'"
    cursor.execute(sql, public.user_id)
    row = cursor.fetchone()
    if not row or not row[0]:
        _count = 0
    else:
        _count = row[0]
    resp['detail'] = detail
    resp['count'] = _count
    return resp


# 消息已读
def msg_read(request, data, resp):
    msg_id = data.get('msg_id')
    if not msg_id:
        msg_id = data.get('form_var', {}).get('msg_id')
        if not msg_id:
            return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()
    sql = "update sys_msg set state='1' where msg_id=%s and user_id=%s and click_read='1'"
    row = cursor.execute(sql, (msg_id, public.user_id))
    if row:
        resp['success'] = True
    else:
        resp['success'] = False
    return resp


# 系统消息配置
def sys_msg_cfg(request, data, resp):
    form_var = data.get('form_var', {})
    msg_type = form_var.get('msg_type')
    open = request.GET.get('open')
    cursor = connection.cursor()
    if open == '1':
        state = '1'
    else:
        state = '0'
    try:
        sql = "insert into sys_msg_cfg(msg_type,state) value(%s,%s)"
        cursor.execute(sql, (msg_type, state))
    except IntegrityError:
        sql = "update sys_msg_cfg set state=%s where msg_type=%s"
        cursor.execute(sql, (state, msg_type))
    return resp


# 用户消息配置
def user_msg_cfg(request, data, resp):
    form_var = data.get('form_var', {})
    msg_type = form_var.get('msg_type')
    open = request.GET.get('open')
    cursor = connection.cursor()
    if open == '1':
        state = '1'
    else:
        state = '0'
    try:
        sql = "insert into sys_msg_user_cfg(msg_type,user_id,state) value(%s,%s,%s)"
        cursor.execute(sql, (msg_type, public.user_id, state))
    except IntegrityError:
        sql = "update sys_msg_user_cfg set state=%s where msg_type=%s and user_id=%s"
        cursor.execute(sql, (state, msg_type, public.user_id))
    return resp
