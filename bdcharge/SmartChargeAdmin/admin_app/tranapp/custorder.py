import sys
from django.shortcuts import render,redirect,HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.sys import public_db

###########################################################################################################
#客户订单管理模块
#add by litz, 2020.06.15
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


#备货单查询
def custorder_stockup_show(request):
    log = public.logger
    form_data= public.req_body['form_data']
    try:
        total_num = 5 #显示5条明细
        this_num = 0 #当前记录数
        form_var = {}
        ht_info = []
        cp_info = []
        jq_info = []

        cur = connection.cursor()  # 创建游标

        if form_data.get('id'):
            sql = "select tran_date,bill_no,tc_no,cust_name,salesperson,otherinfo,state from yw_bill_stockup_head where id=%s "
            cur.execute(sql, form_data.get('id'))
            row =  cur.fetchone()
            if not row:
                public.respcode, public.respmsg = "320331", "查询无数据!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo

            # #重新赋值一些数据
            form_var['tran_date'] =  row[0]
            form_var['bill_no'] = row[1]
            form_var['tc_no'] = row[2]
            form_var['cust_name'] = row[3]
            form_var['salesperson'] =  row[4]
            form_var['otherinfo'] = row[5]
            form_var['state'] =  row[6]
            form_var['id'] = form_data.get('id')

            #删除后重新插入明细
            sql = "select prd_name, prd_num, prd_hardversion, prd_pcbversion, prd_shellinfo, prd_macinfo " \
                  "from yw_bill_stockup_body where head_id=%s"
            cur.execute(sql, form_data.get('id'))
            rows = cur.fetchall()

            for item in rows:
                this_num=this_num+1
                # 获取表身明细
                ht_info_dict = {}
                cp_info_dict = {}
                jq_info_dict = {}

                ht_info_dict['prd_name'] = item[0]
                ht_info_dict['prd_num'] = item[1]
                ht_info_dict['prd_hardversion'] = item[2]
                ht_info_dict['prd_pcbversion'] = item[3]
                ht_info_dict['prd_shellinfo'] = item[4]
                ht_info_dict['prd_macinfo'] = item[5]

                cp_info_dict['prd_name'] = item[0]
                jq_info_dict['prd_name'] = item[0]


                ht_info.append(ht_info_dict)
                cp_info.append(cp_info_dict)
                jq_info.append(jq_info_dict)

        if this_num < total_num:
            for i in range(1, total_num-this_num):
                ht_info_dict = {}
                ht_info_dict['prd_hardversion'] =  ''
                ht_info_dict['prd_macinfo'] =  ''
                ht_info_dict['prd_name'] =  ''
                ht_info_dict['prd_num'] =  ''
                ht_info_dict['prd_pcbversion'] =  ''
                ht_info_dict['prd_shellinfo'] =  ''
                ht_info.append(ht_info_dict)
                cp_info_dict={}
                cp_info_dict["prd_name"] =  ''
                cp_info_dict["prd_no"] =  ''
                cp_info_dict["prd_blueprint_ver"] =  ''
                cp_info_dict["prd_pcb_ver"] =  ''
                cp_info_dict["prd_key_components"] =  ''
                cp_info_dict["prd_otherinfo"] =  ''
                cp_info.append(cp_info_dict)
                jq_info_dict={}
                jq_info_dict["prd_name"] =  ''
                jq_info_dict["delivery_plan_no"] =  ''
                jq_info_dict["delivery_comp_coll_time"] =  ''
                jq_info_dict["delivery_pcba_return_time"] =  ''
                jq_info_dict["delivery_cust_time"] =  ''
                jq_info_dict["prd_otherinfo"] =  ''
                jq_info.append(jq_info_dict)
        form_var['ht_info'] = ht_info
        form_var['cp_info'] = cp_info
        form_var['jq_info'] = jq_info
        cur.close()  # 关闭游标
    except Exception as ex:
        log.error("更新数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()  # 关闭游标
        public.respcode, public.respmsg = "100010", "更新数据失败!" + str(ex)
        public.respinfo = HttpResponse(public.setrespinfo())

    else:
        public.respcode, public.respmsg = "000000", "交易成功!"
        json_data = {
            "HEAD": public.resphead_setvalue(),
            "BODY": {
                "form_id" : form_data.get("form_id"),
                "form_var": form_var
            }
        }
        s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
        public.respinfo = HttpResponse(s)

    return public.respinfo

#备货单信息新增或修改保存
def custorder_stockup_save(request):
    log = public.logger
    form_var= public.req_body['form_var']
    try:
        id = form_var.get('id')
        ht_info = form_var.get('ht_info')
        if not ht_info or len(ht_info) == 0:
            public.respcode, public.respmsg = "320330", "明细必输!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo


        cur = connection.cursor()  # 创建游标
        # #重新赋值一些数据
        form_var['bill_no'] = public_db.Get_SeqNo('STOCKUP_SERIAL') #生成备货单号
        form_var['state'] = '0' #合同信息新录入
        if not id: #新增数据
            sql = "insert into yw_bill_stockup_head(tran_date,bill_no,tc_no,cust_name,salesperson,state)  " \
                  "values(%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (datetime.datetime.now(), form_var.get('bill_no'), form_var.get('tc_no'), form_var.get('cust_name'),
                        form_var.get('salesperson'), form_var.get('state') ) )
            form_var['id'] = cur.lastrowid
            id = form_var.get('id')
        else: #更新记录
            sql = "update yw_bill_stockup_head set tran_date=%s,bill_no=%s,tc_no=%s,cust_name=%s,salesperson=%s,state=%s " \
                  "where id=%s"
            cur.execute(sql, (datetime.datetime.now(), form_var.get('bill_no'), form_var.get('tc_no'), form_var.get('cust_name'),
                        form_var.get('salesperson'), form_var.get('state'),  id) )

        #删除后重新插入明细
        sql = "delete from yw_bill_stockup_body where head_id=%s"
        cur.execute(sql, form_var['id'])

        #插入新的表身明细
        ht_info = form_var.get('ht_info')
        cp_info = form_var.get('cp_info')
        jq_info = form_var.get('jq_info')
        i = 0
        for ht_item in ht_info:
            cp_item = cp_info[i]
            jq_item = jq_info[i]
            i = i + 1
            print('ht_item=', ht_item)
            print('cp_item=', cp_item)
            print('jq_item=', jq_item)
            if not ht_item.get('prd_num'):
                continue

            sql = "insert into yw_bill_stockup_body(head_id, tran_date, prd_name, prd_num ) values(%s, %s, %s, %s)"
            cur.execute(sql, (form_var.get('id'), datetime.datetime.now(), ht_item.get('prd_name'),ht_item.get('prd_num') ))
        cur.close()  # 关闭游标
    except Exception as ex:
        log.error("更新数据失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()  # 关闭游标
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
    return public.respinfo

