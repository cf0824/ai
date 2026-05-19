"""
运维相关接口
"""
import datetime
import random
import time
import hashlib
from app.models import SSiteInfo, SEqInfo, SEqPort, SysYwtyDict
from app.utils import MyLog
from django.core.paginator import Paginator
from django.db import transaction
from app.models import *
from app.models_super import *
from SmartChargeBD.settings import TOKEN_EXP_TIME
from app.utils import Error
from app.utils import token_handle
from app.utils.comm import api_handle
from app.utils import wx
from app.utils import handle
from django.db import connection
from django.db.models import Q
from app.utils.eq_api import tieta_handle2
from app.utils import devops_handle

log = MyLog.log


# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


def test(request, data, resp):
    print('test')
    return resp


# 登录
def login(request, data, resp):
    username = data.get('username')
    password = data.get('password')
    code = data.get('code')
    h = hashlib.md5()
    h.update(password.encode('utf-8'))
    md5_password = h.hexdigest()
    # 校验账户
    user = SDevopsUserInfo.objects.filter(user_name=username).first()
    if not user:
        return Error.USER_NOT_FOUND
    if user.user_password != md5_password:
        resp['success'] = False
        resp['tip'] = '账号或密码错误'
        return resp
    res = wx.get_devops_user_grant(code)
    if not res:
        return Error.NETWORK_ERROR
    print('res=', res)
    if user.state == '0':
        resp['success'] = False
        resp['tip'] = '账号已被禁用'
        return resp
    open_id = res['open_id']
    union_id = res['union_id']
    user.open_id = open_id
    user.union_id = union_id
    user.login_time = datetime.datetime.now()
    user.save()
    user_id = user.user_id
    # token刷新机制参考：https://www.jianshu.com/p/d5fb2bb94514
    token = token_handle.create_token({
        'token_type': 'grant',
        'user_id': user_id,
        'grant_api': ['devops']
    }, TOKEN_EXP_TIME)

    # refresh_token = token_handle.create_token({
    #     'token_type': 'refresh',
    #     'user_id': user_id
    # }, TOKEN_EXP_TIME * 2)
    # token过期时间戳
    exp_time = int(time.time()) + int(TOKEN_EXP_TIME)
    resp['token'] = str(token, encoding='utf-8')
    # resp['refresh_token'] = str(refresh_token, encoding='utf-8')
    resp['exp_time'] = exp_time
    resp['success'] = True
    resp['tip'] = '登录成功'
    return resp


# 获取任务列表
def get_task_list(request, data, resp):
    user_id = data.get('user_id')
    # info_task = SDevopsTaskInfo.objects.filter(state=0)
    task_name = data.get('task_name')
    # 查询有权限的站点
    site_ids = devops_handle.get_auth_site_ids(user_id)
    info_task = SDevopsTaskInfoSuper.objects.filter(state=0, site_id__in=site_ids)
    if task_name:
        info_task = info_task.filter(task_name__contains=task_name)
    info_task = info_task.order_by('-create_time')
    page = data.get('page', 1)
    paginator = Paginator(info_task, 10)
    page_data = paginator.page(page)
    list_task = []
    for item in page_data:
        list_task.append({
            "task_id": item.task_id,
            "task_name": item.task_name,
            "site_name": item.site_name,
            "site_address": item.site_address,
            'state': item.state,
            "eq_id": item.eq_id if item.eq_id else "--",
            "create_time": item.create_time
        })
        # site = SSiteInfo.objects.filter(site_id=i.site_id).first()
        # site_name = ''
        # if site:
        #     site_name = site.site_name
        # list_task.append(
        #     {
        #         'task_name': i.task_name,
        #         'create_time': i.create_time,
        #         'site_name': site_name,
        #         'task_id': i.id
        #     }
        # )
    # paginator = Paginator(list_task, 10)
    # list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = paginator.count
    resp['list_task'] = list_task
    return resp


# 获取任务详情信息
def get_task_info(request, data, resp):
    task_id = data.get('task_id')
    if not task_id:
        return Error.REQ_PARAMS_ERROR
    task = SDevopsTaskInfoSuper.objects.filter(task_id=task_id).first()
    # img_list = handle.img_str2url_list(task.repair_img)
    task_msg = {
        'task_name': task.task_name,
        'task_id': task_id,
        'state': task.state,
        'site_name': task.site_name,
        'task_desc': task.task_desc,
        'create_time': task.create_time,
        'feedback_tel': task.feedback_tel if task.feedback_tel else '-',
    }
    resp['task_msg'] = task_msg
    return resp


# 领取任务
def task_recv(request, data, resp):
    user_id = data.get("user_id")
    task_id = data.get('task_id')
    if not user_id or not id:
        return Error.REQ_PARAMS_ERROR

    sid = transaction.savepoint()
    task_msg = SDevopsTaskInfo.objects.filter(task_id=task_id, state='0').first()
    if not task_msg:
        resp['success'] = False
        resp['tip'] = '任务已被领取'
        return resp
    result = SDevopsTaskInfo.objects.filter(task_id=task_id, state='0').update(state='1')
    if not result:
        transaction.savepoint_rollback(sid)
        resp['success'] = False
        resp['tip'] = '任务已被领取'
        return resp
    recv = SDevopsTaskRecv.objects.create(
        task_id=task_id,
        user_id=user_id,
        create_time=datetime.datetime.now(),
        state='1'
    )
    transaction.savepoint_commit(sid)
    resp['success'] = True
    resp['tip'] = '领取成功'
    return resp


# 获取我的任务统计
def get_my_task_count(request, data, resp):
    user_id = data.get('user_id')
    mytasks = SDevopsTaskRecv.objects.filter(user_id=user_id)
    resp['processing'] = mytasks.filter(state='1').count()
    resp['finished'] = mytasks.filter(state='2').count()
    resp['report'] = mytasks.filter(state='9').count()
    return resp


# 我的任务
def task_my_list(request, data, resp):
    # 根据参数，查询未完成的和完成的
    user_id = data.get('user_id')
    state = data.get('state')
    page = data.get('page', 1)
    if not user_id or not state:
        return Error.REQ_PARAMS_ERROR

    # task_data = SDevopsTaskInfo.objects.filter(recv_user_id=recv_user_id, state=state)
    recv_data = SDevopsTaskRecv.objects.filter(user_id=user_id, state=state)
    panginator = Paginator(recv_data, 10)
    list_page_data = panginator.page(page)
    recv_list = []
    for recv in list_page_data:
        task = SDevopsTaskInfoSuper.objects.filter(task_id=recv.task_id).first()
        if not task:
            continue
        recv_list.append({
            'task_name': task.task_name,
            'task_id': task.task_id,
            'state': recv.state,
            'site_name': task.site_name,
            'task_desc': task.task_desc,
            'create_time': task.create_time,
            'feedback_tel': task.feedback_tel,
            'recv_id': recv.recv_id,
            'eq_id': task.eq_id if task.eq_id else "--"
        })
        # task_list.append(item.get_task_desc())
        # site = SSiteInfo.objects.filter(site_id=i.site_id).first()
        # site_name = ''
        # if site:
        #     site_name = site.site_name
        # task_list.append(
        #     {
        #         "task_id": i.id,
        #         "site_name": site_name,
        #         'state': i.state,
        #         "eq_id": i.eq_id if i.eq_id else "--"
        #     }
        # )
    resp['num_pages'] = panginator.num_pages
    resp['list_len'] = len(recv_list)
    resp['task_list'] = recv_list
    return resp


# 获取我的任务详情
def get_my_task_detail(request, data, resp):
    recv_id = data.get('recv_id')
    user_id = data.get('user_id')
    if not recv_id or not user_id:
        return Error.REQ_PARAMS_ERROR
    recv = SDevopsTaskRecv.objects.filter(recv_id=recv_id, user_id=user_id).first()
    if not recv:
        return Error.CONTENT_NOT_FOUND
    detail = {
        'fault_reason': recv.fault_reason,
        'repair_way': recv.repair_way,
        'repair_img': handle.img_str2url_list(recv.repair_img),
        'report_reason': recv.report_reason,
        'recv_time': recv.create_time,
        'finish_time': recv.finish_time,
        'state': recv.state,
    }
    task = SDevopsTaskInfoSuper.objects.filter(task_id=recv.task_id).first()
    if task:
        task_info = {
            'task_name': task.task_name,
            'task_id': task.task_id,
            'site_name': task.site_name,
            'task_desc': task.task_desc,
            'create_time': task.create_time,
            'feedback_tel': task.feedback_tel
        }
        detail.update(task_info)
    resp['detail'] = detail
    return resp


# 完成任务
def task_finished(request, data, resp):
    user_id = data.get('user_id')
    recv_id = data.get('recv_id')
    fault_reason = data.get('fault_reason')
    repair_way = data.get('repair_way')
    repair_img = data.get('repair_img')
    if not user_id or not recv_id:
        return Error.REQ_PARAMS_ERROR
    if not repair_img:
        resp['success'] = False
        resp['tip'] = '必须上传图片'
        return resp
    recv = SDevopsTaskRecv.objects.filter(recv_id=recv_id, user_id=user_id).first()
    if not recv_id:
        return Error.CONTENT_NOT_FOUND
    task = SDevopsTaskInfo.objects.filter(task_id=recv.task_id).first()
    if not task:
        return Error.CONTENT_NOT_FOUND
    with transaction.atomic():
        result = SDevopsTaskInfo.objects.filter(task_id=task.task_id, state='1') \
            .update(state='2', finish_time=datetime.datetime.now())
        if result == 0:
            resp['success'] = False
            resp['tip'] = '更新失败'
            return resp
        recv.fault_reason = fault_reason
        recv.repair_way = repair_way
        recv.repair_img = repair_img
        recv.finish_time = datetime.datetime.now()
        recv.state = '2'
        recv.save()
    resp['success'] = True
    resp['tip'] = '更新成功'
    return resp


# 上报任务
def report_task(request, data, resp):
    user_id = data.get('user_id')
    recv_id = data.get('recv_id')
    fault_reason = data.get('fault_reason')
    report_reason = data.get('report_reason')
    if not user_id or not recv_id:
        return Error.REQ_PARAMS_ERROR
    with transaction.atomic():
        row = SDevopsTaskRecv.objects.filter(recv_id=recv_id, user_id=user_id, state='1').update(
            fault_reason=fault_reason, report_reason=report_reason, finish_time=datetime.datetime.now(), state='9')
        if row:
            resp['success'] = True
            resp['tip'] = '更新成功'
        else:
            resp['success'] = False
            resp['tip'] = '更新失败'
        recv = SDevopsTaskRecv.objects.filter(recv_id=recv_id).first()
        SDevopsTaskReport.objects.create(
            task_id=recv.task_id,
            recv_id=recv.recv_id,
            user_id=recv.user_id,
            fault_reason=recv.fault_reason,
            report_reason=recv.report_reason,
            create_time=datetime.datetime.now(),
            state='0'
        )
    return resp


# 获取站点中设备信息，就先获取名字，然后从关联站点的名字中搜索出来设备id。
# 然后在另一个表里搜索，如果这个设备中有一个端口在使用，就判断是使用，否侧就是空闲。

# 获取电站列表
def get_site_list(request, data, resp):
    user_id = data.get('user_id')
    # 0表示查询全部，1表示启用，2表示停用，3表示离线，4表示故障
    status_type = data.get('status_type', 0)
    all_a = True
    offline = False
    fault = False
    # 查询有权限的站点
    site_ids = devops_handle.get_auth_site_ids(user_id)
    objs = SSiteInfo.objects.filter(site_id__in=site_ids)
    if status_type == 0:
        site_list = objs
    elif status_type == 1:
        site_list = objs.filter(state=status_type)
    elif status_type == 2:
        site_list = objs.filter(state=status_type)
    else:
        site_list = objs
        all_a = False
        if status_type == 3:
            offline = True
        if status_type == 4:
            fault = True

    site_msg_list = []

    for i in site_list:
        free_eq_count = SEqInfo.objects.filter(site_id=i.site_id, eq_state='0', conn_state='1').count()
        use_eq_count = SEqInfo.objects.filter(site_id=i.site_id, eq_state='1', conn_state='1').count()
        offline_eq_count = SEqInfo.objects.filter(site_id=i.site_id, conn_state='0').count()
        fault_eq_count = 0
        if i.state == '1':
            state = "启用"
        else:
            state = "停用"
        if all_a:
            site_msg_list.append(
                {
                    "site_name": i.site_name,
                    "site_id": i.site_id,
                    "site_state": state,
                    "free_eq_count": free_eq_count,
                    "use_eq_count": use_eq_count,
                    "offline_eq_count": offline_eq_count,
                    "fault_eq_count": fault_eq_count

                }
            )
        elif offline and offline_eq_count != 0:
            site_msg_list.append(
                {
                    "site_name": i.site_name,
                    "site_id": i.site_id,
                    "site_state": state,
                    "free_eq_count": free_eq_count,
                    "use_eq_count": use_eq_count,
                    "offline_eq_count": offline_eq_count,
                    "fault_eq_count": fault_eq_count

                }
            )
        elif fault and fault_eq_count != 0:
            site_msg_list.append(
                {
                    "site_name": i.site_name,
                    "site_id": i.site_id,
                    "site_state": state,
                    "free_eq_count": free_eq_count,
                    "use_eq_count": use_eq_count,
                    "offline_eq_count": offline_eq_count,
                    "fault_eq_count": fault_eq_count

                }
            )
    resp['site_msg_list'] = site_msg_list
    return resp


# 获取电站信息
def get_site_info(request, data, resp):
    site_id = data.get('site_id', None)
    if not site_id:
        return Error.REQ_PARAMS_ERROR

    # 启用统计
    enable_eq_count = 0
    # 停用统计
    deactivate_eq_count = 0
    # 空闲
    free_eq_count = 0
    # 使用
    use_eq_count = 0
    # 离线
    offline_eq_count = 0
    # 故障
    fault_eq_count = 0
    # 查询站点信息并获取状态
    site_data = SSiteInfo.objects.filter(site_id=site_id).first()
    site_state = site_data.state

    # 如果站点为2，表示停用，则应该所有的都是离线得。
    if site_state == '2':
        state = "停用"
        # 统计未开启的
        deactivate_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id).count()
        offline_eq_count += deactivate_eq_count
    #     否则，站点启用
    else:
        #     统计设备启用，停用等
        state = "启用"
        enable_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id, state='1').count()
        deactivate_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id, state='0').count()
        free_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id, state='1', eq_state='0',
                                                conn_state='1').count()
        use_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id, state='1', eq_state='1',
                                               conn_state='1').count()
        offline_eq_count += SEqInfo.objects.filter(site_id=site_data.site_id, state='1', conn_state='0').count()
        fault_eq_count += 0

    site_msg_list = {
        "site_name": site_data.site_name,
        "site_id": site_data.site_id,
        "site_state": state,
        "site_address": site_data.site_address,
        "site_position": site_data.site_position,
        "site_build": site_data.site_build,
        "enable_eq_count": enable_eq_count,
        "deactivate_eq_count": deactivate_eq_count,
        "free_eq_count": free_eq_count,
        "use_eq_count": use_eq_count,
        "offline_eq_count": offline_eq_count,
        "fault_eq_count": fault_eq_count,
        "parkingInstructions": "新能源汽车充电过程中不收取费用,充电完成后或未充电按2元每小时收取停车费用。",
    }

    resp['site_msg_list'] = site_msg_list
    return resp


# 获取电桩列表
def get_eq_list(request, data, resp):
    user_id = data.get('user_id')
    # 查询有权限的站点
    site_ids = devops_handle.get_auth_site_ids(user_id)
    objs = SEqInfo.objects.filter(site_id__in=site_ids)
    # 0全部 1启用 2停用 3空闲 4使用 5离线 6故障
    status_type = data.get('status_type', 0)
    page = data.get('page', 1)
    if status_type == 0:
        eq_list = objs
    elif status_type == 1:
        eq_list = objs.filter(state='1')
    elif status_type == 2:
        eq_list = objs.filter(state='0')
    elif status_type == 3:
        eq_list = objs.filter(state='1', eq_state='0', conn_state='1')
    elif status_type == 4:
        eq_list = objs.filter(state='1', eq_state='1', conn_state='1')
    elif status_type == 5:
        eq_list = objs.filter(state='1', conn_state='0')
    elif status_type == 6:
        eq_list = objs.filter(eq_state=3)
    else:
        eq_list = []

    eq_info_list = []
    for i in eq_list:
        if i.state == '1':
            state = "启用"
        else:
            state = "停用"
        if i.eq_state == '0' and i.conn_state == '1':
            eq_state = "空闲"
        elif i.eq_state == '1' and i.conn_state == '1':
            eq_state = "使用"
        elif i.conn_state == '0':
            eq_state = "离线"
        else:
            eq_state = "故障"
        eq_info_list.append(
            {
                "eq_id": i.eq_id,
                "state": state,
                "eq_state": eq_state
            }
        )

    panginator = Paginator(eq_info_list, 10)
    list_page_data = panginator.page(page).object_list
    resp['num_pages'] = panginator.num_pages
    resp['list_len'] = len(eq_info_list)
    resp["eq_info_list"] = list_page_data
    return resp


# 获取电桩详细信息
def get_eq_info(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    eq_data = SEqInfo.objects.filter(eq_id=eq_id).first()
    site_name = SSiteInfo.objects.filter(site_id=eq_data.site_id).first().site_name

    eq_elec_attr = SysYwtyDict.objects.filter(dict_name="EQ_ELEC_ATTR",
                                              dict_code=eq_data.eq_elec_attr).first().dict_target
    state = SysYwtyDict.objects.filter(dict_name="SITE_STATE", dict_code=eq_data.state).first().dict_target
    eq_state = SysYwtyDict.objects.filter(dict_name="EQ_EQ_STATE", dict_code=eq_data.eq_state).first().dict_target
    eq_info = {
        "eq_id": eq_id,
        "site_name": site_name,
        "eq_type": eq_elec_attr,
        "brand": "智云",
        "eq_model": "T-800",
        "rated_power": eq_data.rated_power,
        "state": state,
        "eq_state": eq_state,
        "remark": eq_data.remark,
        "soft_version": eq_data.soft_version,
        "agree_version": eq_data.agree_version,
        "communication_type": "4G",
        "communication_cp": "移动",
    }

    resp['eq_info'] = eq_info
    return resp


# 远程诊断
def site_judge(request, data, resp):
    page = data.get('page', 1)
    sname = data.get('sname', '')
    site = SSiteInfo.objects.filter(site_name__contains=sname)
    site_info = []
    for i in site:
        site_info.append(
            {
                "site_id": i.site_id,
                "site_name": i.site_name
            }
        )
    p = Paginator(site_info, 10)
    resp['num_pages'] = p.num_pages
    resp['list_len'] = len(site_info)
    resp['site_info'] = p.page(page).object_list
    return resp


# 诊断结果

# 个人资料
def get_devops_user_info(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    user_data = SDevopsUserInfo.objects.filter(user_id=user_id).first()
    user_info = {
        "user_name": user_data.user_name,
        "user_comp": user_data.user_comp,
        "user_post": user_data.user_post
    }

    resp["user_info"] = user_info
    return resp


# 获取设备功率
def get_eq_power(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    cursor = connection.cursor()
    # 取近24小时
    now_hour = datetime.datetime.now().hour
    begin_hour = now_hour + 1
    labels = [f"{str(item).rjust(2, '0')}" for item in range(begin_hour, 24)]
    labels += [f"{str(item).rjust(2, '0')}" for item in range(0, now_hour + 1)]
    v_data = [0 for _ in range(24)]
    a_data = [0 for _ in range(24)]
    p_data = [0 for _ in range(24)]
    sql = "select date_format(create_time,'%%Y-%%m-%%d %%H') dt,round(avg(attr_value)/100,2) from s_eq_attr_data where eq_id=%s and attr_key='v100' and create_time>=date_sub(now(), interval 24 hour) group by date_format(create_time,'%%Y-%%m-%%d %%H') order by dt desc limit 24"
    cursor.execute(sql, eq_id)
    rows = cursor.fetchall()
    for i, (date_str, v) in enumerate(rows):
        hour_str = f"{date_str.split(' ')[-1]}"
        index = labels.index(hour_str)
        v_data[index] = v
    sql = "select date_format(create_time,'%%Y-%%m-%%d %%H') dt,round(avg(attr_value)/100,2) from s_eq_attr_data where eq_id=%s and attr_key='a100' and create_time>=date_sub(now(), interval 24 hour) group by date_format(create_time,'%%Y-%%m-%%d %%H') order by dt desc limit 24"
    cursor.execute(sql, eq_id)
    rows = cursor.fetchall()
    for i, (date_str, a) in enumerate(rows):
        hour_str = f"{date_str.split(' ')[-1]}"
        index = labels.index(hour_str)
        a_data[index] = a
    for i, v in enumerate(v_data):
        p_data[i] = round((v * a_data[i]), 2)
    detail = {
        "categories": labels,
        "series": [{
            "name": "电压",
            "data": v_data
        }, {
            "name": "电流",
            "data": a_data
        }, {
            "name": "功率",
            "data": p_data
        }]

    }
    resp['chartsData'] = detail
    return resp


# 获取上报原因键值对
def get_report_reason_kv(request, data, resp):
    detail = []
    objs = SysYwtyDict.objects.filter(dict_name='REPORT_REASON')
    for obj in objs:
        detail.append({
            "key": obj.dict_code,
            "name": obj.dict_target,
            "checked": False,
            "disabled": False
        })
    resp['detail'] = detail
    return resp


# 远程诊断查询
def remote_check_search(request, data, resp):
    user_id = data.get('user_id')
    # 查询有权限的站点
    site_ids = devops_handle.get_auth_site_ids(user_id)
    site_objs = SSiteInfo.objects.filter(site_id__in=site_ids)
    eq_objs = SEqInfo.objects.filter(site_id__in=site_ids)
    search_key = data.get('search_key')
    if not search_key:
        return Error.REQ_PARAMS_ERROR
    if str(search_key).isdigit():
        sites = site_objs.filter(site_id=search_key)
    else:
        sites = site_objs.filter(site_name__contains=search_key)
    if str(search_key).isdigit():
        eqs = eq_objs.filter(eq_id=search_key)
    else:
        eqs = []
    detail = []
    for site in sites:
        detail.append({
            'type': 'site',
            'site_id': site.site_id,
            'site_name': site.site_name
        })
    for eq in eqs:
        st = SSiteInfo.objects.filter(site_id=eq.site_id).first()
        site_name = st.site_name if st.site_name else ''
        detail.append({
            'type': 'eq',
            'eq_id': eq.eq_id,
            'site_id': eq.site_id,
            'site_name': site_name
        })
    resp['detail'] = detail
    return resp


# 修改密码
def update_password(request, data, resp):
    user_id = data.get('user_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not user_id or not old_password or not new_password:
        return Error.REQ_PARAMS_ERROR
    h = hashlib.md5()
    h.update(old_password.encode('utf-8'))
    old_md5 = h.hexdigest()
    h2 = hashlib.md5()
    h2.update(new_password.encode('utf-8'))
    new_md5 = h2.hexdigest()
    user = SDevopsUserInfo.objects.filter(user_id=user_id).first()
    if not user:
        return Error.USER_NOT_FOUND
    if user.user_password != old_md5:
        resp['success'] = False
        resp['tip'] = '原密码错误'
        return resp
    user.user_password = new_md5
    user.save()
    resp['success'] = True
    resp['tip'] = '修改成功'
    return resp


# 重启设备
def restart_eq(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    eq = SEqInfo.objects.filter(eq_id=eq_id).first()
    if not eq:
        return Error.CONTENT_NOT_FOUND
    th = tieta_handle2.TietaHandle(SCmdDetail)
    res = th.eq_restart(eq.eq_code)
    if not res:
        resp['success'] = False
        resp['tip'] = '重启失败'
        return resp
    resp['success'] = True
    resp['tip'] = '重启成功'
    return resp


# 获取设备计价规则
def get_eq_price_rule(request, data, resp):
    eq_id = data.get('eq_id')
    if not eq_id:
        return Error.REQ_PARAMS_ERROR
    eq = SEqInfo.objects.filter(eq_id=eq_id).first()
    if not eq:
        return Error.CONTENT_NOT_FOUND
    if not eq.mode_id:
        mode_id = 1
    else:
        mode_id = eq.mode_id
    objs = SPriceModeDetail.objects.filter(mode_id=mode_id)
    detail = []
    for item in objs:
        detail.append(
            f"{item.begin_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}   {str(item.price).rstrip('0')}元/度")
    resp['detail'] = detail
    return resp


# 获取电站计价规则
def get_site_price_rule(request, data, resp):
    site_id = data.get('site_id')
    if not site_id:
        return Error.REQ_PARAMS_ERROR
    site = SSiteInfo.objects.filter(site_id=site_id).first()
    if not site:
        return Error.CONTENT_NOT_FOUND
    if not site.mode_id:
        mode_id = 1
    else:
        mode_id = site.mode_id
    objs = SPriceModeDetail.objects.filter(mode_id=mode_id)
    detail = []
    for item in objs:
        detail.append(
            f"{item.begin_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}   {str(item.price).rstrip('0')}元/度")
    resp['detail'] = detail
    return resp
