import decimal
import json
import os
import time
from datetime import datetime
from random import sample
from string import digits, ascii_letters
# from . import MyLog
from app.utils import MyLog
from wechatpayv3 import WeChatPay, WeChatPayType

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings')
django.setup()
from app.models import *
from SmartChargeBD.settings import WX_XCX_APP_ID, WX_PAY_MCH_ID, WX_PAY_PRIVATE_KEY, WX_PAY_CERT_SERIAL_NO, \
    WX_PAY_APIV3_KEY, WX_PAY_NOTIFY_URL

# 微信支付商户号（直连模式）或服务商商户号（服务商模式，即sp_mchid)
MCHID = WX_PAY_MCH_ID

# 商户证书私钥
# with open('./apiclient_key.pem') as f:
#     PRIVATE_KEY = f.read()
PRIVATE_KEY = WX_PAY_PRIVATE_KEY

# 商户证书序列号
CERT_SERIAL_NO = WX_PAY_CERT_SERIAL_NO

# API v3密钥， https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_2.shtml
APIV3_KEY = WX_PAY_APIV3_KEY

# APPID，应用ID或服务商模式下的sp_appid
APPID = WX_XCX_APP_ID

# 回调地址，也可以在调用接口的时候覆盖
NOTIFY_URL =  WX_PAY_NOTIFY_URL

# 微信支付平台证书缓存目录，减少证书下载调用次数
# 初始调试时可不设置，调试通过后再设置，示例值：'./cert'
CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cert')

# 日志记录器，记录web请求和回调细节
# LOGGER = MyLog.getLogger("wx_pay")

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

# 接入模式：False=直连商户模式，True=服务商模式
PARTNER_MODE = False

# 代理设置，None或者{"https": "http://10.10.1.10:1080"}，详细格式参见https://docs.python-requests.org/zh_CN/latest/user/advanced.html
PROXY = None

# 是否解冻剩余未分资金
UNFREEZE_UNSPLIT = False



def get_wxpay():
    # 初始化
    wxpay = WeChatPay(
        wechatpay_type=WeChatPayType.MINIPROG,  # 小程序
        mchid=MCHID,
        private_key=PRIVATE_KEY,
        cert_serial_no=CERT_SERIAL_NO,
        apiv3_key=APIV3_KEY,
        appid=APPID,
        notify_url=NOTIFY_URL,
        cert_dir=CERT_DIR,
        logger=log,
        partner_mode=PARTNER_MODE,
        proxy=PROXY)
    return wxpay


def create_order(open_id, order_id, amount, desc):
    log.info(f'创建微信充值订单')
    log.info(f'open_id: {open_id}, order_id: {order_id}')
    wxpay = get_wxpay()
    log.info(f'amount: {amount}, desc: {desc}')
    # out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    out_trade_no = order_id
    # description = 'demo-description'
    description = desc
    # amount = 1
    payer = {'openid': open_id}
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        payer=payer,
        settle_info={'profit_sharing': True}
    )
    result = json.loads(message)
    log.info(f'充值结果：{code}-{result}')
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = str(int(time.time()))
        noncestr = 'demo-nocestr'
        package = 'prepay_id=' + prepay_id
        paysign = wxpay.sign([APPID, timestamp, noncestr, package])
        signtype = 'RSA'
        return True, {
            'appId': APPID,
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': paysign
        }
    else:
        return False, result.get('code')


# 订单退款
def order_refund(transaction_id, order_id, out_trade_no, amount, total_money):
    log.info(f'处理退款：{transaction_id}，退款金额：{amount}, 微信订单金额：{total_money}')
    log.info(f'支付订单号：{out_trade_no}，退款单号：{order_id}')
    try:
        wxpay = get_wxpay()
        code, message = wxpay.refund(
            out_trade_no=out_trade_no,
            out_refund_no=order_id,
            amount={'refund': amount, 'total': total_money, 'currency': 'CNY'},
            transaction_id=transaction_id
        )
        log.info(f'退款结果：code: {code}, message: {message}')
        """
        code: 200, message: {"amount":{"currency":"CNY","discount_refund":0,"from":[],"payer_refund":2,"payer_total":2,"refund":2,"settlement_refund":2,"settlement_total":2,"total":2},"channel":"ORIGINAL","create_time":"2021-11-23T10:40:06+08:00","funds_account":"AVAILABLE","out_refund_no":"123","out_trade_no":"202111230000000022","promotion_detail":[],"refund_id":"50301100102021112314717040330","status":"SUCCESS","transaction_id":"4200001166202111236002088102","user_received_account":"支付用户零钱"}
    
        """
        message = json.loads(message)
        if code == 200 and message.get('refund_id'):
            return True, message.get('refund_id')
        return False, ''
    except Exception as e:
        log.error(f'退款错误：{e}', exc_info=True)
        return False



#

# 微信提现

def new_transfer_batch(appid, out_bill_no, transfer_scene_id, openid, transfer_amount, transfer_remark, transfer_scene_report_infos, user_name=None, notify_url=None, user_recv_perception=None):
    from wechatpayv3.type import RequestType
    wxpay = get_wxpay()

    params = {}
    if appid:
        params.update({'appid': appid})
    else:
        raise Exception('appid is not assigned')
    if out_bill_no:
        params.update({'out_bill_no': out_bill_no})
    else:
        raise Exception('out_batch_no is not assigned')
    if transfer_scene_id:
        params.update({'transfer_scene_id': transfer_scene_id})
    else:
        raise Exception('transfer_scene_id is not assigned!')
    if openid:
        params.update({'openid': openid})
    else:
        raise Exception('openid is not assigned!')
    if transfer_amount:
        params.update({'transfer_amount': transfer_amount})
    else:
        raise Exception('transfer_amount is not assigned!')
    if transfer_remark:
        params.update({'transfer_remark': transfer_remark})
    else:
        raise Exception('transfer_remark is not assigned!')
    if transfer_scene_report_infos:
        params.update({'transfer_scene_report_infos': transfer_scene_report_infos})
    else:
        raise Exception('transfer_scene_report_infos is not assigned!')

    cipher_data = False

    # params.update({'appid': appid or wxpay._appid})
    if notify_url or wxpay._notify_url:
        params.update({'notify_url': notify_url or wxpay._notify_url})
    if user_name:
        params.update({'user_name': user_name})
    if user_recv_perception:
        params.update({'user_recv_perception': user_recv_perception})

    path = '/v3/fund-app/mch-transfer/transfer-bills'
    log.info(f'微信转账请求参数： {params}')
    return wxpay._core.request(path, method=RequestType.POST, data=params, cipher_data=cipher_data), params

def wx_cash_out(order_id, desc, amount, open_id):
    try:
        log.info(f'处理微信提现：{order_id}, {desc}, {amount}, {open_id}')
        # wxpay = get_wxpay()
        transfer_scene_id = '1011'
        transfer_scene_report_infos = [{
            "info_type": "赔付原因",
            "info_content": "用户钱包提现"
        }]
        notify_url = 'https://smartcharge.pinmait.com/api/wx-transfer-money-notice'
        # res = wxpay.transfer_batch(order_id, desc, desc, amount, 1, detail)
        # out_bill_no, transfer_scene_id, openid, transfer_amount, transfer_remark, transfer_scene_report_infos, user_name = None, notify_url = None, user_recv_perception = None
        res, paras = new_transfer_batch(APPID, order_id, transfer_scene_id, open_id, amount, '用户提现', transfer_scene_report_infos, notify_url=notify_url)
        return res, paras
    except Exception as e:
        log.error(f'请求微信提现出现错误：{e}')


# 获取微信提现结果
def new_transfer_query_out_detail_no(out_bill_no):
    """商家明细单号查询明细单
    :param out_detail_no: 商家明细单号，示例值：x23zy545Bd5436
    :param out_batch_no: 商家批次单号，示例值：plfk2020042013
    """
    wxpay = get_wxpay()
    if out_bill_no:
        path = '/v3/fund-app/mch-transfer/transfer-bills/out-bill-no/%s' % (out_bill_no)
    else:
        raise Exception('out_bill_no or out_batch_no is not assigned')
    return wxpay._core.request(path)
def get_wx_cash_out_result(order_id):
    log.info(f'获取微信提现结果：{order_id}')
    # wxpay = get_wxpay()
    out_bill_no = order_id
    # out_detail_no = order_id
    # res = wxpay.transfer_query_out_batch_no(out_batch_no,need_query_detail=True)
    res = new_transfer_query_out_detail_no(out_bill_no=out_bill_no)
    log.info(f'微信提现结果：{res}')
    # print('res=', res)
    return res

# 分账
def wx_profit_share(tran_order_id, order_id, transaction_id, amount, receivers):
    """
    微信分账: 钱包充值、卡充值、订单在线支付
    :param out_order_no: 商户订单号
    :return:
    """
    log.info(f'开始分账: {tran_order_id}, 分账金额：{amount}')
    wxpay = get_wxpay()

    # 通过商户订单号查所需信息

    receivers = [{'type':'PERSONAL_OPENID', 'account':'oDya55Xu1AJs0XH62PbCA85nhlMI', 'amount': amount, 'description':'分给商户A'}]
    res = wxpay.profitsharing_order(
        transaction_id=transaction_id,
        out_order_no=order_id,
        receivers=receivers,
        unfreeze_unsplit=UNFREEZE_UNSPLIT
    )
    log.info(f'分账结果：{res}')
    return res

def return_profit_share(order_id, amount):

    log.info(f'分账回退: {order_id}, 回退金额：{amount}')
    wxpay = get_wxpay()

    # 通过商户订单号查所需信息


    res = wxpay.profitsharing_return(
        out_return_no='R' + datetime.now().strftime('%Y%m%d%H%M%S'),
        return_mchid='1584191351',
        amount=amount,
        description='分账回退',
        order_id=order_id,
    )
    return res

def add_receiver(receiver_data):
    wxpay = get_wxpay()
    account_type = receiver_data['account_type']
    account = receiver_data['account']
    relation_type = receiver_data['relation_type']
    name = receiver_data['name']
    res = wxpay.profitsharing_add_receiver(account_type, account, relation_type)
    return res

def del_receiver(receiver_data):
    wxpay = get_wxpay()
    account_type = receiver_data['account_type']
    account = receiver_data['account']
    relation_type = receiver_data['relation_type']
    name = receiver_data['name']
    res = wxpay.profitsharing_delete_receiver(account_type, account, relation_type)
    return res

if __name__ == '__main__':
    from app.utils import get_seq

    transaction_id = "4200002757202505239500648336"
    order_id = "WF_PAY_2025_000081"
    amount = int(7)
    order_refund(transaction_id, order_id, order_id, amount, 10)

    # order_id = get_seq.Get_SeqNo("PROFIT_SHARE_WX")
    # tran_order_id = 'WF_PAY_2025_000040'
    # res = wx_profit_share(tran_order_id, order_id)
    # print(res)
    # receiver_data = {
    #     'account_type': 'PERSONAL_OPENID',
    #     'account': 'oDya55Xu1AJs0XH62PbCA85nhlMI',
    #     'relation_type': 'USER',
    #     'name': '张三'
    # }
    # res = add_receiver(receiver_data)
    # # res = del_receiver(receiver_data)
    # print(res)
    # order_return = '30000702342025051788139496488'
    # amount = 30
    # res = return_profit_share(order_return, amount)
    # print(res)