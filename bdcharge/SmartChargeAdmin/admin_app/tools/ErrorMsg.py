ERROR={
    'REQ_PARAMS_ERROR':{
        'respcode':'300100',
        'respmsg':'请求参数有误'
    },
    'OPERA_FAIL':{
        'respcode':'300101',
        'respmsg':'操作失败'
    }
}

def err_msg(code="99999", msg="操作失败"):
    return {
        'respcode': code,
        'respmsg': msg
    }