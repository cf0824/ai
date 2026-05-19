__author__ = 'litz'

############################################################################################
# 共函数库
# add by litz,20200401
############################################################################################
import os
import datetime
import decimal
import string
import logging
import logging.handlers
import json
import random
from django.shortcuts import HttpResponse
from django.db import connection

localhome = os.getcwd() + '/'  # 本地根目录,对调用的程序来讲的路径，django就是程序根目录

# 全局变量，记录错误信息
exc_type = ''
exc_value = ''
exc_traceback = ''
# 全局变量，请求报文头公共变量
respcode, respmsg, respinfo = '', '', ''
menu_id, user_id, tran_type, check_sum, req_seq, req_ip = '', '', '', '', '', ''
req_head = {}
req_body = {}


# 返回报文头赋值
def resphead_setvalue():
    HEAD = {
        "mid": req_head.get('mid'),
        "uid": req_head.get('uid'),
        "tran_type": req_head.get('tran_type'),
        "checksum": req_head.get('checksum'),
        "req_seq": req_head.get('req_seq'),
        "respcode": respcode,
        "respmsg": respmsg,
    }
    return HEAD


# 查询类型，管理台配置查询条件时使用
selecttypes = [
    {
        "value": '=',
        "label": '='
    }, {
        "value": 'like',
        "label": 'like'
    }, {
        "value": '>',
        "label": '>'
    }, {
        "value": '<',
        "label": '<'
    }, {
        "value": '>=',
        "label": '>='
    }, {
        "value": '<=',
        "label": '<='
    }, {
        "value": 'is not null',
        "label": 'is not null'
    }, {
        "value": 'is null',
        "label": 'is null'
    }
]

# 日志初始化,日志名称
global logger, fh
logger = logging.getLogger(str(os.getpid()))


def loger_init(logname):
    # 日志中添加自定义字段，平台流水号
    def ptlsh(record):
        try:
            if record.ptlsh:
                pass
            else:
                record.ptlsh = 'noserial'
        except:
            record.ptlsh = 'noserial'
        return True

    # -----------------------------------------------#
    # 日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    if os.path.exists(localhome + 'log/'):
        log_file_temp = localhome + 'log/' + logname + '_' + now_time + '.log'
    else:
        log_file_temp = logname + '_' + now_time + '.log'
    # print(log_file_temp)
    # fh = logging.FileHandler(log_file_temp)  # 定义一个写文件的handler
    fh = logging.handlers.RotatingFileHandler(log_file_temp, maxBytes=1024 * 1024 * 100, backupCount=30)
    fh.addFilter(ptlsh)
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter('[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] '
                                     '[%(process)-7d] [%(ptlsh)s] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    # print('public',logger)
    if not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh


# 将date datetime decimal类型转换为json
class JsonCustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        elif isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return json.JSONEncoder.default(self, o)


# 返回信息转换为json格式
def setrespinfo(BODY=None):
    if req_head:
        json_data = {
            "HEAD": {
                "mid": req_head.get('mid'),
                "uid": req_head.get('uid'),
                "tran_type": req_head.get('tran_type'),
                "checksum": req_head.get('checksum'),
                "req_seq": req_head.get('req_seq'),
                "respcode": respcode,
                "respmsg": respmsg,
            },
        }
        if BODY:
            json_data['BODY'] = BODY
    else:
        json_data = {
            "respcode": respcode,
            "respmsg": respmsg,
        }
    s = json.dumps(json_data, cls=JsonCustomEncoder, ensure_ascii=False)
    return HttpResponse(s)


# session校验
def checksession(request):
    suid = request.session.get('uid', None)
    schecksum = request.session.get('checksum', None)
    print('suid=', suid, 'schecksum=', schecksum)
    print('user_id=', user_id, 'check_sum=', check_sum)
    # print(str(uid) != str(suid) or checksum != schecksum)
    # test --begin
    if check_sum == '11223355':
        return True
    # test --end

    if suid == None or schecksum == None:
        return False
    if str(user_id) != str(suid) or check_sum != schecksum:
        return False
    return True


# 生成整型随机数,number随机数个数
def getintrandom(number):
    rand = ''
    for i in range(0, int(number)):
        a = random.randint(0, 9)
        rand = rand + str(a)
    return rand


# 生成毫秒时间+10位随机数+进行号的字符串做为唯一标志
def genRandomString(slen=10):
    randstr = ''.join(random.sample(string.ascii_letters + string.digits, slen))
    return datetime.datetime.now().strftime('%H:%M:%S.%f') + "_" + randstr + "_" + str(os.getpid())


# 真或者假转为'Y','N'
def True2y(src):
    if src == 'True' or src == 'true' or src == True:
        return 'Y'
    else:
        return 'N'


# 'Y'或'N'转为真或者假
def Y2True(src):
    if src == 'Y' or src == 'y':
        return True
    else:
        return False


# 关键字转换
def SqlKeywordConver(sql_item, form_var, extra_data=None):
    extra_data = extra_data or {}
    resql = sql_item
    if form_var:
        for item in form_var:
            Keyword = '$[' + item + ']'
            # print("Keyword:"+str(Keyword) )
            # print("resql:"+str(resql) )
            if Keyword in resql:
                temp = str(form_var.get(item, ''))
                if temp == 'None':
                    value = 'null'
                else:
                    value = "'" + temp + "'"
                resql = resql.replace(Keyword, value)
            else:
                continue
    if '${USER_ID}' in resql:  # 用户ID系统变量
        value = "'" + str(user_id) + "'"
        resql = resql.replace('${USER_ID}', value)
    # if '${USER_ID}' in resql:  # 用户ID系统变量
    #     value = "'" + str(user_id) + "'"
    #     resql = resql.replace('${USER_ID}', value)
    if '${TRAN_DATE}' in resql:
        value = "'" + datetime.datetime.now().strftime('%Y-%m-%d') + "'"
        resql = resql.replace('${TRAN_DATE}', value)
    if '${TRAN_TIME}' in resql:
        value = "'" + datetime.datetime.now().strftime('%H:%M:%S') + "'"
        resql = resql.replace('${TRAN_TIME}', value)
    if '${TRAN_DATETIME}' in resql:
        value = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
        resql = resql.replace('${TRAN_DATETIME}', value)
    if '${ORG_ID}' in resql:
        value = "(SELECT org_id FROM sys_user_org WHERE user_id='%s')" % user_id
        resql = resql.replace('${ORG_ID}', value)
    if '${ORG_SPELL_ID}' in resql:
        value = "(select a.org_spell from sys_org a, sys_user_org b where a.org_id=b.org_id and b.user_id='%s')" % user_id
        resql = resql.replace('${ORG_SPELL_ID}', value)
    if '${ROLE_ID}' in resql:
        value = "(SELECT role_id FROM sys_user_role WHERE user_id='%s')" % user_id
        resql = resql.replace('${ROLE_ID}', value)
    if '${IS_SUPER_ADMIN}' in resql:
        # 判断是否是超级管理员
        cur = connection.cursor()  # 创建游标
        sql = "select * from sys_user_role where user_id=%s and role_id='root'"
        cur.execute(sql, user_id)
        row = cur.fetchone()
        if row and row[0]:
            # 是超级管理员
            value = "true"
        else:
            value = "false"
        resql = resql.replace('${IS_SUPER_ADMIN}', value)
    if '${DISABLED_MSG_TYPES}' in resql:
        value = f"(select distinct msg_type from (select msg_type from sys_msg_cfg where state='0' union select msg_type from sys_msg_user_cfg where user_id={user_id} and state='0') tmp)"
        resql = resql.replace('${DISABLED_MSG_TYPES}', value)

    # 20221203新增 替换extra数据
    logger.info('extra_data=%s' % extra_data)
    for extra_key in extra_data:
        rep_text = '${EXTRA.%s}' % extra_key
        rep_value = extra_data.get(extra_key)
        if rep_value:
            resql = resql.replace(rep_text, rep_value)
    return resql



