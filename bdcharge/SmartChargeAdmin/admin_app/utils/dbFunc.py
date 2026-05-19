#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  SchoolConsumeBackend -> dbFunc.py.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   dbFunc.py.py
@Time    :   2024/5/10 10:49
@Desc    :   数据库连接池和redis连接池的实现
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
import sys
from decimal import Decimal

import django
from datetime import datetime, timedelta
from admin_app.sys import public

# 添加当前路径到环境变量中
pwd = os.path.dirname(os.path.realpath(__file__))
# print('pwd=', pwd)
pwd = pwd.replace('\\admin_app\\utils', '').replace('/admin_app/utils', '')
# print('pwd=', pwd)
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_cfg.settings')  # VueSt是自己的项目名称
django.setup()  # 更新配置

log = public.logger
from django.db import connections


class MySQLDB:
    """
        数据的工具类
    """

    def __init__(self, db_alias='default'):
        self.connection = connections[db_alias]
        self.cursor = self.connection.cursor()

    def execute(self, sql, args=()):
        """
        执行sql语句的方法
        """
        if args:
            log.info(f"即将执行的SQL语句：{self.cursor.mogrify(sql, args)}")
        else:
            log.info(f"即将执行的SQL语句：{self.cursor.mogrify(sql)}")
        try:
            if args:
                self.cursor.execute(sql, args)
                log.info(f"sql语句执行成功:{self.cursor.mogrify(sql, args)}")
            else:
                self.cursor.execute(sql)
                log.info(f"sql语句执行成功:{self.cursor.mogrify(sql)}")
        except Exception as e:
            log.error(f"sql语句执行错误:{e}", exc_info=True)
            raise e

    def executemany(self, sql, args=()):
        """
        执行sql语句的方法
        """
        try:
            if args:
                self.cursor.executemany(sql, args)
            else:
                self.cursor.executemany(sql)
            log.info(f"sql语句执行成功, 参数数量: {len(args)}")
        except Exception as e:
            log.error(f"sql语句执行错误:{e}")
            raise e

    @staticmethod
    def __dict_obj_to_str(result_dict):
        """把字典里面的datetime和timedelta对象转成字符串，Decimal对象转换成float"""
        if result_dict:
            result_replace = {
                k: (
                    v.isoformat() if isinstance(v, datetime) else  # datetime转换为字符串
                    str(v.total_seconds()) if isinstance(v, timedelta) else  # timedelta转换为秒数的字符串
                    float(v) if isinstance(v, Decimal) else  # Decimal转换为float
                    v  # 其他类型保持不变
                )
                for k, v in result_dict.items()
            }
            result_dict.update(result_replace)
        return result_dict

    def fetchone(self, sql, args=()):
        """
        执行sql语句并返回单个结果
        """
        try:
            self.execute(sql, args)
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            # 获取结果
            row = self.cursor.fetchone()
            if row:
                result = dict(zip(columns, row))
                return self.__dict_obj_to_str(result)
            return None
        except Exception as e:
            log.error(f"查询单条记录语句错误{sql, args}: {e}")
            raise e

    def fetchall(self, sql, args=()):
        """
        执行sql语句并返回所有结果
        """
        try:
            self.execute(sql, args)
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            rows = self.cursor.fetchall()
            return [self.__dict_obj_to_str(dict(zip(columns, row))) for row in rows]
        except Exception as e:
            log.error(f"查询记录语句错误{sql, args}: {e}")
            raise e

    def insert(self, table, data):
        """
        插入单条数据
        """
        try:
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = 'INSERT INTO {table}({keys}) VALUES ({values});'.format(table=table, keys=keys, values=values)
            params = tuple(data.values())
            self.execute(sql, params)
        except Exception as e:
            log.error(f"{table}插入数据{data}错误: {e}", exc_info=True)
            raise e

    def insert_many(self, table, data_list):
        """
        批量插入数据
        """
        try:
            columns = ", ".join(data_list[0].keys())
            values = ", ".join(["%s"] * len(data_list[0]))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            params_list = [tuple(data.values()) for data in data_list]
            self.executemany(sql, params_list)
        except Exception as e:
            log.error(f"{table}插入数据{data_list}错误: {e}")
            raise e

    def update(self, table, data, query):
        """
        修改数据
        """
        try:
            sets = ', '.join(['{} = %s'.format(k) for k in data])
            condition = ' and '.join(['{} = %s'.format(k) for k in query])
            sql = 'UPDATE {table} SET {sets} WHERE {condition};'.format(table=table, sets=sets, condition=condition)
            args = list(data.values())
            args.extend(list(query.values()))
            self.execute(sql, args)
        except Exception as e:
            log.error(f"{table}更新数据{data}，更新条件{query}错误: {e}")
            raise e

    def delete(self, table, query):
        """
        删除数据
        """
        try:
            condition = ' and '.join(['{} = %s'.format(k) for k in query])
            sql = 'DELETE FROM {table} WHERE {condition};'.format(table=table, condition=condition)
            log.info(f"{table} sql={sql}")
            self.execute(sql, list(query.values()))
        except Exception as e:
            log.error(f"{table}删除数据条件{query}错误: {e}")
            raise e

    def get_last_rowid(self):
        """
        获取最后一条sql语句的id
        """
        return self.cursor.lastrowid

    def call_pro(self, proc_name: str, return_sub: list, *args):
        """
        调用存储过程并处理输出参数
        :param proc_name: 存储过程名称
        :param return_sub: 输出参数名下标
        :param args: 存储过程参数（输入参数）
        :return: 存储过程的输出参数和可能的结果集
        """
        try:
            # 准备调用存储过程
            self.cursor.callproc(proc_name, args)

            data = self.cursor.fetchall()

            params = ",".join("@_{}_{}".format(proc_name, i) for i in return_sub)
            s_result_sql = "select {}".format(params)

            self.cursor.execute(s_result_sql)
            result = self.cursor.fetchone()

            return data, result
        except Exception as e:
            log.error(f"调用存储过程 {proc_name} 时发生错误: {e}")
            return None, None

    def call_function(self, function_name: str, *args):
        """
        调用 MySQL 自定义函数
        :param function_name: 自定义函数名称
        :param args: 自定义函数参数
        :return: 自定义函数的返回值
        """
        try:
            # 构建 SQL 查询字符串，将参数传递给函数
            params = ", ".join(["%s"] * len(args))  # 参数占位符
            sql = f"SELECT {function_name}({params})"
            # 执行查询
            self.cursor.execute(sql, args)
            # 获取结果
            result = self.cursor.fetchone()
            # 如果函数返回单个值，我们只关心第一个元素
        except Exception as e:
            log.error(f"调用自定义函数 {function_name} 时发生错误: {e}")
            return None

        return result
