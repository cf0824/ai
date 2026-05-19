#coding:utf-8
# -*- coding: utf-8 -*-

import json
import requests
import random
import datetime

#获取领料情况
def getmaterialinfo():
    postdata={
        "trantype": "getmaterialinfo",  #扫码配对工装获取项目信息
        "MENU_ID":"10",
        "uid":"38",
        "checksum":"11223355",
        'order_id': 'MO1909A080',  # 制令单号
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# getmaterialinfo()

#获取每小时产出情况
def gethourinfo():
    postdata={"trantype":"gethourinfo","order_id":"MO2004A059","plan_id":"JH2003A033","prod_line":"ManLine2","begin_date":"2020-04-22","end_date":"2020-04-22","uid":"111131","checksum":"11223355"}
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# gethourinfo()

#获取当日制程数据
def getprocinfo():
    postdata={
        "trantype": "getprocinfo",
        "MENU_ID":"10",
        "uid":"38",
        "checksum":"11223355",
        "plan_id": "JH2003A005",
        "order_id": "MO2003A033",
        "prod_line": "ManLine2",
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
getprocinfo()

#获取看板数据
def getprojlist():
    postdata={
        "trantype":"getprojlist",
        "uid":"111111",
        "checksum":"11223355",
        "typevalues":['ManLine1','ManLine2','ManLine3']
    }

    postdata = json.dumps(postdata)
    print(datetime.datetime.now(), postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    # url = 'http://192.168.2.240:8000/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(datetime.datetime.now(), req.text)
# getprojlist()

#获取昨日生产情况，今年生产情况
def getcollectinfo():
    postdata={
        "trantype":"getcollectinfo",
        "uid":"57",
        "checksum":"11223355",

        "plan_id": "SB2003A004",
        "order_id": "MO2004A025",
        "prod_line": "ManLine3",

    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    # url = 'http://192.168.2.240:8000/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# getcollectinfo()

#获取项目信息
def getprojinfo():
    postdata={
        "trantype":"getprojinfo",
        "uid":"57",
        "checksum":"11223355"
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    # url = 'http://192.168.2.240:8000/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# getprojinfo()

#根据时间段获取获取项目信息
def getprojectlist():
    postdata={
        "trantype":"getprojectlist",
        "uid":"57",
        "checksum":"11223355",
        "begin_date": "2020-04-01",
        "end_date": "2020-04-11",
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    # url = 'http://192.168.2.240:8000/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# getprojectlist()

#获取各工站生产情况
def getstationinfo():
    postdata={
        "trantype": "getstationinfo",  #扫码配对工装获取项目信息
        "MENU_ID":"10",
        "uid":"38",
        "checksum":"11223355",
        # "plan_id": "SB2003A004",
        "order_id": "MO2004A029",
        "prod_line": "ManLine2",
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url='http://192.168.2.174/api/admin/lqkjmes'
    req = requests.post(url, postdata)
    print(req.text)
# getstationinfo()

#烧录数据上传
def Flash_Burn():
    postdata={
        "trantype": "Flash_Burn",  #烧录数据上传
        "MENU_ID":"10",
        "uid":"38",
        "checksum":"11223355",
        "Info": [
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM11"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM12"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM13"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM14"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM15"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM16"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM17"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM18"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM19"}  # 串口号
            },
            {
                "Board_SN": {"Result": "Pass", "Value": "ff4140036386"},  # SN码
                "Platform_Num": {"Result": "Pass", "Value": "10"},  # 机台名称
                "Test_Result": {"Result": "Pass", "Value": "Pass"},  # 抄表结果
                "Batch_Num": {"Result": "Pass", "Value": "MO2001A031"},  # 制令号
                "chip_id": {"Result": "Pass", "Value": "COM11"}  # 串口号
            }
        ]
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url = 'http://222.89.181.194:7080/api/admin/made'
    req = requests.post(url, postdata)
    print(req.text)
# Flash_Burn()

#抄表测试数据上传
def MeterRead_Test():
    postdata = {
        "trantype":"MeterRead_Test",
        "Info":[
            {"Board_SN":{"Result":"","Value":"11111"},"Platform_Num": {"Result": "Pass", "Value": "2"},"Chip_mmid":{"Result":"","Value":""},"Batch_Num":{"Result":"","Value":"zhiling"},"chip_id":{"Result":"","Value":"1"},"Module_ID":{"Result":"","Value":""},"Test_Result":{"Result":"","Value":"zhiling"},"Fw_Version":{"Result":"","Value":""},"Hw_Version":{"Result":"","Value":""},"Vendor_id":{"Result":"","Value":None}},
            {"Board_SN":{"Result":"","Value":"11112"},"Platform_Num": {"Result": "Pass", "Value": "2"},"Chip_mmid":{"Result":"","Value":""},"Batch_Num":{"Result":"","Value":"zhiling"},"chip_id":{"Result":"","Value":"2"},"Module_ID":{"Result":"","Value":""},"Test_Result":{"Result":"","Value":"zhiling"},"Fw_Version":{"Result":"","Value":""},"Hw_Version":{"Result":"","Value":""},"Vendor_id":{"Result":"","Value":None}}
        ]
    }
    postdata = json.dumps(postdata)
    print(postdata)
    url = 'http://222.89.181.194:7080/api/admin/made'
    req = requests.post(url, postdata)
    print(req.text)
# MeterRead_Test()
