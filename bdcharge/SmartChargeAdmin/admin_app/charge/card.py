#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：card.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/7/10 9:51 
@Description :
'''
import json
import os

import requests
from admin_app.sys import public
import datetime
from admin_app.tools import handle

from admin_app.utils.params_validate import validate_params
from admin_app.tools.ErrorMsg import err_msg
from admin_app.utils.dbFunc import MySQLDB
from admin_app.utils.appCom import generate_download_file
from admin_app.utils.excelTool import ExcelTools
import xlrd


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


def add_card(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['card_no', str, True, '卡号'],
        # ['sn', str, True, 'sn'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        card_no = form_var.get('card_no')
        card_sn = form_var.get('card_sn')
        bind_state = form_var.get('bind_state')
        is_enable = form_var.get('is_enable')
        data = {
            'card_no': card_no,
            'card_sn': card_sn,
            'bind_state': bind_state,
            'is_enable': is_enable,
            'create_time': datetime.datetime.now()
        }
        db.insert('s_card_library', data)



        return resp
    except Exception as e:
        log.info(f'添加卡失败：{e}', exc_info=True)
        raise


def update_card(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['card_no', str, True, '卡号'],
        # ['sn', str, True, 'sn'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        card_no = form_var.get('card_no')
        # card_sn = form_var.get('card_sn')
        # bind_state = form_var.get('bind_state')
        is_enable = form_var.get('is_enable')
        data = {
            'card_no': card_no,
            'is_enable': is_enable,
            'update_time': datetime.datetime.now()
        }
        db.update('s_card_library', data, {'card_no': card_no})

        return resp
    except Exception as e:
        log.info(f'修改卡失败:{e}', exc_info=True)
        raise


# 下载学生信息导入模板
def  download_card_import_temp(request, data, resp):
    file_name = "批量导入卡.xlsx"
    output_file = public.localhome + "filetemplate/" + file_name
    return generate_download_file(output_file, file_name, resp, is_remove=False)


def import_card_batch(request, data, resp):
    log = public.logger
    form_var = data.get('form_var', {})
    # OrgID = form_var.get('ORG', '')
    # log.info(f"form_var{form_var}")
    log.info(f"批量上传卡号")

    try:
        file_id = form_var.get('file_id')
        if not file_id:
            return err_msg(msg=f"上传文件不能为空")
        file_id = file_id[0]

        db = MySQLDB()

        # 查询文件信息表
        sql = "select file_name,md5_name,content_type from sys_fileup where file_id='%s' and state='1'"
        file_info = db.fetchone(sql, (file_id,))
        if not file_info:
            return err_msg(msg=f'文件[{file_id}]不存在')

        file_name = file_info.get('file_name')
        file_md5name = file_info.get('md5_name')
        file_contenttype = file_info.get('content_type')

        local_filename = "/app/fileup/" + file_md5name
        if not os.path.exists(local_filename):
            return err_msg(msg=f'文件[{local_filename}]已过期')

        # 打开 Excel 文件
        excel_file = xlrd.open_workbook(local_filename)

        # 获取第一个工作表
        sheet = excel_file.sheet_by_index(0)

        # 获取行数
        total_count = sheet.nrows
        log.info(f"总行数: {total_count}")
        success_count = 0
        failure_count = 0

        # 遍历每一行
        for excel_row in range(2, total_count):
            cell_value = sheet.cell(excel_row, 0).value
            card_no = str(cell_value).strip()  # 移除空格
            if '.0' in card_no:
                card_no.replace('.0', '')

            sel_card_exist = "select * from s_card_library where card_no=%s"
            card_exist = db.fetchone(sel_card_exist, (card_no,))
            if card_exist:
                failure_count = failure_count + 1
                log.info(f"第{excel_row}行,卡号[{card_no}]重复！")
                continue
            try:
                data = {
                    'card_no': card_no,
                    'create_time': datetime.datetime.now(),
                    'bind_state': '0',
                    'is_enable': '1'
                }
                db.insert('s_card_library', data)
                success_count += 1
            except Exception as e:
                return err_msg(msg=f"第{excel_row}行,卡号[{card_no}]入库异常！{str(e)}")
        log.info(f"本次处理数据[{total_count}]条, 成功登记[{success_count}]条, 重复未登记[{failure_count}]条")
        # 或者手动删除引用
        del sheet
        del excel_file

        # 在处理完文件后尝试删除它
        try:
            os.remove(local_filename)
            log.info(f"Deleted local file: {local_filename}")
        except OSError as e:
            log.error(f"Error occurred while deleting file: {e.strerror}")
            raise Exception(f"数据处理异常:{str(e)}")
        return resp

    except Exception as e:
        log.error(f"错误：{e}")
        raise Exception(f"数据处理异常:{str(e)}")

def user_bind_card(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    log.info(f'传入的数据form_var: {form_var}')
    form_data = data.get('form_data', {})
    log.info(f'form_data: {form_data}')

    verify_dict = [
        ['user_id', int, True, '用户id'],
        ['phone_number', str, True, '手机号'],
        ['card_num', str, True, '卡号'],
    ]
    not_valid, valid_info = validate_params(verify_dict, form_var)
    if not not_valid:
        return err_msg(msg=valid_info)
    log.info(valid_info)

    try:
        db = MySQLDB()

        card_num = form_var.get('card_num')
        user_id = form_var.get('user_id')
        phone_number = form_var.get('phone_number')
        user_name = form_var.get('user_name')
        # is_enable = form_var.get('is_enable')

        # sql_for_user_info = """
        #             select * from s_user_info where user_id = %s
        #         """
        # user_info = db.fetchone(sql_for_user_info, (user_id,))
        # if user_info.get('phone_number') is None:
        #     return err_msg(msg=f'该用户个人信息未完善')
        #
        # phone_number = user_info.phone_number
        # if tel != phone_number:
        #     resp['tips'] = '手机号错误'
        #     resp['success'] = False
        #     return resp

        sql_for_bind_info = """
            select * from s_cards_info where user_id = %s
        """
        bind_info = db.fetchone(sql_for_bind_info, (user_id,))
        if bind_info:
            return err_msg(msg=f'该用户已绑过卡')

        sql_for_card_info = """
            select * from s_card_library where card_no = %s
        """
        card_info = db.fetchone(sql_for_card_info, (card_num,))
        if card_info is None:
            return err_msg(msg=f'找不到此卡号')
        bind_state = card_info.get('bind_state')
        if bind_state == '1':
            return err_msg(msg=f'该卡已绑定')

        # 绑定电卡
        db.update('s_user_info', {'card_num': card_num}, {'user_id': user_id})
        data = {
            'bind_state': '1',
            'bind_time': datetime.datetime.now()
        }
        db.update('s_card_library', data, {'card_no': card_num})


        data1 = {
            'card_sn': card_info.get('card_sn'),
            'card_num': card_info.get('card_no'),
            'user_id': user_id,
            'user_name': user_name,
            'tel': phone_number,
            'money': 0,
            'gift_money': 0,
            'use_state': '0',
            'state': '1'
        }
        db.insert('s_cards_info', data1)

        return resp
    except Exception as e:
        log.info(f'修改卡失败:{e}', exc_info=True)
        raise


# 处理微信支付成功，电卡充值
def wx_card_recharge_success(request, data, resp):
    log = public.logger
    log.info(f'总数据data:{data}')
    form_var = data.get('form_var', {})
    out_trade_no = form_var.get('order_id')
    transaction_id = form_var.get('transaction_id')

    try:
        db = MySQLDB()
        sql = "select * from s_wx_tran_card_detail where order_id=%s order by id desc"
        order = db.fetchone(sql, (out_trade_no,))
        if not order:
            log.info(f'电卡充值失败，未找到原充值记录 -->out_trade_no：{out_trade_no}')
            return err_msg(msg=f'电卡充值失败，未找到原充值记录')
        order_state = order.get('state')
        order_id = order.get('id')
        if order_state != '1':
            log.info(f'电卡充值失败，原充值记录已成功 -->out_trade_no：{out_trade_no}')
            return err_msg(msg=f'电卡充值失败，原充值记录已成功')
        if order.get('change_type') != 'in':
            log.info(f'电卡充值失败，当前只处理充值，不处理退款 -->change_type：{order.get("change_type")}')
            return err_msg(msg=f'电卡充值失败，原充值记录已成功')

        order_user_id = order.get('user_id')
        log.info(f'order -->order_id:{order_id},order_state：{order_state}, order_user_id:{order_user_id}')

        data = {
            'finish_time': datetime.datetime.now(),
            'transaction_id': transaction_id,
            'state': '3',
            'remark': '后台人工处理'
        }
        db.update('s_wx_tran_card_detail', data, {'id': order_id})

        # 插入电卡充值记录
        data = {
            'card_sn': order.get('card_sn'),
            'card_num': order.get('card_num'),
            'card_tel': order.get('card_tel'),
            'recharge_type': 'online',
            'transaction_id': transaction_id,
            'recharge_money': order.get('change_money'),
            'user_id': order.get('user_id'),
            'remark': '后台人工补账',
            'create_time': datetime.datetime.now()
        }
        db.insert('s_card_recharge_detail', data)

        # 增加卡余额
        # 保证变更金额为正浮点数
        change_money = float(order.get('change_money'))
        change_money = abs(change_money)

        wheresql = ""
        if order.get('card_num'):
            wheresql = wheresql + "card_num = '%s' and " % order.get('card_num')
        if order.get('card_sn'):
            wheresql = wheresql + "card_sn = '%s' and " % order.get('card_sn')
        if not wheresql:
            log.info(f'增加卡余额失败，原记录卡号为空-->card_num：{order.get("card_num")}， card_sn：{order.get("card_sn")}')
            return err_msg(msg=f'电卡充值失败，原记录卡号为空')
        wheresql = wheresql + " 1=1"
        sql = "select money from s_cards_info where %s" % wheresql
        log.info(sql)
        cardinfo = db.fetchone(sql)
        if not cardinfo:
            log.info(f'增加卡余额失败，未找到卡余额表记录 -->{sql}')
            return err_msg(msg=f'电卡充值失败，未找到卡余额表记录')
        change_money = change_money + cardinfo.get('money')
        db.update('s_cards_info', {'money':change_money}, {'id': cardinfo.get('id')})

        return resp
    except Exception as e:
        log.error(f'电卡充值失败:{e}', exc_info=True)
        return err_msg(msg=f'电卡充值失败,{str(e)}')
    