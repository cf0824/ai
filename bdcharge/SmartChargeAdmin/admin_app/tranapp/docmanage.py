import sys
from django.shortcuts import render,redirect,HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.sys import public_db

###########################################################################################################
#文件档案管理
#add by litz, 2020.05.15
#
###########################################################################################################

#增删改查配置数据操作主流程
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


def docment_manage_fileauth_cfg(request):
    log = public.logger
    form_var= public.req_body['form_var']

    try:
        file_type = form_var.get('file_type')
        if not file_type:
            public.respcode, public.respmsg = "310310", "请先选择文件类型!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标
        sql = "select 1 from yw_workflow_document_manage_cfg where file_type=%s"
        cur.execute(sql, file_type)
        row = cur.fetchone()
        if row: #有数据， 更新
            sql="update yw_workflow_document_manage_cfg set read_cfgtype=%s,read_cfginfo=%s, write_cfgtype=%s,write_cfginfo=%s  " \
                "where file_type=%s"
        else: #无数据，插入
            sql = "insert into yw_workflow_document_manage_cfg(read_cfgtype,read_cfginfo,write_cfgtype,write_cfginfo, file_type) " \
                  "values(%s, %s, %s, %s, %s)"
        cur.execute(sql, (form_var.get('read_cfgtype'), str(form_var.get('read_cfginfo')), form_var.get('write_cfgtype'),
                          str(form_var.get('write_cfginfo')), file_type) )
    except Exception as ex:
        log.error("更新数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        public.respcode, public.respmsg = "100010", "更新数据失败!" + str(ex)
        public.respinfo = HttpResponse(public.setrespinfo())

    else:
        public.respcode, public.respmsg = "000000", "交易成功!"
        json_data = {
            "HEAD": public.resphead_setvalue(),
            "BODY": {
                "form_var": form_var
            }
        }
        s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
        public.respinfo = HttpResponse(s)
    finally:
        cur.close()  # 关闭游标

    return public.respinfo

def get_doccfg_info(request):
    log = public.logger
    form_data= public.req_body['form_data']

    try:
        file_type = form_data.get('file_type')
        if not file_type:
            public.respcode, public.respmsg = "310310", "请先选择文件类型!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标
        sql = "select read_cfgtype,read_cfginfo,write_cfgtype,write_cfginfo from yw_workflow_document_manage_cfg where file_type=%s"
        cur.execute(sql, file_type)
        row = cur.fetchone()
        if row: #有数据
            form_data['read_cfgtype'] = row[0]
            if row[1]:
                form_data['read_cfginfo'] = eval(row[1])
            else:
                form_data['read_cfginfo'] = eval([])

            form_data['write_cfgtype'] = row[2]
            if row[3]:
                form_data['write_cfginfo'] = eval(row[3])
            else:
                form_data['write_cfginfo'] = eval([])

        #获取下拉配置属性
        sql="select dict_code, dict_target from sys_ywty_dict where DICT_NAME='DOCMENT_MANAGE_DOCTYPE'"
        cur.execute(sql)
        rows = cur.fetchall()
        options=[]
        for item in rows:
            options.append({"key":item[0], "value":item[1]})
        form_data['filetype_options'] = options

        sql = "select dict_code,CONCAT(dict_code,'-',dict_target) from sys_ywty_dict where dict_name='DOCMENT_MANAGE_READ_CFGTYPE'"
        cur.execute(sql)
        rows = cur.fetchall()
        options = []
        for item in rows:
            options.append({"key": item[0], "value": item[1]})
        form_data['read_cfgtype_options'] = options
        form_data['write_cfgtype_options'] = options

        if form_data.get('read_cfgtype') == 'byorg':
            sql = "select org_id, org_name from sys_org where org_state='1' "
        else:
            sql = "SELECT user_id, user_name FROM sys_user  WHERE state='1'"
        cur.execute(sql)
        rows=cur.fetchall()
        transfer= []
        for item in rows:
            transfer.append( { "key": item[0],  "label": str(item[0])+'-'+item[1], "disabled": False} )
        form_data['read_cfginfo_options'] = transfer

        if form_data.get('write_cfgtype') == 'byorg':
            sql = "select org_id, org_name from sys_org where org_state='1' "
        else:
            sql = "SELECT user_id, user_name FROM sys_user  WHERE state='1'"
        cur.execute(sql)
        rows=cur.fetchall()
        transfer= []
        for item in rows:
            transfer.append( { "key": item[0],  "label": str(item[0])+'-'+item[1], "disabled": False} )
        form_data['write_cfginfo_options'] = transfer

    except Exception as ex:
        log.error("查询数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        public.respcode, public.respmsg = "100010", "查询数据失败!" + str(ex)
        public.respinfo = HttpResponse(public.setrespinfo())

    else:
        public.respcode, public.respmsg = "000000", "交易成功!"
        json_data = {
            "HEAD": public.resphead_setvalue(),
            "BODY": {
                "form_var": form_data
            }
        }
        s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
        public.respinfo = HttpResponse(s)
    finally:
        cur.close()  # 关闭游标

    return public.respinfo

