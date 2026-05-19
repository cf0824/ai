#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：fee.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/4/26 16:04 
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
from admin_app.utils.timeTool import compare_time


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


def add_time_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')


    verify_dict = [
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['time_frame_no', str, True, '时段编号'],
        ['begin_time', str, True, '起始时间'],
        ['end_time', str, True, '结束时间'],
        ['electric_price', str, True, '电价'],
        ['service_fee', str, True, '服务费'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        site_id = form_var.get('site_id')
        standard_name = form_var.get('standard_name')
        fee_no = form_var.get('fee_no')
        time_frame_no = form_var.get('time_frame_no')
        begin_time = form_var.get('begin_time')
        end_time = form_var.get('end_time')
        electric_price = form_var.get('electric_price')
        service_fee = form_var.get('service_fee')
        time_legal = compare_time(begin_time, end_time)
        if not time_legal:
            return err_msg(msg='开始时间需要早于结束时间')


        sql = "select * from s_fee_standard_1 where site_id=%s and fee_no=%s order by time_frame_no"
        args = (site_id, fee_no,)
        fee_standard_info = db.fetchall(sql, args)
        log.info(f'{fee_no}的收费标准信息:{fee_standard_info}')

        if fee_standard_info:
            log.info(f'该编号已有相关配置')
            last_time_frame = fee_standard_info[-1]
            log.info(f'last_time_frame: {last_time_frame}')
            last_time_frame_no = last_time_frame.get('time_frame_no')
            last_end_time = last_time_frame.get('end_time')

            if int(last_time_frame_no) + 1 != int(time_frame_no):
                return err_msg(msg=f'该标准编号最大时段编号为：{last_time_frame_no},请按顺序输入时段编号')
            time_legal_1 = compare_time(str(last_end_time), begin_time)
            if not time_legal_1:
                return err_msg(msg=f'时间段重叠，开始时间早于上个时间区间结束时间：{last_end_time}')
            time_legal_2 = compare_time(begin_time, str(last_end_time))
            if not time_legal_2:
                return err_msg(msg=f'时间段未完全覆盖，开始时间晚于上个时间区间结束时间：{last_end_time}')
            data = {
                'time_frame_no': time_frame_no,
                'site_id': site_id,
                'fee_no': fee_no,
                'standard_name': standard_name,
                'begin_time': begin_time,
                'end_time': end_time,
                'electric_price': electric_price,
                'service_fee': service_fee
            }
            db.insert('s_fee_standard_1', data)
        elif not fee_standard_info:
            log.info(f'该编号没有相关配置，新建')
            if int(time_frame_no) != 1:
                return err_msg(msg=f'该配置首次创建，时段编号应为1')
            data1 = {
                'time_frame_no': time_frame_no,
                'site_id': site_id,
                'fee_no': fee_no,
                'standard_name': standard_name,
                'begin_time': begin_time,
                'end_time': end_time,
                'electric_price': electric_price,
                'service_fee': service_fee
            }
            db.insert('s_fee_standard_1', data1)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def update_time_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')


    verify_dict = [
        ['id', int, True, '主键id'],
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['time_frame_no', str, True, '时段编号'],
        ['begin_time', str, True, '起始时间'],
        ['end_time', str, True, '结束时间'],
        ['electric_price', str, True, '电价'],
        ['service_fee', str, True, '服务费'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        standard_name = form_var.get('standard_name')
        fee_no = form_var.get('fee_no')
        time_frame_no = form_var.get('time_frame_no')
        begin_time = form_var.get('begin_time')
        end_time = form_var.get('end_time')
        electric_price = form_var.get('electric_price')
        service_fee = form_var.get('service_fee')
        time_legal = compare_time(begin_time, end_time)
        if not time_legal:
            return err_msg(msg='开始时间需要早于结束时间')


        sql = "select * from s_fee_standard_1 where site_id=%s and fee_no=%s order by time_frame_no"
        args = (site_id, fee_no,)
        fee_standard_info = db.fetchall(sql, args)
        log.info(f'{fee_no}的收费标准信息:{fee_standard_info}')


        data = {
            'time_frame_no': time_frame_no,
            'site_id': site_id,
            'fee_no': fee_no,
            'standard_name': standard_name,
            'begin_time': begin_time,
            'end_time': end_time,
            'electric_price': electric_price,
            'service_fee': service_fee
        }
        db.update('s_fee_standard_1', data, {'id': id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def add_elec_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['grads_no', str, True, '时段编号'],
        ['electric_down', str, True, '梯度下限'],
        ['electric_up', str, True, '梯度上限'],
        ['electric_price', str, True, '电价'],
        ['service_fee', str, True, '服务费'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        site_id = form_var.get('site_id')
        standard_name = form_var.get('standard_name')
        fee_no = form_var.get('fee_no')
        grads_no = form_var.get('grads_no')
        electric_down = form_var.get('electric_down')
        electric_up = form_var.get('electric_up')
        electric_price = form_var.get('electric_price')
        service_fee = form_var.get('service_fee')

        if float(electric_down) > float(electric_up):
            return err_msg(msg='梯度下限不能大于梯度上限')

        sql = "select * from s_fee_standard_2 where site_id=%s and fee_no=%s order by grads_no"
        args = (site_id, fee_no,)
        fee_standard_info = db.fetchall(sql, args)
        log.info(f'{fee_no}的收费标准信息:{fee_standard_info}')

        if fee_standard_info:
            log.info(f'该编号已有相关配置')
            last_grads = fee_standard_info[-1]
            log.info(f'last_grads: {last_grads}')
            last_grads_no = last_grads.get('grads_no')
            last_electric_up = last_grads.get('electric_up')

            if int(last_grads_no) + 1 != int(grads_no):
                return err_msg(msg=f'该标准编号最大梯度编号为：{last_grads_no},请按顺序输入梯度编号')

            if float(last_electric_up) > float(electric_down):
                return err_msg(msg=f'梯度重叠，梯度下限低于上个梯度的上限：{last_electric_up}')

            if float(last_electric_up) < float(electric_down):
                return err_msg(msg=f'梯度区间未完全覆盖，梯度下限高于上个梯度的上限：{last_electric_up}')
            data = {
                'grads_no': grads_no,
                'site_id': site_id,
                'fee_no': fee_no,
                'standard_name': standard_name,
                'electric_down': electric_down,
                'electric_up': electric_up,
                'electric_price': electric_price,
                'service_fee': service_fee
            }
            db.insert('s_fee_standard_2', data)
        elif not fee_standard_info:
            log.info(f'该编号没有相关配置，新建')
            if int(grads_no) != 1:
                return err_msg(msg=f'该配置首次创建，梯度编号应为1')
            if float(electric_down) != 0:
                return err_msg(msg=f'该配置首次创建，电量区间请从0开始')
            data1 = {
                'grads_no': grads_no,
                'site_id': site_id,
                'fee_no': fee_no,
                'standard_name': standard_name,
                'electric_down': electric_down,
                'electric_up': electric_up,
                'electric_price': electric_price,
                'service_fee': service_fee
            }
            db.insert('s_fee_standard_2', data1)

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def update_elec_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    form_var['electric_price'] = float(form_var.get('electric_price'))
    form_var['service_fee'] = float(form_var.get('service_fee'))
    form_var['electric_down'] = float(form_var.get('electric_down'))
    form_var['electric_up'] = float(form_var.get('electric_up'))
    verify_dict = [
        ['id', int, True, '主键id'],
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['grads_no', str, True, '时段编号'],
        ['electric_down', float, True, '梯度下限'],
        ['electric_up', float, True, '梯度上限'],
        ['electric_price', float, True, '电价'],
        ['service_fee', float, True, '服务费'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        standard_name = form_var.get('standard_name')
        fee_no = form_var.get('fee_no')
        grads_no = form_var.get('grads_no')
        electric_down = form_var.get('electric_down')
        electric_up = form_var.get('electric_up')
        electric_price = form_var.get('electric_price')
        service_fee = form_var.get('service_fee')

        if float(electric_down) >= float(electric_up):
            return err_msg(msg='梯度下限需小于梯度上限')

        sql = "select * from s_fee_standard_2 where site_id=%s and fee_no=%s order by grads_no"
        args = (site_id, fee_no,)
        fee_standard_info = db.fetchall(sql, args)
        log.info(f'{fee_no}的收费标准信息:{fee_standard_info}')

        data = {
            'grads_no': grads_no,
            'site_id': site_id,
            'fee_no': fee_no,
            'standard_name': standard_name,
            'electric_down': electric_down,
            'electric_up': electric_up,
            'electric_price': electric_price,
            'service_fee': service_fee
        }
        db.update('s_fee_standard_2', data, {'id': id})

        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

def del_time_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['id', int, True, '主键id'],
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['time_frame_no', str, True, '时段编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        fee_no = form_var.get('fee_no')
        grads_no = form_var.get('grads_no')
        sql = "select * from s_order_info where fee_type=%s and fee_no=%s and state=%s"
        args = ('1', fee_no, '1',)
        fee_order_info = db.fetchall(sql, args)
        log.info(f'使用该收费标准的订单:{fee_order_info}')
        if fee_order_info:
            return err_msg(msg='目前有订单正在使用该标准，删除会无法计费')

        db.delete('s_fee_standard_1', {'id': id})
        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise


def del_elec_fee_standard(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['id', int, True, '主键id'],
        ['site_id', int, True, '站点id'],
        ['fee_no', str, True, '收费标准编号'],
        ['grads_no', str, True, '时段编号']
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)
    try:
        db = MySQLDB()
        id = form_var.get('id')
        site_id = form_var.get('site_id')
        fee_no = form_var.get('fee_no')
        grads_no = form_var.get('grads_no')
        sql = "select * from s_order_info where fee_type=%s and fee_no=%s and state=%s"
        args = ('2', fee_no, '1',)
        fee_order_info = db.fetchall(sql, args)
        log.info(f'使用该收费标准的订单:{fee_order_info}')
        if fee_order_info:
            return err_msg(msg='目前有订单正在使用该标准，删除会无法计费')

        db.delete('s_fee_standard_2', {'id': id})
        return resp
    except Exception as e:
        log.error(e, exc_info=True)
        raise

    