#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ChargingPile 
@File    ：db_handle.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/24 11:45 
@Description :
'''
from utils.dbMysql import MysqlCursor
import datetime
# from utils.dbFunc import MySQLDB
import MyLog

log = MyLog.log

class DbCmd:
    """
    对命令操作的方法
    """
    def __init__(self):
        self.db1 = MysqlCursor()



    def insert_cmd_T2S(self, dict_data):
        """
        插入终端向服务器发启的命令
        :param dict_data: 服务器接收的解包后的数据
        :return:
        """
        try:
            data = {
                'cmd': dict_data,
                'create_time': datetime.datetime.now(),
                'send_type': '2',
                'state': '0'
            }
            self.db1.insert('s_cmd_info', data)

        except Exception as e:
            log.error(f'插入T2S_cmd命令出错！[{e}]', exc_info=True)



    def select_cmd_eq(self, eq_code):
        """
        查询命令表中某设备未操作的命令
        :param eq_code: 设备号
        :return:
        """
        try:
            sql1 = "select * from s_cmd_info where eq_code = %s and state = '0' and send_type='1' order by id desc"
            arg1 = (eq_code, )
            result = self.db1.fetchone(sql1, arg1)
            return result


        except Exception as e:
            log.error(f'查询cmd命令出错！[{e}]', exc_info=True)

    def select_cmd(self):
        """
        查询命令表中未操作的命令
        :param eq_code: 设备号
        :return:
        """
        try:
            sql1 = "select * from s_cmd_info where state = '0' order by id desc"
            result = self.db1.fetchone(sql1)
            return result


        except Exception as e:
            log.error(f'查询cmd命令出错！[{e}]', exc_info=True)

    def complete_cmd(self, cmd_id):
        """
        更新命令为：已完成
        :param cmd_id:
        :return:
        """
        try:
            data = {
                'state': '1',
                'handle_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.db1.update('s_cmd_info', data, {'id': cmd_id})

        except Exception as e:
            log.error(f'更新cmd命令出错！[{e}]', exc_info=True)

    def failure_cmd(self, cmd_id):
        """
        更新命令为：失败
        :param cmd_id:
        :return:
        """
        try:
            data = {
                'state': '-1',
                'handle_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.db1.update('s_cmd_info', data, {'id': cmd_id})

        except Exception as e:
            log.error(f'更新cmd命令出错！[{e}]', exc_info=True)

class DbData:
    """
    用来读取数据、插入数据
    """
    def __init__(self):
        self.db2 = MysqlCursor()

    def get_term_password(self, term_addr):
        """
        根据终端地址，获取其密码
        :param term_addr:
        :return:
        """


if __name__ == '__main__':
    db = DbCmd()
    result = db.select_cmd()
    print(result)
