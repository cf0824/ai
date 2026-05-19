from django.shortcuts import HttpResponse
from django.db import connection
import sys
import traceback
import json
import random
import string
import datetime
from admin_app.sys import public

maxlength = 1024**2  # 最大日志记载


# 入口主流程.
# @transaction.atomic  # 当前视图函数中支持事务 #外加事务支持的业务代码内部就不要做泛型的try catch异常捕捉，这样会导致，真正的事务支持接不到异常，导致可能所需的事务回滚不会执行。
def Enter(request):
    global log, fh
    # 请求流水号赋初值
    public.req_seq = 'PT_'+datetime.datetime.now().strftime('%H%M%S%f')+"_"+''.join(random.sample(string.digits, 6))
    try:
        starttime = datetime.datetime.now()
        # 获取访问路径
        path = request.path.split('/')
        print('path=', path)
        if len(path) >= 4:
            param1 = "%s_%s" % (path[len(path) - 3], path[len(path) - 2])
        else:
            param1 = None

        # 初始化日志，根据请求的接口类别自动创建子日志
        if param1:
            log, fh = public.loger_init(param1)
        else:
            log, fh = public.loger_init('Term_Main')
        print('log=', log)

        log.info('----------------------Term_Main-begin---------------------------', extra={'ptlsh':public.req_seq})
        # log.info('headers=%s' % request.META)
        log.info("请求path:[%s]" % request.path, extra={'ptlsh': public.req_seq})
        log.info("请求method:[%s]" % request.method, extra={'ptlsh': public.req_seq})
        log.info("请求GET:[%s]" % request.GET, extra={'ptlsh': public.req_seq})
        # if request.method != "POST":  # 仅支持POST调用
        #     public.respinfo = HttpResponse("api error! Support only POST!")
        #     return public.respinfo

        reqest_body = request.body.decode(encoding='utf-8')  # 请求报文转换为JSON报文
        if len(str(request.body)) < maxlength:  # 日志太大不打印了,如文件上传等日志。
            log.info("请求body:[%d][%s]" % (len(str(reqest_body)), str(reqest_body)), extra={'ptlsh': public.req_seq})
        else:
            log.info("请求body:[%d][%s......]" % (len(str(reqest_body)), str(reqest_body[0:maxlength])), extra={'ptlsh': public.req_seq})
            # 大的请求报文只打印部分
        public.req_body = reqest_body
        # 根据请求path处理接口数据
        # log.info("请求path:[%d][%s]" % (len(path), str(path)), extra={'ptlsh': public.req_seq})
        # 调用指定函数
        try:
            # 动态地import需要创建的类，减少报错，内存的使用，加快速度等
            if len(path) >= 4:
                cmd_import = 'from admin_app.%s import %s' % (path[len(path) - 2], path[len(path) - 1])
                func_main_name = '%s.%s(request)' % (path[len(path) - 1], 'Main_Proc')
            else:
                cmd_import = 'none'
            log.info(f"cmd_import:[{cmd_import}], func_main_name:[{func_main_name}]", extra={'ptlsh': public.req_seq})
            exec(cmd_import)  # 动态地import需要创建的类
            # log.info("----Main-[%s.Main_Proc]-start---" % (path[3]), extra={'ptlsh': public.req_seq})
            public.respinfo = eval(func_main_name)
            # log.info("----Main-[%s.Main_Proc]-end----" % (path[3]), extra={'ptlsh': public.req_seq})
        except Exception as ex:
            log.error('程序运行错误:' + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
            public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
            public.respinfo = HttpResponse("api error!")
        return public.respinfo
    except Exception as ex:
        log.error('程序运行错误:'+str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        public.exc_type, public.exc_value, public.exc_traceback = sys.exc_info()
        public.respinfo = HttpResponse('程序运行错误:'+str(ex))
        return public.respinfo
    finally:
        try:
            if not public.respinfo:  # 如果返回信息为空
                public.respinfo = HttpResponse("系统错误[返回数据异常]")

            resp_pkg = public.respinfo.getvalue().decode(encoding='utf-8')
            if len(str(resp_pkg)) < maxlength:
                log.info("返回报文:[%d][%s]" % (len(str(public.respinfo)), resp_pkg), extra={'ptlsh':public.req_seq} )
            else:  # 日志太大不打印了,如文件上传等日志。
                resp_pkg = '返回报文太大，不记录到表中' # 返回报文太大，不记录到表中

            log.info('交易处理时间: %s' % str(datetime.datetime.now()-starttime), extra={'ptlsh':public.req_seq})
            log.info('----------------------Term_Main-end---------------------------', extra={'ptlsh':public.req_seq})

            if fh:
                fh.close()
                log.removeHandler(fh)
        except Exception as ex:
            log.error('系统finally处理失败:' + str(ex), exc_info=True, extra={'ptlsh': public.req_seq})
        return public.respinfo
