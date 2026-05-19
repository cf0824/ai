from django.shortcuts import HttpResponse
import json
import datetime
from  admin_app.sys import public
import os
import base64
import hashlib
from django.db import connection
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils import MyLog
import requests

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

###########################################################################################################
#文件接口  文件上传，下载，列表查看
#add by litz, 20200414
#
###########################################################################################################

#上传文件
def upload(request):
    log.info('upload')

    if request.method != "POST":  # 仅支持POST调用
        public.respcode, public.respmsg = "100000", "api error! Support only POST!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    # 获取公共数据
    public.menu_id = request.POST.get('mid')
    public.user_id = request.POST.get('uid')
    public.tran_type = request.POST.get('tran_type')
    public.check_sum = request.POST.get('check_sum')
    public.req_seq = request.POST.get('req_seq')
    public.req_ip = request.META.get('REMOTE_ADDR')  # 请求IP地址

    # 获取文件信息,
    file_obj = request.FILES.get("file")

    filename_ext = file_obj.name.split('.')[1]
    # 获取文件内容到变量中
    filexx=b''
    for line in file_obj.chunks():
        filexx=filexx+line

    # 生成md5值的文件名
    m2 = hashlib.md5()
    m2.update(filexx)
    md5filename = m2.hexdigest() + '.' + filename_ext
    del filexx
    #判断文件是否存在,存在不处理，不存在则写处
    if not os.path.exists(public.localhome+"fileup/"+md5filename):
        # 写入本地指定目录
        with open(public.localhome+"fileup/"+md5filename, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)
        f.close()

    # 登记文件信息表
    cur = connection.cursor()  # 创建游标
    sql = "insert into sys_fileup(file_name,file_size,md5_name,tran_date,user_id, menu_id,content_type,req_seq,req_ip,state) " \
          "values('%s','%s','%s','%s','%s', '%s','%s','%s','%s','%s')" \
          % (file_obj.name, file_obj.size, md5filename, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             public.user_id, public.menu_id, file_obj.content_type, public.req_seq, public.req_ip, '1')
    # print(sql)
    cur.execute(sql)
    cur.execute("SELECT LAST_INSERT_ID()")  # 获取自增字段刚刚插入的ID
    connection.commit()
    row = cur.fetchone()
    if row:
        file_id = row[0]
    else:
        public.respcode, public.respmsg = "100132", "文件上传失败!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    public.respcode, public.respmsg = "000000", "上传文件成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {
            "file_id": file_id
        }
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo

#下载文件
def download(request):
    log = public.logger
    if request.method != "POST":  # 仅支持POST调用
        public.respcode, public.respmsg = "100000", "api error! Support only POST!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    reqest_body = json.loads(request.body.decode(encoding='utf-8'))  # 请求报文转换为JSON报文
    # 获取请求变量
    public.req_ip = request.META.get('REMOTE_ADDR')  # 请求IP地址
    public.req_head = reqest_body.get('HEAD', None)  # 请求报文头
    public.req_body = reqest_body.get('BODY', None)  # 请求报文体
    if public.req_head:
        public.menu_id = public.req_head.get('mid', '')  # 菜单ID
        public.user_id = public.req_head['uid']  # 请求用户ID
        public.check_sum = public.req_head['checksum']  # session校验码
        public.tran_type = public.req_head['tran_type']  # 交易代码
        public.req_seq = public.req_head['req_seq']  # 请求流水号
    else:
        log.info("请求报文头错误!", extra={'ptlsh': public.req_seq})
        public.respcode, public.respmsg = "100000", "请求报文头错误!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    # 获取文件信息,
    file_id=public.req_body.get("file_id")
    # print('file_id=',file_id)

    # 查询文件信息表
    cur = connection.cursor()  # 创建游标
    sql = "select file_name,md5_name,content_type from sys_fileup where file_id='%s' and state='1'" % (file_id)
    cur.execute(sql)
    row = cur.fetchone()
    if row:
        file_name = row[0]
        file_md5name = row[1]
        file_contenttype = row[2]
    else:
        public.respcode, public.respmsg = "100133", "文件不存在!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    fullpathfile=public.localhome+"fileup/"+file_md5name
    # print('fullpathfile=',fullpathfile)
    if not os.path.exists(fullpathfile):
        # public.respcode, public.respmsg = "100134", "文件已过期!"
        public.respcode, public.respmsg = "000000", "文件已过期!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    with open(public.localhome+"fileup/"+file_md5name, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        file_base64 = base64_data.decode()

    public.respcode, public.respmsg = "000000", "文件下载成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {
            "id": file_id,
            "name":file_name,
            "type":file_contenttype,
            "url":'data:%s;base64,%s' % (file_contenttype, file_base64),
        }
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo



#上传文件
def chart_media_upload(request):
    log = public.logger
    if request.method != "POST":  # 仅支持POST调用
        public.respcode, public.respmsg = "100000", "api error! Support only POST!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    # # 获取公共数据
    # public.menu_id = request.POST.get('mid')
    # public.user_id = request.POST.get('uid')
    # public.tran_type = request.POST.get('tran_type')
    # public.check_sum = request.POST.get('check_sum')
    # public.req_seq = request.POST.get('req_seq')
    # public.req_ip = request.META.get('REMOTE_ADDR')  # 请求IP地址

    # 获取文件信息,
    file_obj = request.FILES.get("file")

    filename_ext = file_obj.name.split('.')[1]
    # 获取文件内容到变量中
    filexx=b''
    for line in file_obj.chunks():
        filexx=filexx+line

    # 生成md5值的文件名
    m2 = hashlib.md5()
    m2.update(filexx)
    md5filename = m2.hexdigest() + '.' + filename_ext
    del filexx
    # 目录不存在就创建
    media_dir = public.localhome+"static/chart_media/"
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    #判断文件是否存在,存在不处理，不存在则写处
    if not os.path.exists(media_dir+md5filename):
        # 写入本地指定目录
        with open(media_dir+md5filename, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)
        f.close()

    # 登记文件信息
    cursor = connection.cursor()
    sql = "insert into sys_chart_media(media_old_name,media_name,create_time,state) value(%s,%s,now(),'1')"
    cursor.execute(sql,(file_obj.name,md5filename))
    connection.commit()
    # # 登记文件信息表
    # cur = connection.cursor()  # 创建游标
    # sql = "insert into sys_fileup(file_name,file_size,md5_name,tran_date,user_id, menu_id,content_type,req_seq,req_ip,state) " \
    #       "values('%s','%s','%s','%s','%s', '%s','%s','%s','%s','%s')" \
    #       % (file_obj.name, file_obj.size, md5filename, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #          public.user_id, public.menu_id, file_obj.content_type, public.req_seq, public.req_ip, '1')
    # # print(sql)
    # cur.execute(sql)
    # cur.execute("SELECT LAST_INSERT_ID()")  # 获取自增字段刚刚插入的ID
    # connection.commit()
    # row = cur.fetchone()
    # if row:
    #     file_id = row[0]
    # else:
    #     public.respcode, public.respmsg = "100132", "文件上传失败!"
    #     public.respinfo = HttpResponse(public.setrespinfo())
    #     return public.respinfo

    # file_id = 0
    public.respcode, public.respmsg = "000000", "上传文件成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {
            # "file_id": file_id
        }
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo


# def upload_tencent(request):
#     log = public.logger
#     log.info(f'---------腾讯云上传文件-------')
#     if request.method != 'POST':
#         return HttpResponseBadRequest()
#     # token = request.META.get('HTTP_TOKEN')
#     # 校验token
#     # print('request.FILES=',request.FILES)
#     file = request.FILES.get('file')
#     log.info(f'file:{file}')
#     res = {}
#     if file is None:
#         res['code'] = 400
#         res['msg'] = "上传的图片不能为空"
#         return return_resp(res)
#     log.info(f'file:{file}')
#     log.info(f'file.name={file.name}')
#     log.info(f'file.size={file.size}')
#     try:
#         res = upload_obj.tencent_cos_upload(file)
#     except Exception as e:
#         log.error(f'上传失败：{e}', exc_info=True)
#     return return_resp(res)

def tencent_cos_upload(request):
    try:
        from admin_app.utils.uploadUtil import TencentCOS
        log.info(f'上传tencent_cos_upload')
        if request.method != "POST":  # 仅支持POST调用
            public.respcode, public.respmsg = "100000", "api error! Support only POST!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo
        # 获取文件信息,
        files = request.FILES.get("file")

        tencent_oss = TencentCOS(log)

        _uploads = tencent_oss.tencent_cos_upload(files, 'share_profit')

        public.respcode, public.respmsg = "000000", "上传文件成功!"
        json_data = {
            "HEAD": public.resphead_setvalue(),
            "BODY": {
                "file_id": _uploads[0]
            }
        }
        s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
        public.respinfo = HttpResponse(s)
        return public.respinfo
    except Exception as e:
        log.error(e, exc_info=True)

def tencent_cos_download(request):
    try:
        log.info(f'下载腾讯云')
        if request.method != "POST":  # 仅支持POST调用
            public.respcode, public.respmsg = "100000", "api error! Support only POST!"
            public.respinfo = HttpResponse(public.setrespinfo())
            return public.respinfo

        reqest_body = json.loads(request.body.decode(encoding='utf-8'))  # 请求报文转换为JSON报文
        # 获取请求变量
        public.req_ip = request.META.get('REMOTE_ADDR')  # 请求IP地址
        public.req_head = reqest_body.get('HEAD', None)  # 请求报文头
        public.req_body = reqest_body.get('BODY', None)  # 请求报文体

        file_id = public.req_body.get("file_id")
        log.info(f'file_id: {file_id}')
        file_name = file_id['fileName']
        file_url = file_id['fileUrl']
        file_type = file_id['fileType']

        # 发送GET请求
        log.info(f'1')
        response = requests.get(file_url, stream=True)
        # 下载腾讯文件到本地
        # local_filename = public.localhome + "fileup/" + file_name
        # if response.status_code == 200:
        #     # 确保本地目录存在
        #     os.makedirs(os.path.dirname(local_filename), exist_ok=True)
        #     # 将文件内容保存到本地
        #     with open(local_filename, 'wb') as f:
        #         for chunk in response.iter_content(chunk_size=8192):
        #             f.write(chunk)
        #     # 现在将文件内容读取为Base64编码的字符串（如果需要）
        #     with open(local_filename, 'rb') as f:
        #         base64_data = base64.b64encode(f.read())
        #         file_base64 = base64_data.decode()
        log.info(f'2')
        if response.status_code == 200:
            # 初始化一个空的bytearray来存储文件内容
            file_content = bytearray()
            # 读取响应的字节流，并添加到bytearray中
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_content.extend(chunk)
            # 将bytearray转换为bytes，然后编码为Base64
            base64_data = base64.b64encode(file_content)
            file_base64 = base64_data.decode()  # 解码为字符串

        public.respcode, public.respmsg = "000000", "文件下载成功!"

        json_data = {
            "HEAD": public.resphead_setvalue(),
            "BODY": {
                "id": file_id,
                "name": file_name,
                "type": file_type,
                "url": 'data:%s;base64,%s' % (file_type, file_base64),
            }
        }
        s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
        public.respinfo = HttpResponse(s)
        return public.respinfo
    except Exception as e:
        log.error(e, exc_info=True)



#下载文件
def only_download(request):
    log = public.logger
    if request.method != "POST":  # 仅支持POST调用
        public.respcode, public.respmsg = "100000", "api error! Support only POST!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    reqest_body = json.loads(request.body.decode(encoding='utf-8'))  # 请求报文转换为JSON报文
    # 获取请求变量
    public.req_ip = request.META.get('REMOTE_ADDR')  # 请求IP地址
    public.req_head = reqest_body.get('HEAD', None)  # 请求报文头
    public.req_body = reqest_body.get('BODY', None)  # 请求报文体
    if public.req_head:
        public.menu_id = public.req_head.get('mid', '')  # 菜单ID
        public.user_id = public.req_head['uid']  # 请求用户ID
        public.check_sum = public.req_head['checksum']  # session校验码
        public.tran_type = public.req_head['tran_type']  # 交易代码
        public.req_seq = public.req_head['req_seq']  # 请求流水号
    else:
        log.info("请求报文头错误!", extra={'ptlsh': public.req_seq})
        public.respcode, public.respmsg = "100000", "请求报文头错误!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    # 获取文件信息,
    file_id=public.req_body.get("file_id")
    # print('file_id=',file_id)

    # 查询文件信息表
    cur = connection.cursor()  # 创建游标
    sql = "select file_name,md5_name,content_type from sys_fileup where file_id='%s' and state='1'" % (file_id)
    cur.execute(sql)
    row = cur.fetchone()
    if row:
        file_name = row[0]
        file_md5name = row[1]
        file_contenttype = row[2]
    else:
        public.respcode, public.respmsg = "100133", "文件不存在!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    fullpathfile=public.localhome+"fileup/"+file_md5name
    # print('fullpathfile=',fullpathfile)
    if not os.path.exists(fullpathfile):
        # public.respcode, public.respmsg = "100134", "文件已过期!"
        public.respcode, public.respmsg = "000000", "文件已过期!"
        public.respinfo = HttpResponse(public.setrespinfo())
        return public.respinfo

    with open(public.localhome+"fileup/"+file_md5name, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        file_base64 = base64_data.decode()

    public.respcode, public.respmsg = "000000", "文件下载成功!"
    json_data = {
        "HEAD": public.resphead_setvalue(),
        "BODY": {
            "id": file_id,
            "name":file_name,
            "type":file_contenttype,
            "url":'data:%s;base64,%s' % (file_contenttype, file_base64),
        }
    }
    s = json.dumps(json_data, cls=public.JsonCustomEncoder, ensure_ascii=False)
    public.respinfo = HttpResponse(s)
    return public.respinfo