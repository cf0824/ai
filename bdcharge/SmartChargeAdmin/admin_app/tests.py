# coding:utf-8
# -*- coding: utf-8 -*-
# Create your tests here.

import subprocess
import datetime
import time

postdata={
        "trantype":"getprojlist",
        "uid":"111111",
        "checksum":"11223355",
        "typevalues":['ManLine1','ManLine2','ManLine3','ManLine31']
    }


print(len( str(postdata) ) )

[
    {"name": "order_number", "label": "申请单号"},
    {"name": "tran_date", "label": "申请发起时间"},
    {"name":"user_id", "label":"申请人" },
    {"name": "department", "label": "申请部门"},
    {"name": "start_address", "label": "预计取车地点"},
    {"name": "end_address", "label": "预计还车地点"},
    {"name": "start_date", "label": "预计取车时间"},
    {"name": "end_date", "label": "预计还车时间"},
    {"name": "car_type", "label": "车辆类型"},
    {"name": "car_number", "label": "车牌号码"},
    {"name": "use_person", "label": "使用人"},
    {"name": "car_person", "label": "同乘人员"},
    {"name": "car_mileage", "label": "预计公里数"},
    {"name": "reason", "label": "申请原因"},
    {"name": "status", "label": "当前用车状态"},
    {"name": "apply_state", "label": "当前审批状态"},
    {"name": "remark", "label": "备注说明"},
    {"name": "id", "label": "记录主键"},
]

