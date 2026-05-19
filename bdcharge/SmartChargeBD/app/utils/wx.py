import requests
import json
import os
from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException
from wechatpy.session.redisstorage import RedisStorage
from redis import Redis
from SmartChargeBD.settings import WX_APP_ID, WX_APP_SECRET
from SmartChargeBD.settings import WX_XCX_APP_ID, WX_XCX_SECRET
from SmartChargeBD.settings import WX_YW_XCX_APP_ID, WX_YW_XCX_SECRET
from SmartChargeBD.settings import REDISConfig_dev
from app.utils import MyLog
from django.http import HttpResponseRedirect

# log = MyLog.log
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger


# 获取access_token
def get_access_token():
    api = f"https://api.weixin.qq.com/cgi-bin/token"
    try:
        with requests.Session() as r:
            data = {
                "grant_type": "client_credential",
                "appid": WX_XCX_APP_ID,
                "secret": WX_XCX_SECRET
            }
            result = r.post(api, data=data)
            res = result.json()
    except Exception as e:
        log.error(e)
        return None
    return res


def get_component_access_token():
    api = f"https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token?component_access_token=COMPONENT_ACCESS_TOKEN"
    try:
        with requests.Session() as r:
            data = {
                "grant_type": "client_credential",
                "appid": WX_XCX_APP_ID,
                "secret": WX_XCX_SECRET
            }
            result = r.post(api, data=data)
            res = result.json()
    except Exception as e:
        log.error(e)
        return None
    return res


def get_user_phone_number(code, access_token):
    url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
    log.info(f'url:{url}')
    try:
        with requests.Session() as r:
            log.info(f'r: {r}')
            data = {
                "code": code
            }
            json_data = json.dumps(data)
            log.info(f"json_data: {json_data}")
            # headers = {"Content-Type": "application/json"}
            result = r.post(url, data=json_data)
            res = result.json()
    except Exception as e:
        log.error(e)
        return None
    return res




# 小程序获取用户授权
def get_user_grant(code):
    user_grant = {}
    api = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_XCX_APP_ID}&secret={WX_XCX_SECRET}&js_code={code}&grant_type=authorization_code"
    log.info(f'api:{api}')
    try:
        # result = requests.get(api)
        with requests.session() as r:
            log.info(f'r:{r}')
            result = r.get(api)
            log.info(f"result:{result}")
            res = result.json()
        print('get_user_grant res=', res)
        log.info('get_user_grant res=', res)
        if not res.get('openid'):
            return None
        user_grant['open_id'] = res.get('openid')
        user_grant['session_key'] = res.get('session_key')
        user_grant['union_id'] = res.get('unionid')
    except Exception as e:
        log.error(f'用户授权错误：{e}', exc_info=True)
        return None
    return user_grant

# {
# "openid":"xxxxxx",
# "session_key":"xxxxx",
# "unionid":"xxxxx",
# "errcode":0,
# "errmsg":"xxxxx"
# }


# 获取运维小程序用户授权
def get_devops_user_grant(code):
    user_grant = {}
    api = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_YW_XCX_APP_ID}&secret={WX_YW_XCX_SECRET}&js_code={code}&grant_type=authorization_code"
    log.info(f'api{api}')
    try:
        # result = requests.get(api)
        with requests.session() as r:
            result = r.get(api, timeout=5)
            res = result.json()
        print('get_user_grant res=', res)
        if not res.get('openid'):
            return None
        user_grant['open_id'] = res.get('openid')
        user_grant['session_key'] = res.get('session_key')
        user_grant['union_id'] = res.get('unionid')
    except:
        return None
    return user_grant


def get_wechat_client():
    redis_url = f"redis://{REDISConfig_dev['host']}:{REDISConfig_dev['port']}/{REDISConfig_dev['db']}"
    # redis_client = Redis.from_url('redis://redis:6379/0')
    redis_client = Redis.from_url(redis_url, password=REDISConfig_dev['password'])
    session_interface = RedisStorage(redis_client, prefix='wechatpy')
    wechat_client = WeChatClient(WX_APP_ID, WX_APP_SECRET, session=session_interface)
    return wechat_client


# 获取微信公众号用户信息
def get_wx_user_info(open_id):
    wx = get_wechat_client()
    user_info = wx.user.get(open_id)
    return user_info



def generate_wxacode(access_token, device_id):
    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(access_token)
    params = {
        "scene": f"pileNum={device_id}",  # 携带设备ID参数
        "page": "pages/Charge/Choosepile",  # 指定跳转页面路径
        "width": 430,
        "check_path": False,
        "is_hyaline": True,
        "env_version": "trial"
    }
    response = requests.post(url, json=params)
    return response.content  # 返回二进制图片数据

def generate_experience_qrcode(access_token, device_id):
    url = "https://api.weixin.qq.com/wxa/get_qrcode"
    params = {
        "access_token": access_token,
        "path": f"pages/Charge/Choosepile?pileNum={device_id}",
        # 体验版专用参数
        # "env_version": "trial"  # 正式版为"release"
    }
    response = requests.get(url, params=params)
    return response.content


def generate_qrcode_safely(access_token, device_id):
    try:
        image_data = generate_wxacode(access_token, device_id)

        # 检查是否为有效图片（微信接口错误时会返回JSON）
        if image_data.startswith(b'{'):
            error_info = json.loads(image_data)
            print(f"生成失败: {error_info.get('errmsg')}")
            return None

        return image_data
    except Exception as e:
        print(f"二维码生成异常: {str(e)}")
        return None




if __name__ == '__main__':
    token = get_access_token()
    print(token)
    # res = get_user_phone_number("1", token)
    token = token.get('access_token')
    print(token)
    result = generate_wxacode(token, '100002')
    # result = generate_experience_qrcode(token, "device_123")
    # print(result)
    if result:
        with open('qrcode_体验版.jpg', 'wb') as f:
            f.write(result)


