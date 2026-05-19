import sys
from django.shortcuts import render,redirect,HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime,time
from calendar import weekday,monthrange
from datetime import timedelta
import re
import psutil

#配置操作主流程
@transaction.atomic()
def Main_Proc( request ):
    public.respcode, public.respmsg = "999998", "交易开始处理!"
    log = public.logger
    sid = transaction.savepoint()
    func_name=public.tran_type+'(request)'
    if globals().get(public.tran_type):
        log.info('---[%s]-begin---' % (public.tran_type), extra={'ptlsh': public.req_seq})
        public.respinfo = eval(func_name)
        log.info('---[%s]-end----' % (public.tran_type), extra={'ptlsh': public.req_seq})
    else:
        public.respcode, public.respmsg = "100002", "trantype error!"
        public.respinfo = HttpResponse( public.setrespinfo() )
    if public.respcode=="000000":
        # 提交事务
        transaction.savepoint_commit(sid)
    # else:
    #     # 回滚事务
    #     transaction.savepoint_rollback(sid)
    return public.respinfo



def get_server_info( request ):
    log = public.logger
    body = public.req_body
    head = public.req_head
    cpu_percent = psutil.cpu_times_percent()
    cpu_info = [
        {
            "label": "核心数",
            "value": psutil.cpu_count()
        },
        {
            "label": "用户使用率",
            "value": str(cpu_percent.user) + "%"
        },
        {
            "label": "系统使用率",
            "value": str(cpu_percent.system) + "%"
        },
        {
            "label": "当前空闲率",
            "value": str(cpu_percent.idle) + "%"
        }
    ]
    memory=psutil.virtual_memory()
    memory_info=[
        {
            "label":"总内存",
            "value":'%sM'%(round(memory.total/1024/1024,1))
        },
        {
            "label": "已用内存",
            "value": '%sM'%(round(memory.used/1024/1024,1))
        },
        {
            "label": "剩余内存",
            "value": '%sM'%(round(memory.available/1024/1024,1))
        },
        {
            "label": "使用率",
            "value": str(memory.percent)+"%"
        }
    ]

    disk=psutil.disk_usage('/')
    disk_info=[
        {
            "label": "总空间",
            "value": '%sM' % (round(disk.total / 1024 / 1024, 1))
        },
        {
            "label": "已用空间",
            "value": '%sM' % (round(disk.used / 1024 / 1024, 1))
        },
        {
            "label": "剩余空间",
            "value": '%sM' % (round(disk.free / 1024 / 1024, 1))
        },
        {
            "label": "使用率",
            "value": str(disk.percent) + "%"
        }
    ]
    public.respcode, public.respmsg = "000000", "查询成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {
            "form_var":{
                "cpu_info":cpu_info,
                "memory_info":memory_info,
                "disk_info":disk_info
            }
        }
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo
