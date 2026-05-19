import sys
import os
import shutil
from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
from admin_app.sys import public
import datetime
import base64
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR, err_msg
from admin_app.tools.aes_sdk import AesEncrypt
from admin_cfg.settings import PM_ADMIN_UPDATE_KEY, BASE_DIR


# 增删改查配置数据操作主流程
def Main_Proc(request):
    gb = globals()
    return handle.func_handle(request, gb)


docker_home = "/admin/"


# 升级初始化
def update_init(request, data, resp):
    log = public.logger

    log.info(f"项目根目录".format(docker_home))

    form_var = data.get('form_data', {})
    log.info("升级初始化")
    try:
        with open(f"{docker_home}/version.info", 'r') as f:
            version = f.read()
    except Exception as e:
        log.info(f"Failed to read version {str()}", exc_info=True)
        raise Exception('项目根路径路径: {}'.format(docker_home))
    form_var['now_version'] = version
    form_var['update_package'] = ""
    resp['form_var'] = form_var
    return resp


def download_log(request, data, resp):
    form_var = data.get('form_var', {})
    id = form_var.get('id')
    cursor = connection.cursor()
    sql = "select update_version from sys_update_info where id=%s"
    cursor.execute(sql, id)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('日志不存在')
    update_version, = row
    localhome = public.localhome[:-1]
    log_path = f"{docker_home}/.updates/{update_version}/update.log"
    if not os.path.exists(log_path):
        return err_msg('日志不存在')
    with open(log_path, 'rb') as f:
        b = f.read()
        base64_data = base64.b64encode(b)
        file_base64 = base64_data.decode()
    resp['respcode'] = '125800'
    resp['filename'] = f"update-{update_version}.log"
    resp['filetype'] = 'text/plain'
    resp['filedata'] = file_base64
    return resp


def compare_version(old_version, new_version):
    log = public.logger
    v1 = str(old_version).lstrip('v').split('.')
    v2 = str(new_version).lstrip('v').split('.')
    log.info(f"old_version={v1}")
    log.info(f"new_version={v2}")
    for i in range(3):
        log.info(f"old_version_{i}={v1[i]}")
        log.info(f"new_version_{i}={v2[i]}")
        if int(v2[i]) > int(v1[i]):
            return True
    return False


# 开始升级
def start_update(request, data, resp):
    log = public.logger
    localhome = public.localhome[:-1]
    form_var = data.get('form_var', {})
    now_version = form_var.get('now_version')
    update_package = form_var.get('update_package')
    cursor = connection.cursor()
    sql = "select file_name, md5_name from sys_fileup where file_id=%s"
    cursor.execute(sql, update_package)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('升级包不存在')
    log.info('开始升级')

    try:
        file_name, md5_name = row
        file_path = f"{docker_home}/fileup/{md5_name}"
        # update_version = file_name.split('-')[1]
        ae = AesEncrypt(PM_ADMIN_UPDATE_KEY)
        zip_dir = f'/tmp/pmadmin_updates'
        zip_path = f'{zip_dir}/{md5_name}.zip'
        if not os.path.exists(zip_dir):
            os.makedirs(zip_dir)

        # 解密升级包
        log.info('开始解密升级包')
        ae.file_decrypt(file_path, zip_path)
        log.info('升级包解密成功，开始解压升级包')

        # 解压升级包
        unzip_dir = f"{docker_home}/.updates"
        unzip_path = f"{zip_dir}/{md5_name}"
        if not os.path.exists(unzip_dir):
            os.makedirs(unzip_dir)
        log.info('1=%s,2=%s' % (zip_path, unzip_path))
        ae.un_zip(zip_path, unzip_path)
        log.info('升级包解压成功')

        _package_list = os.listdir(unzip_path)
        update_version = _package_list[0]
        admin_update_path = f"{docker_home}/.updates"
        if not os.path.exists(admin_update_path):
            os.makedirs(admin_update_path)
        # 移动到的目录
        to_path = f"{admin_update_path}/{update_version}"
        if os.path.exists(to_path):
            log.info(f'to_path={to_path},目录已存在，删除')
            shutil.rmtree(to_path, ignore_errors=True)
        shutil.move(f"{unzip_path}/{update_version}", admin_update_path)
        log.info('升级文件已移动到项目根目录')
    except:
        log.error('升级失败', exc_info=True)
        return err_msg('升级包解析失败')
    if not compare_version(now_version, update_version):
        return err_msg('当前版本已经是最新了，无需升级')
    sql = "insert into sys_update_info(old_version,update_version,update_package_name,create_time,state) value(%s,%s,%s,%s,%s)"
    cursor.execute(sql, (now_version, update_version, file_name, datetime.datetime.now(), '0'))
    update_id = cursor.lastrowid

    # 开始执行升级脚本
    shell_path = f"{admin_update_path}/{update_version}/run.py"
    cmd = f"python {shell_path} {docker_home} {update_version}"
    log.info(f'cmd={cmd}')
    res = os.system(cmd)
    log.info(f'res={res}')
    if res == 0:
        state = '1'
    else:
        state = '9'

    sql = "update sys_update_info set state=%s,finish_time=%s where id=%s and state=%s"
    cursor.execute(sql, (state, datetime.datetime.now(), update_id, '0'))
    log.info(f'update res={res}')
    return resp


# 开始回退
def start_rollback(request, data, resp):
    log = public.logger
    localhome = public.localhome[:-1]
    form_var = data.get('form_var', {})
    now_version = form_var.get('now_version')
    rollback_package = form_var.get('rollback_package')
    cursor = connection.cursor()
    sql = "select file_name, md5_name from sys_fileup where file_id=%s"
    cursor.execute(sql, rollback_package)
    row = cursor.fetchone()
    if not row or not row[0]:
        return err_msg('回退包不存在')
    log.info('开始回退')

    try:
        file_name, md5_name = row
        file_path = f"{docker_home}/fileup/{md5_name}"
        # update_version = file_name.split('-')[1]
        ae = AesEncrypt(PM_ADMIN_UPDATE_KEY)
        zip_dir = f'/tmp/pmadmin_roll_back'
        zip_path = f'{zip_dir}/{md5_name}.zip'
        if not os.path.exists(zip_dir):
            os.makedirs(zip_dir)

        # 解密升级包
        log.info('开始解密回退包')
        ae.file_decrypt(file_path, zip_path)
        log.info('回退包解密成功，开始解压回退包')

        # 解压升级包
        unzip_dir = f"{docker_home}/.rollback"
        unzip_path = f"{zip_dir}/{md5_name}"
        if not os.path.exists(unzip_dir):
            os.makedirs(unzip_dir)
        log.info('1=%s,2=%s' % (zip_path, unzip_path))
        ae.un_zip(zip_path, unzip_path)
        log.info('回退包解压成功')

        _package_list = os.listdir(unzip_path)
        roll_back_version = _package_list[0]
        log.info(f'roll_back_version={roll_back_version}')
        admin_rollback_path = f"{docker_home}/.rollback"
        if not os.path.exists(admin_rollback_path):
            os.makedirs(admin_rollback_path)
        # 移动到的目录
        to_path = f"{admin_rollback_path}/{roll_back_version}"
        if os.path.exists(to_path):
            log.info(f'to_path={to_path},目录已存在，删除')
            shutil.rmtree(to_path, ignore_errors=True)
        shutil.move(f"{unzip_path}/{roll_back_version}", admin_rollback_path)
        log.info('回退文件已移动到项目根目录')
    except:
        log.error('回退失败', exc_info=True)
        return err_msg('回退包解析失败')

    if not compare_version(roll_back_version, now_version):
        return err_msg('回退包版本不能高于现在的版的本')

    sql = "insert into sys_update_info(old_version,update_version,update_package_name,create_time,state) value(%s,%s,%s,%s,%s)"
    cursor.execute(sql, (now_version, roll_back_version, file_name, datetime.datetime.now(), '0'))
    update_id = cursor.lastrowid

    # 开始执行升级脚本
    shell_path = f"{admin_rollback_path}/{roll_back_version}/roll_back_run.py"
    cmd = f"python {shell_path} {docker_home} {roll_back_version}"
    log.info(f'cmd={cmd}')
    res = os.system(cmd)
    log.info(f'res={res}')
    if res == 0:
        state = '1'
    else:
        state = '9'

    sql = "update sys_update_info set state=%s,finish_time=%s where id=%s and state=%s"
    cursor.execute(sql, (state, datetime.datetime.now(), update_id, '0'))
    log.info(f'update res={res}')
    return resp
