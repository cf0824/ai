# 能源管理 定时任务

import sys
import os
import django

# 添加当前路径到环境变量中
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_cfg.settings')  # VueSt是自己的项目名称
django.setup()  # 更新配置

import time
from django.db import connection
import datetime

# 定时任务周期（秒）
TASK_TIME = 10
# 掉线阈时长（秒）
LOST_TIME = 12 * 60


# 获取设备列表
def get_eqp_list():
    cursor = connection.cursor()
    sql = "select equipment_id from e_equipment_info"
    cursor.execute(sql)
    rows = cursor.fetchall()
    eqp_list = []
    for equipment_id, in rows:
        eqp_list.append(equipment_id)
    return eqp_list


def get_eqp_company(eqp):
    cursor = connection.cursor()
    sql = "select gw_id from e_equipment_info where equipment_id=%s"
    cursor.execute(sql, eqp)
    gw_id, = cursor.fetchone()
    if gw_id:
        return gw_id
    return ''


def task_func():
    print('task_func start')
    eqp_list = get_eqp_list()
    cursor = connection.cursor()
    for eqp in eqp_list:
        sql = "select create_time from e_equipment_data where equipment_id=%s order by create_time desc limit 1"
        cursor.execute(sql, eqp)
        row = cursor.fetchone()
        if row and row[0]:
            create_time = row[0]
            utime1 = time.mktime(create_time.timetuple())
            utime2 = time.mktime(datetime.datetime.now().timetuple())
            if utime2 - utime1 > LOST_TIME:
                lost = True
            else:
                lost = False
        else:
            lost = True
        if lost:
            sql = "update e_equipment_info set conn_state='0' where equipment_id=%s and conn_state='1'"
            row = cursor.execute(sql, eqp)
            if row > 0:
                company_id = get_eqp_company(eqp)
                sql = "insert into e_warn_detail(warn_type,warn_desc,warn_level,company_id,create_time,state) value(%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, ('rtu', '设备%s掉线' % eqp, '1', company_id, datetime.datetime.now(), '0'))
        else:
            sql = "update e_equipment_info set conn_state='1' where equipment_id=%s and conn_state='0'"
            row = cursor.execute(sql, eqp)
            if row > 0:
                company_id = get_eqp_company(eqp)
                sql = "insert into e_warn_detail(warn_type,warn_desc,warn_level,company_id,create_time,state) value(%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, ('rtu', '设备%s上线' % eqp, '1', company_id, datetime.datetime.now(), '0'))


if __name__ == '__main__':
    while True:
        task_func()
        time.sleep(TASK_TIME)
