#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：share_profit.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/4/11 11:35 
@Description :
'''
import ast
import base64
import os
import sys
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

def add_disprofit_config(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['site_id', int, True, '站点id'],
        ['user_id', int, True, '分润对象id'],
        ['dis_rate', str, True, '分润比例']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        dis_rate = form_var.get('dis_rate')
        dis_rate = float(dis_rate)
        log.info(f'dis_rate:{dis_rate}')
        sql = "select * from s_dis_profit_cfg where site_id=%s"
        args = (site_id)
        disprofit_info = db.fetchall(sql, args)
        log.info(f'站点：{site_id}的分润信息:{disprofit_info}')
        total_rate = 0.00
        for item in disprofit_info:
            total_rate += item.get('dis_rate')

        if total_rate + dis_rate > 1:
            return err_msg(msg=f'该站点当前分润比例：{total_rate}, 新增比例不得超过：{1-total_rate}')
        data = {
            'site_id': site_id,
            'user_id': user_id,
            'dis_rate': dis_rate
        }
        db.insert('s_dis_profit_cfg', data)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def update_disprofit_config(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['id', int, True, 'id'],
        ['site_id', int, True, '站点id'],
        ['user_id', int, True, '分润对象id'],
        ['dis_rate', str, True, '分润比例']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        user_id = form_var.get('user_id')
        dis_rate = form_var.get('dis_rate')
        dis_rate = float(dis_rate)
        log.info(f'dis_rate:{dis_rate}')
        sql = "select * from s_dis_profit_cfg where site_id=%s"
        args = (site_id)
        disprofit_info = db.fetchall(sql, args)
        log.info(f'站点：{site_id}的分润信息:{disprofit_info}')
        total_rate = 0.00
        for item in disprofit_info:
            total_rate += item.get('dis_rate')

        if total_rate + dis_rate > 1:
            return err_msg(msg=f'该站点当前分润比例：{total_rate}, 新增比例不得超过：{1-total_rate}')
        data = {
            'site_id': site_id,
            'user_id': user_id,
            'dis_rate': dis_rate
        }
        db.update('s_dis_profit_cfg', data, {'id': id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def cal_profit_info(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    select_list = form_data.get('select_list')
    log.info(f'select_list: {select_list}')
    if not select_list:
        return err_msg(msg=f'请选择分润记录')
    verify_dict = [

    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        user_id = select_list[0].get('user_id')
        dis_money = 0.00
        count = 0
        for item in select_list:
            count += 1
            if item['state'] == '1':
                return err_msg(msg=f'第{count}记录已经分润过！')
            if item['user_id'] == user_id:
                dis_money = item['dis_money'] + dis_money
            else:
                return err_msg(msg=f'第{count}记录的分润对象不同，每次分润请选择同一个分润对象！')

        sql = 'select * from s_user_info where user_id=%s'
        arg = (user_id,)
        user_info = db.fetchone(sql, arg)
        log.info(f'分润对象信息: {user_info}')
        if not user_info:
            return err_msg(msg='该用户不存在')
        phone_number = user_info.get('phone_number')
        wx_nickname = user_info.get('wx_nickname')

        form_var['user_id'] = user_id
        form_var['phone_number'] = phone_number
        form_var['wx_nickname'] = wx_nickname
        form_var['dis_money'] = dis_money
        form_var['count'] = count
        form_var['select_list'] = f"{select_list}"
        resp['form_var'] = form_var

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


@transaction.atomic()
def create_share_profit(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    form_var['dis_money'] = float(form_var.get('dis_money'))
    verify_dict = [
        ['file', list, True, '截图'],
        ['user_id', int, True, '分润对象id'],
        ['dis_money', float, True, '分润金额'],
        ['select_list', str, True, '分润记录'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        file = form_var.get('file')
        select_list = form_var.get('select_list')
        user_id = form_var.get('user_id')
        dis_money = form_var.get('dis_money')
        profit_no = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        evidence_img = []
        for i in file:
            evidence_img.append(i.get('fileUrl'))
        data1 = {
            'profit_no': profit_no,
            'user_id': user_id,
            'evidence_img': str(evidence_img),
            'profit_money': dis_money,
            'profit_time': datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        }
        db.insert('s_dis_profit_record', data1)
        select_list = ast.literal_eval(select_list)
        log.info(f'select_list: {type(select_list)}')
        for data in select_list:
            log.info(f'data: {data}, type: {type(data)}')
            id = data.get('id')
            data2 = {
                'profit_no': profit_no,
                'profit_time': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                'state': '1'
            }
            db.update('s_dis_profit_detail', data2, {'id': id})

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
        raise


@transaction.atomic()
def create_share_profit_2(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')
    form_var['money'] = float(form_var.get('money'))
    verify_dict = [
        ['file', list, True, '截图'],
        ['user_id', int, True, '分润对象id'],
        ['money', float, True, '分润金额'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        file = form_var.get('file')
        user_id = form_var.get('user_id')
        money = form_var.get('money')
        begin_time = form_var.get('begin_time')
        end_time = form_var.get('end_time')
        profit_no = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        profit_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        evidence_img = []
        for i in file:
            evidence_img.append(i.get('fileUrl'))
        data1 = {
            'profit_no': profit_no,
            'user_id': user_id,
            'evidence_img': str(evidence_img),
            'profit_money': money,
            'profit_time': profit_time
        }
        db.insert('s_dis_profit_record', data1)

        sql = "update s_dis_profit_detail set profit_no =%s, profit_time =%s, state =%s where create_time >= %s and create_time <= %s and user_id =%s"
        args = (profit_no, profit_time, '1', begin_time, end_time, user_id)
        db.execute(sql, args)
        sql = "update s_deduction_detail set batch_no =%s, handle_time =%s, state =%s where create_time >= %s and create_time <= %s and user_id =%s"
        args = (profit_no, profit_time, '1', begin_time, end_time, user_id)
        db.execute(sql, args)

        return resp

    except Exception as e:
        log.error(e, exc_info=True)
        raise

def get_evidence_img_list(request, data, resp):
    log = public.logger
    log.info(f'data:{data}')
    form_var = data.get('form_var')
    log.info(f'form_var: {form_var}')
    id = form_var.get('id')
    profit_no = form_var.get('profit_no')
    evidence_img = form_var.get('evidence_img')
    evidence_img = json.loads(evidence_img.replace("'", '"'))

    table_data = []
    for data in evidence_img:
        table_item = {
            'evidence_img': data
        }
        table_data.append(table_item)
    resp['table_data'] = table_data

    return resp

def get_feedback_img_list(request, data, resp):
    log = public.logger
    log.info(f'data:{data}')
    form_var = data.get('form_var')
    log.info(f'form_var: {form_var}')
    id = form_var.get('id')
    feedback_img = form_var.get('feedback_img')
    if not feedback_img:
        return err_msg(msg='此反馈用户未提交图片')
    feedback_img = json.loads(feedback_img.replace("'", '"'))

    table_data = []
    for data in feedback_img:
        table_item = {
            'feedback_img': data
        }
        table_data.append(table_item)
    resp['table_data'] = table_data

    return resp


def get_reply_img_list(request, data, resp):
    log = public.logger
    log.info(f'data:{data}')
    form_var = data.get('form_var')
    log.info(f'form_var: {form_var}')
    id = form_var.get('id')
    reply_img = form_var.get('reply_img')
    if not reply_img:
        return err_msg(msg='此反馈无回复图片')
    reply_img = json.loads(reply_img.replace("'", '"'))

    table_data = []
    for data in reply_img:
        table_item = {
            'reply_img': data
        }
        table_data.append(table_item)
    resp['table_data'] = table_data

    return resp

def get_repair_img_list(request, data, resp):
    log = public.logger
    log.info(f'data:{data}')
    form_var = data.get('form_var')
    log.info(f'form_var: {form_var}')
    id = form_var.get('id')
    repair_img = form_var.get('repair_img')
    if not repair_img:
        return err_msg(msg='此报修无图片')
    repair_img = json.loads(repair_img.replace("'", '"'))

    table_data = []
    for data in repair_img:
        table_item = {
            'repair_img': data
        }
        table_data.append(table_item)
    resp['table_data'] = table_data

    return resp
