from django.db import connection
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR

#增删改查配置数据操作主流程
def Main_Proc(request):
    gb=globals()
    return handle.func_handle(request,gb)


# 测试
def test(request,data,resp):
    log = public.logger
    log.info('test begin')
    resp['detail']={'a':1,'b':2}
    return resp


# 保存流程配置
def save_wf_cfg(request,data,resp):
    form_id = data.get('form_id')
    wf_cfg=data.get('wf_cfg')
    if not all([wf_cfg,form_id]):
        return ERROR['REQ_PARAMS_ERROR']
    wf_cfg=json.dumps(wf_cfg)
    cursor = connection.cursor()
    # resp['respcode']='501001'
    # resp['respmsg']='配置有误'
    # return resp
    # 修改
    sql = "update sys_wf_cfg set wf_cfg=%s,update_time=%s where form_id=%s"
    row = cursor.execute(sql, (wf_cfg, datetime.datetime.now(), form_id))
    if row==0:
        # 新增
        sql = "insert into sys_wf_cfg(form_id,wf_cfg,create_time,update_time) value(%s,%s,%s,%s)"
        row = cursor.execute(sql,(form_id,wf_cfg,datetime.datetime.now(),datetime.datetime.now()))
    if row==0:
        return ERROR['OPERA_FAIL']
    return resp


# 获取流程配置
def get_wf_cfg(request,data,resp):
    form_id=data.get('form_id')
    if not form_id:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()
    sql = "select wf_cfg from sys_wf_cfg where form_id=%s"
    cursor.execute(sql,form_id)
    row = cursor.fetchone()
    wf_cfg=None
    if row:
        wf_cfg=row[0]
        wf_cfg=json.loads(wf_cfg)
    resp['wf_cfg']=wf_cfg
    return resp


