#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  wms_app -> excelUtils.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   excelUtils.py
@Time    :   2024-08-23 16:20
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
import os
import json
from collections import OrderedDict
import xlwt


class XlwtBeautifulExcel:
    def __init__(self, path, sheet_name):
        self.path = path
        self.sheet_name = sheet_name
        self.workbook = xlwt.Workbook()
        self.worksheet = self.workbook.add_sheet(sheet_name)

        # 创建样式对象并保存，避免重复创建
        self.default_style = self.create_default_style()
        self.header_style = self.create_header_style()
        self.set_column_widths_and_row_heights()

    @staticmethod
    def create_default_style():
        """
        创建默认单元格样式
        """
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = '微软雅黑'
        font.size = 12
        font.colour_index = 0  # 黑色

        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN

        fill = xlwt.Pattern()
        fill.pattern = xlwt.Pattern.SOLID_PATTERN
        fill.pattern_fore_colour = 1  # 浅黄色背景

        style.font = font
        style.alignment = alignment
        style.borders = borders
        style.pattern = fill
        return style

    @staticmethod
    def create_header_style():
        """
        创建表头单元格样式
        """
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = '微软雅黑'
        font.size = 13
        font.bold = True  # 加粗
        font.colour_index = 34  # 深蓝色

        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN

        fill = xlwt.Pattern()
        fill.pattern = xlwt.Pattern.SOLID_PATTERN
        fill.pattern_fore_colour = 55  # 亮黄色背景

        style.font = font
        style.alignment = alignment
        style.borders = borders
        style.pattern = fill
        return style

    def insert_value(self, row, start_col, end_col, value):
        """
        在 Excel 的指定行中插入指定值
        """
        for col in range(int(start_col), int(end_col) + 1):
            self.worksheet.write(int(row), col - 1, value, self.default_style)  # xlwt 列索引从 0 开始

    def merge_cells(self, start_row, start_col, end_row, end_col):
        """
        合并单元格
        """
        self.worksheet.merge(start_row, start_col - 1, end_row, end_col - 1)  # xlwt 列索引从 0 开始

    def set_column_widths_and_row_heights(self):
        # 设置列宽
        for col_index in range(100):  # 假设最多有100列
            self.worksheet.col(col_index).width = 256 * 25  # 宽度设置为20个字符

        # 设置行高
        for row_index in range(9999):  # 假设最多有9999行
            self.worksheet.row(row_index).height_mismatch = True
            self.worksheet.row(row_index).height = 256 * 2  # 设置行高为18个字符

    def save(self):
        """
        保存 Excel 文件
        """
        self.workbook.save(self.path)

    def get_style(self):
        return self.default_style  # 返回默认样式

    def get_header_style(self):
        return self.header_style  # 返回表头样式


class ExportExcel(XlwtBeautifulExcel):
    def Json2Excel(self, json_input):
        """
        将 JSON 数据写入 Excel
        """
        json_array = self._load_json_input(json_input)
        self._write_data(json_array)

    @staticmethod
    def _load_json_input(json_input):
        if isinstance(json_input, str) and os.path.isfile(json_input):
            with open(json_input, 'r', encoding="utf-8") as file:
                json_array = json.load(file, object_pairs_hook=OrderedDict)
        elif isinstance(json_input, (dict, list)):
            json_array = json_input
        else:
            json_array = []
        return json_array

    def _write_data(self, json_array):
        # 写入表头
        header = json_array[0].keys() if json_array else []
        for col_index, key in enumerate(header):
            self.worksheet.write(0, col_index, key, self.get_header_style())

        # 写入数据
        for row_index, item in enumerate(json_array, start=1):
            for col_index, key in enumerate(header):
                value = item.get(key, "")
                self.worksheet.write(row_index, col_index, value, self.get_style())
        self.save()
