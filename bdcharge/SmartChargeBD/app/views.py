import json

from django.shortcuts import render,HttpResponse
from app.utils import wx_pay
from app.utils import handle
# Create your views here.
from app.utils.wx_pay import log


def code_check(request):
    return render(request, 'eDI7Gjj9T4.txt')

def qr_code_check(request):
    return render(request, 'eDI7Gjj9T4.txt')

def wx_url_check(request):
    return render(request, 'MP_verify_HNQVq1j223OSOfvI.txt')

def wx_QRCode_check(request):
    a = render(request, 'MyxxDGJjhR.txt')
    log.info(f'——————：{a}')
    return render(request, 'MyxxDGJjhR.txt')


def code(request):
    return HttpResponse('请在微信内扫码打开')


# 微信支付成功回调通知
def wx_pay_success_notice(request):
    try:
        log.info('wx_pay_success_notice begin')
        log.info(f'post={request.POST}')
        log.info(f'header={request.META}')
        log.info(f'get={request.GET}')
        log.info(f'body={request.body}')

        headers = {}
        headers.update({'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE')})
        headers.update({'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP')})
        headers.update({'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE')})
        headers.update({'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL')})
        wxpay = wx_pay.get_wxpay()
        result = wxpay.callback(headers=headers, body=request.body)
        log.info(f'微信[支付/退款]成功回调：{result}')
        if result :
            if result.get('event_type') == 'TRANSACTION.SUCCESS':
                resp = result.get('resource')
                appid = resp.get('appid')
                mchid = resp.get('mchid')
                out_trade_no = resp.get('out_trade_no')
                transaction_id = resp.get('transaction_id')
                trade_type = resp.get('trade_type')
                trade_state = resp.get('trade_state')
                trade_state_desc = resp.get('trade_state_desc')
                bank_type = resp.get('bank_type')
                attach = resp.get('attach')
                success_time = resp.get('success_time')
                payer = resp.get('payer')
                amount = resp.get('amount').get('total')
                # TODO: 根据返回参数进行必要的业务处理，处理完后返回200或204
                # 根据商户订单号，判断是电卡充值，还是账户充值
                recharge_type = out_trade_no[0:6]
                log.info(f"recharge_type:{recharge_type}")
                if recharge_type == 'WF_CAR':
                    handle.handle_wx_card_recharge_success(out_trade_no, success_time, transaction_id)
                    # 充值成功直接分账
                    handle.handle_profit_share_create(out_trade_no, transaction_id)
                elif recharge_type == 'WF_PAY':
                    handle.handle_wx_recharge_success(out_trade_no, success_time, transaction_id)
                    handle.handle_profit_share_create(out_trade_no, transaction_id)
                elif recharge_type == 'WF_SUB':
                    handle.handle_wx_order_recharge_success(out_trade_no, success_time, transaction_id)
                log.info('支付回调处理成功')
                return HttpResponse('success')
            elif result.get('event_type') == 'REFUND.SUCCESS':
                # 退款成功
                resp = result.get('resource')
                out_refund_no = resp.get('out_refund_no')
                success_time = resp.get('success_time')
                transaction_id = resp.get('transaction_id')
                out_trade_no = resp.get('out_trade_no')

                refund_type = out_refund_no[0:6]
                if refund_type == 'WF_PAY':
                    handle.handle_wx_refund_success(out_refund_no, success_time)
                elif refund_type == 'CD_REF':
                    handle.handle_wx_order_refund_success(out_trade_no, out_refund_no, success_time, transaction_id)
                # handle.handle_wx_refund_success(out_refund_no, success_time)
                log.info('退款回调处理成功')
                # todo
                res = {
                    "code": "SUCCESS",
                    "message": "成功"
                }
                return HttpResponse(json.dumps(res))
            else:
                log.info('处理失败')
                return HttpResponse('error')
        else:
            log.info('处理失败')
            return HttpResponse('error')
    except Exception as e:
        log.error(f'微信支付消息处理失败：{e}', exc_info=True)

# 微信转账结果回调通知
def wx_transfer_money_success_notice(request):

    log.info('header=', request.META)
    log.info('get=', request.GET)
    log.info('post=', request.POST)
    log.info('body=', request.body)

    headers = {}
    headers.update({'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE')})
    headers.update({'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP')})
    headers.update({'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE')})
    headers.update({'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL')})
    wxpay = wx_pay.get_wxpay()
    result = wxpay.callback(headers=headers, body=request.body)
    log.info(f'微信转账回调通知：{result}')
    if result :
        if result.get('event_type') == 'MCHTRANSFER.BILL.FINISHED':
            # 转账成功
            resp = result.get('resource')
            out_bill_no = resp.get('out_bill_no')
            transfer_bill_no = resp.get('transfer_bill_no')
            state = resp.get('state')
            mch_id = resp.get('mch_id')
            transfer_amount = resp.get('transfer_amount')
            openid = resp.get('openid')
            fail_reason = resp.get('fail_reason')
            create_time = resp.get('create_time')
            update_time = resp.get('update_time')

            handle.handle_wx_transfer_money_success(out_bill_no, transfer_bill_no, state, fail_reason, update_time)

            log.info('提现（转账）回调处理成功')
            # todo
            res = {
                "code": "SUCCESS",
                "message": "成功"
            }
            return HttpResponse(json.dumps(res))
        else:
            log.info('处理失败')
            return HttpResponse('error')
    else:
        log.info('处理失败')
        return HttpResponse('error')