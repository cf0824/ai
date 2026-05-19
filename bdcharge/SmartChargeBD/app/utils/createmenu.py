



import sys
import os
import django

# 添加当前路径到环境变量中
pwd = os.path.dirname(os.path.realpath(__file__))
pwd = pwd.replace(r'\charge\utils', '').replace(r'/charge/utils', '')
sys.path.append(pwd) # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings') # VueSt是自己的项目名称
django.setup()  # 更新配置



from SmartChargeBD.settings import WX_APP_ID, WX_APP_SECRET
from SmartChargeBD.settings import WX_XCX_APP_ID


import json
import logging
import pymysql
import requests

from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException
from wechatpy.session.redisstorage import RedisStorage
from redis import Redis


def createmeun_wx(access_token):
    print("-" * 50)
    print('生成公众号自定义菜单')

    # 生成自定义菜单
    try:
        menudata = {
            "button":[
                {
                    "name": "首页",
                    "type": "miniprogram",
                    "url": "http://mp.weixin.qq.com",
                    "appid": WX_XCX_APP_ID,
                    "pagepath": "pages/Home/index"
                },{
                    "name": "我的订单",
                    "type":"miniprogram",
                    "url":"http://mp.weixin.qq.com",
                    "appid": WX_XCX_APP_ID,
                    "pagepath": "pages/Order/index"

                },
            ],
        }

        url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + access_token
        print(url)
        encode_json = json.dumps(menudata).encode().decode('raw-unicode-escape')
        print('发送数据:%s' % encode_json)
        req = requests.post(url, data=encode_json.encode('utf-8'))  # Use body.encode('utf-8'),不然汉字报错
        # response = urllib.request.urlopen(req)
        print(req.text)
        print('公众号自定义菜单创建成功')
        print("-" * 50)
    except Exception:
        print('公众号自定义菜单创建失败')
        return

# createmeun_wx()

# WX_APP_ID = "wxd04cccbfca6fc70d"
# # 微信公众号secret
# WX_APP_SECRET = "c439b666a3a055a333b51c37f1be6b5d"

def get_wechat_client():
    redis_client = Redis.from_url('redis://redis:6379/0')
    session_interface = RedisStorage(redis_client, prefix='wechatpy')
    wechat_client = WeChatClient(WX_APP_ID, WX_APP_SECRET, session=session_interface)
    return wechat_client



if __name__ == '__main__':
    wx = get_wechat_client()
    access_token = wx.access_token
    print('access_token=', access_token)
    createmeun_wx(access_token)