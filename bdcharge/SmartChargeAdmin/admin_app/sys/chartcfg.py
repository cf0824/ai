from django.db import connection
import json
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
import base64
import requests
from admin_cfg.settings import ADMIN_WEBSITE

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


def get_chart_list(request, data, resp):
    cursor = connection.cursor()  # 创建游标
    sql = "select cid,cname from sys_chart_cfg"
    cursor.execute(sql)
    rows = cursor.fetchall()
    detail = []
    for cid,cname in rows:
        detail.append({
            'cid':cid,
            'cname':cname,
            'url':f'{ADMIN_WEBSITE}/static/chartimg/'+str(cid)+'.png'
        })
    resp['detail'] = detail
    return resp


def add_chart(request, data, resp):
    cname=data.get('chart_name')
    if not cname:
        return ERROR['REQ_PARAMS_ERROR']
    cfg=data.get('cfg',{})
    cfg_str = json.dumps(cfg)
    cursor = connection.cursor()  # 创建游标
    sql = "insert into sys_chart_cfg(cname,cfg,create_time,update_time) value(%s,%s,now(),now())"
    row = cursor.execute(sql,(cname,cfg_str))
    if row==0:
        return ERROR['OPERA_FAIL']
    cid = cursor.lastrowid
    resp['cid'] = cid
    return resp


def update_chart_info(request, data, resp):
    cid = data.get('cid')
    cname = data.get('cname')
    if not all([cid,cname]):
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()  # 创建游标
    sql = "update sys_chart_cfg set cname=%s,update_time=now() where cid=%s"
    row = cursor.execute(sql,(cname,cid))
    if row == 0:
        resp['tip'] = '操作失败'
        resp['success'] = False
        return resp
    resp['tip'] = '修改成功'
    resp['success'] = True
    return resp



def save_cfg(request, data, resp):
    cid=data.get('cid')
    cfg=data.get('cfg',{})
    img = data.get('img')
    if not cid:
        return ERROR['REQ_PARAMS_ERROR']
    # 保存截图
    if img:
        img = img[str(img).find(',')+1:]
        with open(public.localhome+'static/chartimg/'+str(cid)+'.png','wb') as f:
            f.write(base64.b64decode(img))
    cursor = connection.cursor()  # 创建游标
    cfg_str = json.dumps(cfg)
    sql = "update sys_chart_cfg set cfg=%s,update_time=%s where cid=%s"
    row = cursor.execute(sql,(cfg_str,datetime.datetime.now(),cid))
    if row==0:
        return ERROR['OPERA_FAIL']
    return resp


def get_chart_cfg(request, data, resp):
    log = public.logger
    cid = data.get('cid')
    cursor = connection.cursor()  # 创建游标
    if not cid:
        mid = public.menu_id
        if not mid:
            return ERROR['REQ_PARAMS_ERROR']
        sql = "select app_id from sys_menu where menu_id=%s"
        cursor.execute(sql,mid)
        row = cursor.fetchone()
        cid, = row
        if not cid:
            return ERROR['REQ_PARAMS_ERROR']
    log.info('cid=%s'%cid)
    sql = "select cfg from sys_chart_cfg where cid=%s"
    cursor.execute(sql,cid)
    row = cursor.fetchone()
    cfg, = row
    if not cfg:
        cfg = {}
    else:
        cfg = json.loads(cfg)
    resp['cfg'] = cfg
    return resp


def delete_chart(request, data, resp):
    cid = data.get('cid')
    if not cid:
        return ERROR['REQ_PARAMS_ERROR']
    cursor = connection.cursor()  # 创建游标
    sql = "delete from sys_chart_cfg where cid=%s"
    row = cursor.execute(sql, cid)
    if row==0:
        resp['tip'] = '操作失败'
        resp['success'] = False
        return resp
    resp['tip'] = '删除成功'
    resp['success'] = True
    return resp


def get_map_data(request, data, resp):
    log = public.logger
    # res = requests.get('https://geo.datav.aliyun.com/areas/bound/410300_full.json')
    res = requests.get('https://geo.datav.aliyun.com/areas_v2/bound/410000_full.json')
    # log.info('res=%s'%res.json())
    resp['data'] = res.json()
    return resp


def get_chart_media(request, data, resp):
    cursor = connection.cursor()  # 创建游标
    sql = "select media_name from sys_chart_media order by create_time desc"
    cursor.execute(sql)
    rows = cursor.fetchall()
    detail = []
    media_pre = f'{ADMIN_WEBSITE}/static/chart_media/'
    for media_name, in rows:
        detail.append(media_pre + media_name)
    resp['detail'] = detail
    return resp