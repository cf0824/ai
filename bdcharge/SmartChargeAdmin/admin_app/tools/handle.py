from django.shortcuts import HttpResponse
from django.db import connection, transaction
from admin_app.sys import public


#增删改查配置数据操作主流程
@transaction.atomic()
def func_handle( request ,gb):
    public.respcode, public.respmsg = "999998", "交易开始处理!"
    log = public.logger
    sid = transaction.savepoint()
    if gb.get(public.tran_type):
        log.info('---[%s]-begin---' % (public.tran_type), extra={'ptlsh': public.req_seq})
        log = public.logger
        data = public.req_body
        resp={
            'respcode':'000000',
            'respmsg':'交易成功'
        }
        resp = gb[public.tran_type](request,data,resp)
        public.respcode, public.respmsg=resp['respcode'],resp['respmsg']
        del resp['respcode'],resp['respmsg']
        public.respinfo=public.setrespinfo(resp)
        log.info('---[%s]-end----' % (public.tran_type), extra={'ptlsh': public.req_seq})
        return public.respinfo
    else:
        public.respcode, public.respmsg = "100002", "trantype error!"
        public.respinfo = HttpResponse( public.setrespinfo() )
    if public.respcode=="000000":
        # 提交事务
        transaction.savepoint_commit(sid)