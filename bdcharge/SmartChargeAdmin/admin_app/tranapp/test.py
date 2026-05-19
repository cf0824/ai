
from admin_app.tools import handle

import requests



#增删改查配置数据操作主流程
def Main_Proc(request):
    gb=globals()
    return handle.func_handle(request,gb)


def test_set_price_mode(request, data, resp):
    form_var = data.get('form_var', {})
    eq_code = form_var.get('eq_code')
    priceMode = form_var.get('set_attr')
    if not eq_code or not priceMode:
        resp['respcode'] = '999999'
        resp['respmsg'] = '请求参数有误'
    res = requests.post('https://cdz.lianqiaoiot.com/api/test',json={
        'tran_type':"test_set_price_mode",
        'eq_code':eq_code,
        'set_attr':priceMode
    })
    return resp
