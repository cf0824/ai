import sys
from django.shortcuts import render,redirect,HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
from admin_app.sys import public_db
import os

###########################################################################################################
#各种申请的特殊流程
#add by litz, 2020.06.03
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


#用车申请，根据车辆类型获取车牌基本信息
def get_car_info( request ):
    log = public.logger
    body=public.req_body
    formid=body.get("form_id")
    form_var = body.get("form_var")
    if not formid:
        public.respcode, public.respmsg = "110221", "表单ID不可为空!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    if not form_var:
        public.respcode, public.respmsg = "110222", "配置信息不可为空!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    try:
        cur = connection.cursor()  # 创建游标
        sql = "select car_number,car_image,user_id,car_address from yw_workflow_apply_car_info where car_type=%s"
        cur.execute(sql, (body.get('select_key') )  )
        row=cur.fetchone()
        if row:
            body['form_var']['car_number'] =  row[0]
            if row[1]:
                body['form_var']['car_image'] = eval(row[1])
            else:
                body['form_var']['car_image'] = []
            body['form_var']['car_curator'] = public_db.get_username( row[2] )
            body['form_var']['start_address'] = row[3]
        else:
            body['form_var']['car_number'] = ''
            body['form_var']['car_image'] = []
            body['form_var']['car_curator'] = ''
            body['form_var']['start_address'] = ''
        cur.close()  # 关闭游标

    except Exception as ex:
        log.error("交易失败!" + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()  # 关闭游标
        public.respinfo = HttpResponse( public.setrespinfo() )
        return public.respinfo

    public.respcode, public.respmsg = "000000", "交易成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": body,
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo

#用车申请-提交请求
def use_car_apply_commit( request ):
    log = public.logger
    body = public.req_body
    form_var = body.get('form_var')

    try:
        id = form_var.get('id')

        if not form_var.get('department'):
            public.respcode, public.respmsg = "333102", "申请部门不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('start_address'):
            public.respcode, public.respmsg = "333102", "取车地点不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('end_address'):
            public.respcode, public.respmsg = "333102", "还车地点不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('start_date'):
            public.respcode, public.respmsg = "333102", "预计取车时间不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('end_date'):
            public.respcode, public.respmsg = "333102", "预计还车时间不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('car_type'):
            public.respcode, public.respmsg = "333102", "车辆类型不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('car_number'):
            public.respcode, public.respmsg = "333102", "车牌号码不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('use_person'):
            public.respcode, public.respmsg = "333102", "使用人不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('car_mileage'):
            public.respcode, public.respmsg = "333102", "预计公里数不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('reason'):
            public.respcode, public.respmsg = "333102", "申请原因不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标

        if id: #更新数据
            sql = "select status, user_id from yw_workflow_apply_car where id=%s"
            cur.execute(sql, id)
            row = cur.fetchone()
            if not row:
                public.respcode, public.respmsg = "333001", "原数据不存在!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo
            if row[0] not in  ['0','2']:
                public.respcode, public.respmsg = "333002", "审批状态非初始,不可修改!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo
            if row[1] != public.user_id:
                public.respcode, public.respmsg = "333004", "只可修改自己的单据!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo

            sql="update yw_workflow_apply_car set department=%s,start_address=%s,end_address=%s, start_date=%s, end_date=%s, " \
                "car_type=%s, use_person=%s, car_person=%s,car_number=%s,car_mileage=%s,reason=%s,remark=%s, status='0' where id=%s "
            cur.execute(sql, (form_var.get('department'), form_var.get('start_address'), form_var.get('end_address'),
                              form_var.get('start_date'), form_var.get('end_date'), form_var.get('car_type'),
                              form_var.get('use_person'), form_var.get('car_person'), form_var.get('car_number'),
                              form_var.get('car_mileage'), form_var.get('reason'), form_var.get('remark'), id) )

        else: #插入数据

            order_number = public_db.Get_SeqNo( 'USE_CAR' )
            body['form_var']['order_number'] = order_number

            sql = "insert into yw_workflow_apply_car(order_number,user_id,department,start_address,end_address," \
                  "start_date, end_date,car_type,use_person,car_person,car_number,car_mileage,reason,remark, status) " \
                  "values(%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,'0')"
            cur.execute(sql, (form_var.get('order_number'), public.user_id, form_var.get('department'),
                              form_var.get('start_address'), form_var.get('end_address'), form_var.get('start_date'),
                              form_var.get('end_date'), form_var.get('car_type'), form_var.get('use_person'),
                              form_var.get('car_person'), form_var.get('car_number'), form_var.get('car_mileage'),
                              form_var.get('reason'), form_var.get('remark')))
            # 查询刚刚插入的ID
            cur.execute("SELECT LAST_INSERT_ID()")  # 获取自增字段刚刚插入的ID
            row = cur.fetchone()
            if row:
                body['form_var']['id'] = row[0]


        cur.close()

        submit_power = {"show": True, "disabled": True} #提交按钮置灰

    except Exception as ex:
        log.error("生成数据失败!"+str(ex), exc_info=True, extra={'ptlsh':public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()
        public.respcode, public.respmsg = "300010", "生成数据失败!"+str(ex)
        public.respinfo = HttpResponse( public.setrespinfo() )
        return public.respinfo

    public.respcode, public.respmsg = "000000", "生成数据成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": body
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo


#用车申请-归还
def use_car_apply_return( request ):
    log = public.logger
    body = public.req_body
    form_var = body.get('form_var')

    try:
        id = form_var.get('id')

        if not id:
            public.respcode, public.respmsg = "333102", "用车申请数据不存在!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标
        sql = "select status, apply_state from yw_workflow_apply_car where id=%s"
        cur.execute(sql, id)
        row = cur.fetchone()
        if not row:
            public.respcode, public.respmsg = "333001", "原数据不存在!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if row[0] == '3':
            public.respcode, public.respmsg = "333003", "车辆已归还!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if row[1] != '3':
            public.respcode, public.respmsg = "333004", "审批未通过!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        sql = "update yw_workflow_apply_car set status=%s,act_returntime=%s,act_returnaddr=%s, act_mileage=%s, act_others=%s  where id=%s "
        cur.execute(sql, ('3', form_var.get('act_returntime'), form_var.get('act_returnaddr'),
                          form_var.get('act_mileage'), form_var.get('act_others'), id ))

        cur.close()

        body['form_var']['status'] = '3'

        submit_power = {"show": True, "disabled": True} #提交按钮置灰

    except Exception as ex:
        log.error("生成数据失败!"+str(ex), exc_info=True, extra={'ptlsh':public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()
        public.respcode, public.respmsg = "300010", "生成数据失败!"+str(ex)
        public.respinfo = HttpResponse( public.setrespinfo() )
        return public.respinfo

    public.respcode, public.respmsg = "000000", "生成数据成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": body
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo


#用章申请-提交请求
def use_seal_apply_commit( request ):
    log = public.logger
    body = public.req_body
    form_var = body.get('form_var')

    try:
        id = form_var.get('id')

        if not form_var.get('department'):
            public.respcode, public.respmsg = "335102", "申请部门不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('use_addr'):
            public.respcode, public.respmsg = "335102", "使用地点不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('start_date'):
            public.respcode, public.respmsg = "335102", "预计开始时间不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('end_date'):
            public.respcode, public.respmsg = "335102", "预计归还时间不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('seal_type'):
            public.respcode, public.respmsg = "335102", "印章类型不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('use_person'):
            public.respcode, public.respmsg = "335102", "使用人不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if not form_var.get('use_reason'):
            public.respcode, public.respmsg = "335102", "使用事由不可为空!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标

        if id: #更新数据
            sql = "select status, user_id from yw_workflow_apply_seal where id=%s"
            cur.execute(sql, id)
            row = cur.fetchone()
            if not row:
                public.respcode, public.respmsg = "335001", "原数据不存在!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo
            if row[0] not in  ['0','2']:
                public.respcode, public.respmsg = "335002", "审批状态非初始,不可修改!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo
            if row[1] != public.user_id:
                public.respcode, public.respmsg = "335004", "只可修改自己的单据!"
                public.respinfo = HttpResponse(public.setrespinfo())
                return public.respinfo

            sql="update yw_workflow_apply_seal set department=%s,file_name=%s,file_num=%s, start_date=%s, end_date=%s, " \
                "seal_type=%s, use_person=%s, use_addr=%s,use_reason=%s,remark=%s,status='0' where id=%s "
            cur.execute(sql, (form_var.get('department'), form_var.get('file_name'), form_var.get('file_num'),
                              form_var.get('start_date'), form_var.get('end_date'), form_var.get('seal_type'),
                              form_var.get('use_person'), form_var.get('use_addr'),
                               form_var.get('use_reason'), form_var.get('remark'), id) )

        else: #插入数据

            order_number = public_db.Get_SeqNo( 'USE_SEAL' )
            body['form_var']['order_number'] = order_number

            sql = "insert into yw_workflow_apply_seal(order_number,user_id,department,use_reason,file_name," \
                  "file_num,start_date, end_date,seal_type,use_person,use_addr,remark,status) " \
                  "values(%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,'0' )"
            cur.execute(sql, (form_var.get('order_number'), public.user_id, form_var.get('department'),
                              form_var.get('use_reason'), form_var.get('file_name'), form_var.get('file_num'),
                              form_var.get('start_date'),
                              form_var.get('end_date'), form_var.get('seal_type'), form_var.get('use_person'),
                              form_var.get('use_addr'), form_var.get('remark')))
            # 查询刚刚插入的ID
            cur.execute("SELECT LAST_INSERT_ID()")  # 获取自增字段刚刚插入的ID
            row = cur.fetchone()
            if row:
                body['form_var']['id'] = row[0]


        cur.close()

        submit_power = {"show": True, "disabled": True} #提交按钮置灰

    except Exception as ex:
        log.error("生成数据失败!"+str(ex), exc_info=True, extra={'ptlsh':public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()
        public.respcode, public.respmsg = "300010", "生成数据失败!"+str(ex)
        public.respinfo = HttpResponse( public.setrespinfo() )
        return public.respinfo

    public.respcode, public.respmsg = "000000", "生成数据成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": body
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo


#用章申请-归还
def use_seal_apply_return( request ):
    log = public.logger
    body = public.req_body
    form_var = body.get('form_var')

    try:
        id = form_var.get('id')

        if not id:
            public.respcode, public.respmsg = "335102", "用章申请数据不存在!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        cur = connection.cursor()  # 创建游标
        sql = "select status, apply_state from yw_workflow_apply_seal where id=%s"
        cur.execute(sql, id)
        row = cur.fetchone()
        if not row:
            public.respcode, public.respmsg = "335001", "原数据不存在!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if row[0] == '3':
            public.respcode, public.respmsg = "335003", "印章已归还!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        if row[1] != '3':
            public.respcode, public.respmsg = "335004", "审批未通过!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        sql = "update yw_workflow_apply_seal set status=%s,act_returntime=%s,act_returnaddr=%s, act_others=%s  where id=%s "
        cur.execute(sql, ('3', form_var.get('act_returntime'), form_var.get('act_returnaddr'),
                     form_var.get('act_others'), id ))

        cur.close()

        body['form_var']['status'] = '3'

        submit_power = {"show": True, "disabled": True} #提交按钮置灰

    except Exception as ex:
        log.error("生成数据失败!"+str(ex), exc_info=True, extra={'ptlsh':public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        cur.close()
        public.respcode, public.respmsg = "300010", "生成数据失败!"+str(ex)
        public.respinfo = HttpResponse( public.setrespinfo() )
        return public.respinfo

    public.respcode, public.respmsg = "000000", "生成数据成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": body
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo


