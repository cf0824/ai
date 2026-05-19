import json

from tieta_api import TietaApi

api = TietaApi()


# 测试充电开关
def ts_charge_open():
    res = api.charge_open('123', True)
    print('res=', res)

    res = api.charge_open('456', False)
    print('res=', res)


# 测试解析属性上报
def ts_unpack_attr_up():
    cmd = '''{
     "msgType": 310,
     "devId": "YJDC12345600",
     "txnNo": "24000",
     "attrList": [{
       "id": "05102001",
       "value": 1,
       "devId": "YJDC12345600"
      }, {
       "id": "05104001",
       "value": 0,
       "devId": "YJDC12345600"
      }, {
       "id": "05105001",
       "value": 0,
       "devId": "YJDC12345600"
      }, {
       "id": "05108001",
       "value": 0,
       "devId": "YJDC12345600"
      }],
     "isFull": 0
    }'''
    data = json.loads(cmd)
    attrList = data.get('attrList', [])
    res = api.unpack_attr_up(attrList)
    print('res=', res)


# 测试设备重启
def ts_eq_restart():
    cmd = api.eq_restart('XYZA12345678')
    print('cmd=', cmd)


def ts_unpack_search_attr_one():
    cmd = """{"msgType":211,"devId":"MMCD12345600","txnNo":"1567508825531","result":1,"resultList":[{"id":"05104001","devId":"MMCD12345601","value":4816}]}"""
    res = api.unpack_search_attr_one(cmd)
    print('res=', res)


if __name__ == "__main__":
    print('test')
    # ts_charge_open()
    # ts_unpack_attr_up()
    # ts_eq_restart()
    ts_unpack_search_attr_one()
