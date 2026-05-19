import requests
import json
from urllib.parse import urlencode

from admin_cfg.settings import WX_XCX_APP_ID, WX_XCX_SECRET

from admin_app.utils import MyLog


log = MyLog.log


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


def generate_wxacode(access_token, args):
    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(access_token)
    scene_str = urlencode(args)
    params = {
        "scene": scene_str,  # 携带设备ID参数
        "page": "pages/Charge/Choosepile",  # 指定跳转页面路径
        "width": 430,
        "check_path": False,
        "is_hyaline": True,
        "env_version": "release"
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


def generate_qrcode_safely(access_token, args):
    try:
        image_data = generate_wxacode(access_token, args)

        # 检查是否为有效图片（微信接口错误时会返回JSON）
        if image_data.startswith(b'{'):
            error_info = json.loads(image_data)
            print(f"生成失败: {error_info}")
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
    args = {
        "pileNum": "100002",
        "port": "01"
    }
    result = generate_qrcode_safely(token, args)
    # result = generate_experience_qrcode(token, "device_123")
    if result:
        with open('qrcode_体验版.jpg', 'wb') as f:
            f.write(result)


