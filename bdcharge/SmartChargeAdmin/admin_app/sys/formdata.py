from admin_app.tranapp.formbutton import *
from admin_app.tranapp.transfer import *
from admin_app.tranapp.wamreport import *
from admin_app.tranapp.apply import *

###########################################################################################################
#表单自定义按钮，发起交易
#add by litz, 2020.04.10
#
###########################################################################################################

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
    # 特殊系统级交易,因为是配置出来的
    elif public.tran_type in ['aboverole_cfg_select', 'role_cfg_select', 'role_cfg_create', 'role_fieldcfg_select',
                              'role_fieldcfg_create']:
        from admin_app.sys import userauth
        func_name = 'userauth.%s(request)' % public.tran_type
        log.info('---[%s]-begin---' % (func_name), extra={'ptlsh': public.req_seq})
        public.respinfo = eval(func_name)
        log.info('---[%s]-end----' % (func_name), extra={'ptlsh': public.req_seq})
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

#通用交易，执行配置的sql语句
def FORMTRAN_EXESQL(request ):
    log = public.logger
    body=public.req_body
    form_id = body.get('form_id')
    form_var = body.get('form_var')
    button_id = body.get('button_id')
    result_rowcount = 0 #最终影响行数
    if not button_id:
        log.info("按钮ID不存在!", extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        public.respcode, public.respmsg = "200011", "按钮ID不存在!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    try:
        cur = connection.cursor()  # 创建游标
        sql = "select form_sql from sys_form_cfg_info where form_id=%s"
        cur.execute(sql, form_id)
        row = cur.fetchone()
        form_sql=row[0]
        if form_sql:
            form_sql=json.loads(form_sql)
        sqllist=form_sql.get(button_id)
        for sql_item in sqllist.split(';'):
            log.info('初期SQL:'+str(sql_item), extra={'ptlsh': public.req_seq})
            if not sql_item:
                continue
            sql = public.SqlKeywordConver( sql_item, form_var )
            log.info('最终SQL:' + str(sql), extra={'ptlsh': public.req_seq})
            cur.execute( sql )
            if cur.rowcount > 0:
                result_rowcount = result_rowcount + cur.rowcount
        cur.close()
    except Exception as ex:
        log.error("SQL执行失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        if 'Duplicate' in str(ex) and 'PRIMARY' in str(ex):
            public.respcode, public.respmsg = "100200", "SQL执行失败!" + str(ex)
        else:
            public.respcode, public.respmsg = "100200", "SQL执行失败!" + str(ex)
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    if result_rowcount > 0:
        public.respcode, public.respmsg = "000000", "交易成功!"
    else:
        public.respcode, public.respmsg = "200012", "无数据操作!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {}
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo

#通用删除交易，执行配置的sql语句
def TableDelete_EXESQL(request ):
    log = public.logger
    body=public.req_body
    # delete_append_sql = body.get('delete_append_sql') #删除的sql语句
    selected = body.get('selected') #删除的记录
    form_id =  body.get('form_id') #表单ID
    table_id =  body.get('table_id') #表格ID

    result_rowcount = 0 #最终影响行数
    if not selected:
        public.respcode, public.respmsg = "200311", "没有上送需要删除的记录!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo
    if not form_id:
        public.respcode, public.respmsg = "200311", "表单ID必须上送!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    try:
        cur = connection.cursor()  # 创建游标

        sql = "select form_cfg from sys_form_cfg_info where form_id = %s"
        log.info(sql % form_id, extra={'ptlsh': public.req_seq})
        cur.execute(sql, form_id)
        row = cur.fetchone()
        if not row:
            cur.close()  # 关闭游标
            public.respcode, public.respmsg = "100212", "表单配置不存在!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        form_cfg = json.loads(row[0])

        # 递归获取表单中指定的表格删除数据的sql, 多个删除操作用分号分隔开
        def GetDelSQL(form_cfg, table_id):
            deletesql = ""
            for comp_item in form_cfg:
                if comp_item.get('children'):
                    deletesql = GetDelSQL( comp_item['children'], table_id )
                    if not deletesql:
                        continue
                    else:
                        return deletesql
                elif comp_item['type'] == 'null':
                    continue
                elif comp_item['id'] == table_id:
                    deletesql = comp_item['attrs'].get('delete_append_sql')
                    return deletesql
            return deletesql  # 没找到

        delete_append_sql = GetDelSQL(form_cfg, table_id)
        for data_item in selected:
            for sql_item in delete_append_sql.split(';'):
                log.info('初期SQL:'+str(sql_item), extra={'ptlsh': public.req_seq})
                if not sql_item:
                    continue
                sql = public.SqlKeywordConver( sql_item, data_item )

                for sqlitm in data_item:
                    old = "$[" + sqlitm + "]"
                    if sqlitm in data_item.keys():
                        new = "'" + str(data_item.get(sqlitm)) + "'"
                    else:
                        new = "''"
                    sql = sql.replace(old, new)
                log.info('real sql=' + str(sql), extra={'ptlsh': public.req_seq})

                log.info('最终SQL:' + str(sql), extra={'ptlsh': public.req_seq})
                cur.execute( sql )
                if cur.rowcount > 0:
                    result_rowcount = result_rowcount + cur.rowcount
        cur.close()
        log.info('影响记录行数:' + str(result_rowcount), extra={'ptlsh': public.req_seq})

    except Exception as ex:
        log.error("SQL执行失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        if 'Duplicate' in str(ex) and 'PRIMARY' in str(ex):
            public.respcode, public.respmsg = "100200", "SQL执行失败!" + str(ex)
        else:
            public.respcode, public.respmsg = "100200", "SQL执行失败!" + str(ex)
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    if result_rowcount > 0:
        public.respcode, public.respmsg = "000000", "交易成功!"
    else:
        public.respcode, public.respmsg = "200012", "无数据操作!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {}
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo



