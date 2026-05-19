#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：charge_pile.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/3/28 17:39 
@Description :
'''
import base64
import os
import sys
import tempfile
import zipfile

from django.shortcuts import HttpResponse
from django.db import connection, transaction
import json
import requests
from admin_app.sys import public
import datetime
from admin_app.tools import handle
from admin_app.tools.ErrorMsg import ERROR
from admin_cfg.settings import APP_API, HARDWARE_API, BASE_DIR
from admin_app.sys.public_db import Get_SeqNo
from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB


# 增删改查配置数据操作主流程
def Main_Proc(request):
    log = public.logger
    gb = globals()
    return handle.func_handle(request, gb)


# 测试
def test(request, data, resp):
    log = public.logger
    log.info('test begin')
    resp['detail'] = {'a': 1, 'b': 2}
    return resp

def test1(request, data, resp):
    log = public.logger
    log.info('test begin')
    form_var = data.get('form_var', {})
    log.info(f'{form_var}')
    form_var['local_img'] = '/SmartChargeAdmin/file/port_qrcode/编号001.20250401164111.jpg'
    form_var['online_img'] = 'https://kfrural-1257596698.cos.ap-shanghai.myqcloud.com/tencent_oss/qrcode/20250402/a6c9a96d71eb443abc8244c0da801e3d.png'
    resp['detail'] = {'a': 1, 'b': 2}
    resp['form_var'] = form_var
    return resp

def get_eq_info_detail(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    eq_id = form_data.get('eq_id')
    terminal_address = form_data.get('terminal_address')

    verify_dict = [
        ['eq_id', int, True, '设备id'],
        # ['terminal_address', str, True, '通讯地址']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_data)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    db = MySQLDB()
    sql = "select * from s_eq_args_private where eq_id=%s"
    args = (eq_id)
    eq_info = db.fetchone(sql, args)
    eq_info['domain']='bdcdz.pinmait.com'
    eq_info['port']='6999'

    log.info(f'设备详细参数:{eq_info}')
    resp['form_var'] = eq_info
    return resp

def update_eq_args_private(request, data, resp):
    log = public.logger
    from admin_app.utils.handle_hardware import handle_hardware_cmd_set
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')

    form_var['eq_id'] = int(form_var.get('eq_id'))
    verify_dict = [
        ['eq_id', int, True, '设备id'],
        ['heart_time', str, True, '心跳时间'],
        ['uplink_interval', str, True, '上送间隔'],
        ['delay_time', str, True, '充满延时'],
        ['domain', str, True, '域名端口'],
        ['port', str, True, '端口'],
        ['QR_code', str, True, '二维码内容'],
        ['max_power', str, True, '最大功率'],
        ['min_power', str, True, '最小功率'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    log.info(f"form_var{form_var}")
    eq_id = form_var.get('eq_id')
    terminal_address = form_var.get('terminal_address')
    heart_time = form_var.get('heart_time')
    uplink_interval = form_var.get('uplink_interval')
    delay_time = form_var.get('delay_time')
    domain = form_var.get('domain')
    port = form_var.get('port')
    signal_strength = form_var.get('signal_strength')
    QR_code = form_var.get('QR_code')
    max_power = form_var.get('max_power')
    min_power = form_var.get('min_power')

    try:
        db = MySQLDB()
        sql = "select * from s_eq_args_private where eq_id=%s"
        args = (eq_id)
        eq_info = db.fetchone(sql, args)
        log.info(f'设备详细参数:{eq_info}')

        paras = [
            {
                'type': 'set_comm_paras',
                'args': {
                        'heart_cycle': int(heart_time),
                        'up_cycle': int(uplink_interval),
                        'delay_time': int(delay_time)
                    }
            },
            {
                'type': 'set_power_range',
                'args': {
                    'max_power': int(max_power),
                    'min_power': int(min_power)
                }
            },
            {
                'type': 'set_QRCode',
                'args': {
                    'QR_data': QR_code
                }
            }
        ]
        handle_hardware_cmd_set(terminal_address, paras)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def generate_QRcode(request, data, resp):
    log = public.logger
    from admin_app.utils.handle_qrcode import generate_qrcode, upload_to_tencent
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_id', int, True, '设备id'],
        ['terminal_address', str, True, '通讯地址'],
        ['eq_port', str, True, '插座号'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_id = form_var.get('eq_id')
        terminal_address = form_var.get('terminal_address')
        eq_port = form_var.get('eq_port')

        data = '二维码链接'
        text = str(eq_id) + '-' + eq_port
        save_dir = BASE_DIR + '/file/port_qrcode/'
        file_path = generate_qrcode(data, text, save_dir)
        qr_info = upload_to_tencent(file_path, 'qrcode')
        qr_no = qr_info.get('qr_no')
        cos_url = qr_info.get('cos_url')
        data1 = {
            'qr_no': qr_no,
            'QR_code': cos_url
        }
        db.update('s_eq_port', data1, {'eq_id': eq_id, 'terminal_address': terminal_address, 'eq_port': eq_port})

        form_var['qr_no'] = qr_no
        form_var['QR_code'] = cos_url
        resp['form_var'] = form_var
        return resp
    except Exception as e:
        log.info(f'生成二维码失败', exc_info=True)
        raise

def generate_miniprogram_code(request, data, resp):
    log = public.logger
    from admin_app.utils.handle_qrcode import generate_miniprogram_code, upload_to_tencent, add_text_below_qrcode
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_id', int, True, '设备id'],
        ['terminal_address', str, True, '通讯地址'],
        ['eq_port', str, True, '插座号'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_id = form_var.get('eq_id')
        terminal_address = form_var.get('terminal_address')
        eq_port = form_var.get('eq_port')
        args = {
            "pileNum": eq_id,
            "port": eq_port
        }
        text = str(eq_id) + '-' + eq_port
        save_dir = BASE_DIR + '/file/port_qrcode/'
        file_path = generate_miniprogram_code(save_dir, args)
        add_text_below_qrcode(file_path, file_path, text, "DejaVuSans.ttf")

        qr_info = upload_to_tencent(file_path, 'qrcode')
        qr_no = qr_info.get('qr_no')
        cos_url = qr_info.get('cos_url')
        data1 = {
            'qr_no': qr_no,
            'QR_code': cos_url
        }
        db.update('s_eq_port', data1, {'eq_id': eq_id, 'terminal_address': terminal_address, 'eq_port': eq_port})

        form_var['qr_no'] = qr_no
        form_var['QR_code'] = cos_url
        resp['form_var'] = form_var
        return resp
    except Exception as e:
        log.info(f'生成二维码失败', exc_info=True)
        raise


def batch_generate_miniprogram_code(request, data, resp):
    log = public.logger
    from admin_app.utils.handle_qrcode import generate_miniprogram_code, upload_to_tencent, add_text_below_qrcode
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    select_data = form_var.get('select_data', {})

    log.info(f'传入的数据form_var: {form_var}')
    log.info(f'select_data:{select_data}')
    # verify_dict = [
    #     ['eq_id', int, True, '设备id'],
    #     ['terminal_address', str, True, '通讯地址'],
    #     ['eq_port', str, True, '插座号'],
    # ]
    # not_valid, valid_info = validate_params(verify_dict, form_var)
    # if not not_valid:
    #     return err_msg(msg=valid_info)
    # log.info(valid_info)
    if len(select_data) == 0:
        return err_msg(msg=f'请选择插座')
    try:
        db = MySQLDB()
        for data in select_data:
            eq_id = data.get('eq_id')
            terminal_address = data.get('terminal_address')
            eq_port = data.get('eq_port')
            args = {
                "pileNum": eq_id,
                "port": eq_port
            }
            text = str(eq_id) + '-' + eq_port
            save_dir = BASE_DIR + '/file/port_qrcode/'
            file_path = generate_miniprogram_code(save_dir, args)
            add_text_below_qrcode(file_path, file_path, text, "DejaVuSans.ttf")

            qr_info = upload_to_tencent(file_path, 'qrcode')
            qr_no = qr_info.get('qr_no')
            cos_url = qr_info.get('cos_url')
            data1 = {
                'qr_no': qr_no,
                'QR_code': cos_url
            }
            db.update('s_eq_port', data1, {'eq_id': eq_id, 'terminal_address': terminal_address, 'eq_port': eq_port})


        resp['form_var'] = form_var
        return resp
    except Exception as e:
        log.info(f'生成二维码失败', exc_info=True)
        raise



def download_qr_code(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_id', int, True, '设备id'],
        ['terminal_address', str, True, '通讯地址'],
        ['eq_port', str, True, '插座号'],
        ['qr_no', str, True, '二维码编号'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    qr_no = form_var.get('qr_no')
    try:
        db = MySQLDB()
        sql = 'select * from s_qrcode_info where qr_no =%s'
        args = (qr_no,)
        qr_info = db.fetchone(sql, args)
        if not qr_info:
            return err_msg('未找到二维码')
        local_path = qr_info.get('local_path')
        if not os.path.exists(local_path):
            return err_msg('二维码图片不存在')

        with open(local_path, 'rb') as f:
            b = f.read()
            base64_data = base64.b64encode(b)
            file_base64 = base64_data.decode()
        resp['respcode'] = '125800'
        resp['filename'] = qr_info.get('file_name')
        resp['filetype'] = 'text/plain'
        resp['filedata'] = file_base64
        return resp
    except Exception as e:
        log.error(f'二维码下载失败：{e}', exc_info=True)
        raise


def batch_download_qr_code(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    select_data = form_var.get('select_data', {})

    log.info(f'传入的数据form_var: {form_var}')
    log.info(f'select_data:{select_data}')
    # verify_dict = [
    #     ['eq_id', int, True, '设备id'],
    #     ['terminal_address', str, True, '通讯地址'],
    #     ['eq_port', str, True, '插座号'],
    #     ['qr_no', str, True, '二维码编号'],
    # ]
    # not_valid, valid_info = validate_params(verify_dict, form_var)
    # if not not_valid:
    #     return err_msg(msg=valid_info)
    # log.info(valid_info)
    if len(select_data) == 0:
        return err_msg(msg=f'请选择插座')

    qr_no = form_var.get('qr_no')
    try:
        db = MySQLDB()
        num = 0
        for item in select_data:
            num = num + 1
            qr_no = item.get('qr_no')
            if qr_no is None:
                return err_msg(msg=f'第{num}条记录没有二维码信息')
        zip_name = f"二维码-{select_data[0].get('id')} -{select_data[-1].get('id')}.zip"

        temp_dir = tempfile.TemporaryDirectory()
        zip_filename = os.path.join(temp_dir.name, 'qrcodes.zip')
        valid_files = []
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for item in select_data:
                qr_no = item.get('qr_no')
                sql = 'select * from s_qrcode_info where qr_no =%s'
                args = (qr_no,)
                qr_info = db.fetchone(sql, args)

                local_path = qr_info.get('local_path')
                if not os.path.exists(local_path):
                    continue  # 跳过不存在文件，可选记录错误

                # 使用唯一名称避免重名冲突（示例：qr_no + 原文件名）
                arcname = qr_info['file_name']
                zipf.write(local_path, arcname=arcname)
                valid_files.append(arcname)

        with open(zip_filename, 'rb') as f:
            zip_data = f.read()
        base64_zip = base64.b64encode(zip_data).decode()
        resp['respcode'] = '125800'
        resp['filename'] = zip_name
        resp['filetype'] = 'application/zip'
        resp['filedata'] = base64_zip



        temp_dir.cleanup()
        return resp
    except Exception as e:
        log.error(f'二维码下载失败：{e}', exc_info=True)
        raise


def get_question_category_tree_data(request, data, resp):
    log = public.logger
    from admin_app.utils.common import fetch_tree_data
    form_var = data.get('form_var', {})
    log.info(f"form_var{form_var}")
    father_id = form_var.get('father_id', 0)
    tree_data = fetch_tree_data("contest_question_category", "father_id", "id", "name", father_id)
    resp['data'] = tree_data
    return resp

def get_fee_no(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['fee_type', str, True, '设备id']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    fee_type = form_var.get('fee_type')
    site_id = form_var.get('site_id')
    if not site_id:
        return err_msg(msg='请先选择站点')
    try:
        db = MySQLDB()
        if fee_type == '1':
            sql = f"select distinct fee_no from s_fee_standard_1 where site_id={site_id}"
        elif fee_type == '2':
            sql = f"select distinct fee_no from s_fee_standard_2 where site_id={site_id}"
        else:
            log.error(f'收费类型错误')
            return err_msg('收费类型错误')
        result = db.fetchall(sql)
        log.info(f'计费规则信息：{result}')
        fee_no_option = []
        for item in result:
            data = {
                "key": item.get("fee_no"),
                "value": item.get("fee_no")
            }
            fee_no_option.append(data)
        form_var['fee_no_option'] = fee_no_option
        form_var['fee_no'] = None
        resp['form_var'] = form_var
        return resp
    except Exception as e:
        log.error(f'获取计费规则失败：{e}', exc_info=True)
        raise

@transaction.atomic()
def add_charge_pile(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['terminal_address', str, True, '通信地址'],
        ['site_id', int, True, '站点'],
        ['fee_type', str, True, '计价类型'],
        ['fee_no', str, True, '计价规则编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    terminal_address = form_var.get('terminal_address')
    password = form_var.get('password')
    site_id = form_var.get('site_id')
    eq_type_id = form_var.get('eq_type_id')
    hard_version = form_var.get('hard_version')
    soft_version = form_var.get('soft_version')
    agree_version = form_var.get('agree_version')
    remark = form_var.get('remark')
    create_time = form_var.get('create_time')
    state = form_var.get('state')
    fee_type = form_var.get('fee_type')
    fee_no = form_var.get('fee_no')
    port_count = form_var.get('port_count')
    L1 = form_var.get('region_id_1')
    L2 = form_var.get('region_id_2')
    L3 = form_var.get('region_id_3')

    try:
        db = MySQLDB()
        data = {
            'terminal_address': terminal_address,
            'password': password,
            'site_id': site_id,
            'eq_type_id': eq_type_id,
            'hard_version': hard_version,
            'soft_version': soft_version,
            'agree_version': agree_version,
            'remark': remark,
            'create_time': create_time,
            'state': state,
            'fee_type': fee_type,
            'fee_no': fee_no,
            'conn_state': '0',
            'eq_state': '1',
            'region_id_1': L1 if L1 else None,
            'region_id_2': L2 if L2 else None,
            'region_id_3': L3 if L3 else None
        }
        db.insert('s_eq_info', data)
        last_id = db.get_last_rowid()
        data1 = {
            'eq_id': last_id,
            'terminal_address': terminal_address
        }
        db.insert('s_eq_args_private', data1)
        if not port_count:
            port_count = 0
        port_count = int(port_count)
        if port_count:
            for i in range(port_count):
                data = {
                    'eq_id': last_id,
                    'terminal_address': terminal_address,
                    'eq_port': str(i).zfill(2),
                    'use_state': '0',
                    'conn_state': '0',
                    'state': '1'
                }
                db.insert('s_eq_port', data)


        return resp
    except Exception as e:
        log.error(f'添加充电桩失败：{e}', exc_info=True)
        raise


@transaction.atomic()
def update_charge_pile(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_id', int, True, '设备id'],
        ['terminal_address', str, True, '通信地址'],
        ['site_id', int, True, '站点'],
        ['fee_type', str, True, '计价类型'],
        ['fee_no', str, True, '计价规则编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    eq_id = form_var.get('eq_id')
    terminal_address = form_var.get('terminal_address')
    password = form_var.get('password')
    site_id = form_var.get('site_id')
    eq_type_id = form_var.get('eq_type_id')
    hard_version = form_var.get('hard_version')
    soft_version = form_var.get('soft_version')
    agree_version = form_var.get('agree_version')
    remark = form_var.get('remark')
    create_time = form_var.get('create_time')
    state = form_var.get('state')
    fee_type = form_var.get('fee_type')
    fee_no = form_var.get('fee_no')
    L1 = form_var.get('region_id_1', None)
    L2 = form_var.get('region_id_2', None)
    L3 = form_var.get('region_id_3', None)

    try:
        db = MySQLDB()
        data = {
            'terminal_address': terminal_address,
            'password': password,
            'site_id': site_id,
            'eq_type_id': eq_type_id,
            'hard_version': hard_version,
            'soft_version': soft_version,
            'agree_version': agree_version,
            'remark': remark,
            'create_time': create_time,
            'state': state,
            'fee_type': fee_type,
            'fee_no': fee_no,
            'region_id_1': L1 if L1 else None,
            'region_id_2': L2 if L2 else None,
            'region_id_3': L3 if L3 else None
            # 'conn_state': '0',
            # 'eq_state': '1'
        }
        db.update('s_eq_info', data, {'eq_id': eq_id})

        data1 = {
            'terminal_address': terminal_address
        }
        db.update('s_eq_args_private', data1, {'eq_id': eq_id})
        db.update('s_eq_port', data1, {'eq_id': eq_id})

        return resp
    except Exception as e:
        log.error(f'添加充电桩失败：{e}', exc_info=True)
        raise Exception(f"数据处理异常:{str(e)}")


def bind_pile_arg_config(request, data, resp):
    log = public.logger
    from admin_app.utils.handle_hardware import handle_hardware_cmd_set
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['terminal_address', str, True, '通信地址'],
        ['eq_id', int, True, '设备id'],
        ['eq_arg_no', str, True, '参数编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    terminal_address = form_var.get('terminal_address')
    eq_id = form_var.get('eq_id')
    eq_arg_no = form_var.get('eq_arg_no')
    try:
        db = MySQLDB()
        sql = "select * from s_eq_args_common where arg_no=%s"
        args = (eq_arg_no)
        arg_info = db.fetchone(sql, args)
        log.info(f'参数详情：{arg_info}')

        heart_time = arg_info.get('heart_time')
        uplink_interval = arg_info.get('uplink_interval')
        delay_time = arg_info.get('delay_time')
        domain = arg_info.get('domain')
        port = arg_info.get('port')
        max_power = arg_info.get('max_power')
        min_power = arg_info.get('min_power')

        paras = [
            {
                'type': 'set_comm_paras',
                'args': {
                    'heart_cycle': int(heart_time),
                    'up_cycle': int(uplink_interval),
                    'delay_time': int(delay_time)
                }
            },
            {
                'type': 'set_power_range',
                'args': {
                    'max_power': int(max_power),
                    'min_power': int(min_power)
                }
            }
        ]
        handle_hardware_cmd_set(terminal_address, paras)

        data = {
            'eq_arg_no': eq_arg_no
        }

        db.update('s_eq_info', data, {'eq_id': eq_id})
        
        return resp
    except Exception as e:
        log.error(f'更新设备统一参数失败：{e}', exc_info=True)
        raise


def add_port(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['terminal_address', str, True, '通信地址'],
        ['eq_id', int, True, '设备id'],
        ['port_list', str, True, '插座列表']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    terminal_address = form_var.get('terminal_address')
    eq_id = form_var.get('eq_id')
    port_list = form_var.get('port_list')

    try:
        from admin_app.utils.params_validate import validate_string, check_ports_existence
        db = MySQLDB()
        res = validate_string(port_list)
        if res[0]:
            parts = port_list.split(';')
            log.info(parts)
            sql = "select eq_port from s_eq_port where eq_id=%s and terminal_address=%s"
            params = (eq_id, terminal_address)
            port_info = db.fetchall(sql, params)
            log.info(f'已存在的端口：{port_info}')
            result_flag, existing_values = check_ports_existence(parts, port_info)
            if not result_flag:
                return err_msg(msg=f'端口：{existing_values} 已存在！')
            for part in parts:
                if part:
                    data = {
                        'eq_id': eq_id,
                        'terminal_address': terminal_address,
                        'eq_port': part,
                        'use_state': '0',
                        'conn_state': '0',
                        'state': '1'
                    }
                    db.insert('s_eq_port', data)
        else:
            return err_msg(msg=res[1])

        return resp
    except Exception as e:
        log.error(f'添加端口失败：{e}', exc_info=True)


def del_port(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['terminal_address', str, True, '通信地址'],
        ['id', int, True, 'id'],
        ['eq_id', int, True, '设备id'],
        ['eq_port', str, True, '插座']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    terminal_address = form_var.get('terminal_address')
    id = form_var.get('id')

    try:
        db = MySQLDB()
        eq_port = form_var.get('eq_port')
        use_state = form_var.get('use_state')
        if use_state == '1':
            return err_msg(msg=f'插座正在使用中，无法删除')
        db.delete('s_eq_port', {'id': id})


        return resp
    except Exception as e:
        log.error(f'添加端口失败：{e}', exc_info=True)


def add_common_args(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['site_id', int, True, '站点id'],
        # ['arg_no', str, True, '参数编号'],
        ['arg_name', str, True, '参数名称'],
        ['heart_time', str, True, '心跳时间'],
        ['uplink_interval', str, True, '上送间隔'],
        ['delay_time', str, True, '充满延时时间'],
        ['domain', str, True, '通讯域名'],
        ['port', str, True, '通讯端口'],
        ['max_power', str, True, '最大功率'],
        ['min_power', str, True, '最小功率'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        site_id = form_var.get('site_id')
        arg_no = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        arg_name = form_var.get('arg_name')
        heart_time = form_var.get('heart_time')
        uplink_interval = form_var.get('uplink_interval')
        delay_time = form_var.get('delay_time')
        domain = form_var.get('domain')
        port = form_var.get('port')
        max_power = form_var.get('max_power')
        min_power = form_var.get('min_power')
        if int(heart_time) > 0xFFFF:
            return err_msg(msg='心跳时间过大')
        if int(uplink_interval) > 0xFFFF:
            return err_msg(msg='上送间隔时间过大')
        if int(delay_time) > 0xFFFF:
            return err_msg(msg='充满延时时间过大')
        if int(port) > 0xFFFF:
            return err_msg(msg='端口超出范围')
        if int(max_power) > 0xFFFF:
            return err_msg(msg='最大功率过大')
        if int(min_power) > 0xFFFF:
            return err_msg(msg='最小功率过大')
        data = {
            'site_id': site_id,
            'arg_no': arg_no,
            'arg_name': arg_name,
            'heart_time': heart_time,
            'uplink_interval': uplink_interval,
            'delay_time': delay_time,
            'domain': domain,
            'port': port,
            'max_power': max_power,
            'min_power': min_power
        }
        db.insert('s_eq_args_common', data)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def update_common_args(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['id', int, True, 'id'],
        ['site_id', int, True, '站点id'],
        ['arg_no', str, True, '参数编号'],
        ['arg_name', str, True, '参数名称'],
        ['heart_time', str, True, '心跳时间'],
        ['uplink_interval', str, True, '上送间隔'],
        ['delay_time', str, True, '充满延时时间'],
        ['domain', str, True, '通讯域名'],
        ['port', str, True, '通讯端口'],
        ['max_power', str, True, '最大功率'],
        ['min_power', str, True, '最小功率'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        arg_name = form_var.get('arg_name')
        heart_time = form_var.get('heart_time')
        uplink_interval = form_var.get('uplink_interval')
        delay_time = form_var.get('delay_time')
        domain = form_var.get('domain')
        port = form_var.get('port')
        max_power = form_var.get('max_power')
        min_power = form_var.get('min_power')
        if int(heart_time) > 0xFFFF:
            return err_msg(msg='心跳时间过大')
        if int(uplink_interval) > 0xFFFF:
            return err_msg(msg='上送间隔时间过大')
        if int(delay_time) > 0xFFFF:
            return err_msg(msg='充满延时时间过大')
        if int(port) > 0xFFFF:
            return err_msg(msg='端口超出范围')
        if int(max_power) > 0xFFFF:
            return err_msg(msg='最大功率过大')
        if int(min_power) > 0xFFFF:
            return err_msg(msg='最小功率过大')
        data = {
            'site_id': site_id,
            'arg_name': arg_name,
            'heart_time': heart_time,
            'uplink_interval': uplink_interval,
            'delay_time': delay_time,
            'domain': domain,
            'port': port,
            'max_power': max_power,
            'min_power': min_power
        }
        db.update('s_eq_args_common', data, {'id': id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def add_eq_type(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_type', str, True, '类型'],

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_type = form_var.get('eq_type')


        data = {
            'eq_type': eq_type
        }
        db.insert('s_eq_type', data)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def update_eq_type(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_type_id', int, True, '类型id'],
        ['eq_type', str, True, '类型'],

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_type = form_var.get('eq_type')
        eq_type_id = form_var.get('eq_type_id')

        data = {
            'eq_type': eq_type
        }
        db.update('s_eq_type', data, {'eq_type_id': eq_type_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def del_eq_type(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['eq_type_id', int, True, '类型id']

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        eq_type_id = form_var.get('eq_type_id')
        db.delete('s_eq_type', {'eq_type_id': eq_type_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def update_port_state(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    verify_dict = [
        ['id', int, True, 'id'],
        ['use_state', str, True, '使用状态'],
        ['conn_state', str, True, '连接状态'],
        ['state', str, True, '状态'],

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        use_state = form_var.get('use_state')
        conn_state = form_var.get('conn_state')
        state = form_var.get('state')
        data = {
            'use_state': use_state,
            'conn_state': conn_state,
            'state': state,
            'update_time': datetime.datetime.now()
        }
        db.update('s_eq_port', data,{'id': id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def set_elec_price(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    select_data = form_var.get('select_data')
    log.info(f'select_data: {select_data}')
    if len(select_data) == 0:
        return err_msg(msg='请选择设备')
    verify_dict = [
        ['elec_price', str, True, 'id']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        elec_price = form_var.get('elec_price')
        for item in select_data:
            eq_id = item.get('eq_id')
            data = {
                'elec_price': elec_price
            }
            db.update('s_eq_info', data,{'eq_id': eq_id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

