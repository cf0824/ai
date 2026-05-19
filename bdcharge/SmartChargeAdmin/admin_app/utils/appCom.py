#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  SchoolConsumeBackend -> app_com.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   app_com.py
@Time    :   2024/5/14 11:21
@Desc    :
             ┏┓       ┏┓
            ┏┛┻━━━━━━━┛┻┓
            ┃    ☃      ┃
            ┃  ┳┛   ┗┳  ┃
            ┃     ┻     ┃
            ┗━┓       ┏━┛
              ┃       ┗━━━━┓
              ┃ 神兽保佑     ┣┓
              ┃　永无BUG！   ┏┛
              ┗┓┓┏━━━┳┓┏━━━┛
               ┃┫┫   ┃┫┫
               ┗┻┛   ┗┻┛
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
=================================================="""
import base64
import io
import os
import pandas as pd
from admin_cfg.settings import BASE_DIR
from admin_app.utils.exportExcel import ExportExcel
from admin_app.utils.timeUtil import get_current_time_formatted


def df_to_excel_bytes(result, sheet_name='Sheet1', **kwargs):
    """
    将DataFrame转换为Excel文件，并返回包含Excel文件内容的BytesIO对象。

    参数:
    - result: 可以被pandas.DataFrame接受的数据类型，如列表的字典、字典的列表等。
    - sheet_name: Excel文件中的工作表名称，默认为'Sheet1'。
    - **kwargs: 传递给df.to_excel()的其他关键字参数。

    返回:
    - io.BytesIO对象，包含Excel文件的内容。
    """
    # 创建DataFrame
    df = pd.DataFrame(result)
    # 使用字节流存储
    output = io.BytesIO()
    # 保存DataFrame到Excel文件（字节流）
    df.to_excel(output, sheet_name=sheet_name, index=False, **kwargs)
    # 将文件seek位置移动到开头
    output.seek(0)
    # 返回包含Excel文件内容的BytesIO对象
    # 读取字节流内容并编码为Base64
    base64_encoded_data = base64.b64encode(output.getvalue()).decode('utf-8')
    return base64_encoded_data


def generate_download_df_file(base64_encoded_data, filename, response,file_suffix='.xlsx'):
    # 构造响应数据
    response['respcode'] = '125800'
    response['respmsg'] = '导出成功'
    response['filename'] = filename+file_suffix
    response['filetype'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['filedata'] = base64_encoded_data
    return response


# todo: 导出数据到excel
def data_to_excel(data, excel_file_name="", sheet_name="Sheet1"):
    if not excel_file_name:
        excel_file_name = get_current_time_formatted()
    export_path = os.path.join(BASE_DIR, "export_excel")
    if not os.path.exists(export_path):
        os.makedirs(export_path, exist_ok=True)
    excel_file = os.path.join(export_path, excel_file_name)
    ex_tools = ExportExcel(excel_file, sheet_name)
    ex_tools.Json2Excel(data)
    return excel_file


def generate_download_file(output_file_path, filename, response,file_suffix='.xls',is_remove=True):
    try:
        with open(output_file_path, 'rb') as file:
            file_content = file.read()
            # 将文件内容编码为Base64
            base64_encoded_content = base64.b64encode(file_content).decode('utf-8')
            # 删除文件（可选，根据实际需求决定是否删除）
        if is_remove:
            os.remove(output_file_path)
    except FileNotFoundError:
        base64_encoded_content = output_file_path

    # 构造响应数据
    response['respcode'] = '125800'
    response['filename'] = filename+file_suffix
    response['filetype'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['filedata'] = base64_encoded_content
    return response
