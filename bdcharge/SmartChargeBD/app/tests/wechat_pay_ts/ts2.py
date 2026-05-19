import hashlib
import json
import random
import re
import string
import sys
import os
import time

import django
import datetime

# 添加当前路径到环境变量中
import requests
import xmltodict

pwd = os.path.dirname(os.path.realpath(__file__))
pwd = pwd.replace(r'\charge\tests\wechat_pay_ts', '').replace(r'/charge/tests/wechat_pay_ts', '')
# pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings_real')  # VueSt是自己的项目名称
django.setup()  # 更新配置

from ts import wxpay



# 申请退款
def refund():
    code, message=wxpay.refund(
        out_refund_no='123',
        amount={'refund': 2, 'total': 2, 'currency': 'CNY'},
        transaction_id='4200001166202111236002088102'
    )
    print('code: %s, message: %s' % (code, message))


def GenWxSign(dictdata):
    apikey='WTeEd35sbADaEp9zbqOvkezXzDiKcFfA'
    signstr = ''
    signdictstr = dictdata['xml'].keys()

    signdictlist=[]  #对key值排序
    for item in signdictstr:
        signdictlist.append(item)
    signdictlist.sort()

    for item in signdictlist:  #拼接成字符串
        if item == 'sign':  #验证签名时已经有此字段，要去掉
            continue
        if dictdata['xml'][item]==None or dictdata['xml'][item]=='':
            continue
        signstr = signstr + str(item) + '=' + str(dictdata['xml'][item]) + '&'

    signstr = signstr + 'key=' + apikey  # 拼接API密钥
    print(signstr)
    # 生成数字签名
    fmd5 = hashlib.md5(signstr.encode('utf-8'))  # 将py3中的字符串编码为bytes类型
    mysign = fmd5.hexdigest().upper()
    # print('sign=', mysign)
    return mysign

def wxCashOut(amount,openid,order_id):
    data = {
        'mch_appid': 'wx74cec1a81fb0cc01',
        'mchid': '1616733135',
        'nonce_str': ''.join(random.sample(string.ascii_letters + string.digits, 32)),
        'partner_trade_no': order_id,
        'openid': openid,
        'check_name': 'NO_CHECK',
        'amount': amount,
        'desc': '用户提现',
        # 'spbill_create_ip': '39.106.155.114'
    }
    jsondata = {'xml': data}

    jsondata['xml']['sign'] = GenWxSign(jsondata)
    print(str(jsondata))
    xmlStr = xmltodict.unparse(jsondata)
    api = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
    res = requests.post(api, data=xmlStr.encode(encoding='utf-8'), verify=True,
                        cert=('./apiclient_cert.pem', './apiclient_key.pem'))
    respinfo = res.text
    jsonstr = xmltodict.parse(respinfo)
    jsondata = json.dumps(jsonstr, indent=1)
    result=json.loads(jsondata)['xml']
    print(result)
    return result


if __name__ == '__main__':
    refund()
    # wxCashOut('1', 'oQUYz5AOW6kJSialCLsW1b5XgnJo', '111')