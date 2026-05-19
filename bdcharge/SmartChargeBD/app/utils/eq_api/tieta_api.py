"""
铁塔api
"""
import copy
import datetime
import decimal
import time
import json
# from .base import BaseApi
from .base import BaseApi


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        super(MyJSONEncoder, self).default(o)


class TietaApi(BaseApi):
    # todo 信号id转参数名（键）
    single2arg = {
        '05102001': 'charge_state',
        '05104001': 'v100',
        '05105001': 'a100',
        '05108001': 'kwh1000',

        '05101001': 'charge_attrs',  # 充电上报参数

    }
    # todo 属性值转换
    value_trans = {
        # 充电口状态
        'charge_state': {
            '0': '0',  # 待连接
            '1': '1',  # 空闲
            '2': '2',  # 充电中
            '3': '3',  # 已充满
            '4': '4',  # 异常
            '5': '5',  # 掉线
        }
    }

    def __init__(self):
        super().__init__()

    # 获取消息流水号(13位时间戳)
    def _get_txn_no(self):
        return str(int(time.time() * 1000))

    # 从报文里取流水号
    def get_txn_no_from_cmd(self, cmd):
        data = json.loads(cmd)
        txnNo = data.get('txnNo')
        return txnNo

    # 通用发送命令
    def _send_cmd(self, msgType, devId, options=None, txnNo=None):
        txnNo = txnNo or self._get_txn_no()
        data = {
            'msgType': msgType,
            'devId': devId,
            'txnNo': txnNo
        }
        options = options or {}
        data.update(options)
        return json.dumps(data, cls=MyJSONEncoder)

    # 通用回应确认
    def _reply_ack(self, msgType, devId, txnNo, result=True, add_options=None):
        options = {
            'result': 1 if result else 0
        }
        if add_options:
            options.update(add_options)
        return self._send_cmd(msgType, devId, options, txnNo)

    # 通用解析
    def _unpack_cmd(self, cmd):
        tmp_data = json.loads(cmd)
        msgType = tmp_data.get('msgType')
        devId = tmp_data.get('devId')
        txnNo = tmp_data.get('txnNo')
        options = tmp_data
        del options['msgType']
        del options['devId']
        del options['txnNo']
        return msgType, devId, txnNo, options

    def _unpack_cmd_options(self, cmd):
        msgType, devId, txnNo, options = self._unpack_cmd(cmd)
        return options

    # 远程控制
    def ctrl_post(self, devId, paramList):
        msgType = 500
        options = {
            'paramList': paramList
        }
        return self._send_cmd(msgType, devId, options)

    # 远程控制_单个设备
    def ctrl_post_one(self, devId, k, v, addParamList):
        paramList = [
            {
                'id': k,
                'devId': 'ALL',
                'value': v
            }
        ]
        if addParamList:
            paramList = paramList + addParamList
        # 批量添加devid
        for item in paramList:
            if 'devId' not in item:
                item['devId'] = 'ALL'
        return self.ctrl_post(devId, paramList)

    # 解析远程控制_单个设备
    def unpack_ctrl_post_one(self, cmd):
        options = self._unpack_cmd_options(cmd)
        try:
            paramList = options.get('paramList')
            result = paramList[0]['result']
            if result == 1:
                return True
            return False
        except:
            return False

    # 配置查询
    def search_attr(self, devId, paramList):
        msgType = 210
        options = {
            'paramList': paramList
        }
        return self._send_cmd(msgType, devId, options)

    # 配置查询_单个设备
    def search_attr_one(self, devId, k):
        paramList = [
            {
                'id': k,
                'devId': devId
            }
        ]
        return self.search_attr(devId, paramList)

    # 解析配置查询_单个设备
    def unpack_search_attr_one(self, cmd):
        options = self._unpack_cmd_options(cmd)
        result = options.get('result')
        if not result:
            return None
        resultList = options.get('resultList')
        try:
            value = resultList[0]['value']
            return value
        except:
            return None

    # 接收属性上报
    def recv_attr_up(self, cmd):
        attr_info_list = []
        _msgType, _devId, _txnNo, _options = self._unpack_cmd(cmd)
        print('_msgType, _devId, _txnNo, _options=',_msgType, _devId, _txnNo, _options)
        attrList = _options.get('attrList', [])
        for attr in attrList:
            id = attr.get('id')
            value = attr.get('value')
            devId = attr.get('devId')
            if not devId:
                devId = _devId
            k = self.single2arg.get(id, '')
            value_tran_tmp = self.value_trans.get(k, None)
            if value_tran_tmp:
                v = value_tran_tmp.get(str(value), str(value))
            else:
                v = value
            attr_info_list.append(
                {
                    'devId': devId,
                    'k': k,
                    'v': v
                }
            )
        # reply_cmd = self._reply_ack(311, _devId, _txnNo, True)
        # options = {
        #     'attrList': [{
        #         'id': '05101001',
        #         'value': account
        #     }]
        # }

        # options = {
        #     'result': 1
        # }
        reply_cmd = self._reply_ack(311, _devId, _txnNo, True)
        # reply_cmd = self._send_cmd(311, _devId, options=options, txnNo=_txnNo)
        return attr_info_list, reply_cmd

    # 接收交易上报
    def recv_tran_up(self, cmd, account=0):
        attr_info_list = []
        _msgType, _devId, _txnNo, _options = self._unpack_cmd(cmd)
        print('_msgType, _devId, _txnNo, _options=', _msgType, _devId, _txnNo, _options)
        attrList = _options.get('attrList', [])
        for attr in attrList:
            id = attr.get('id')
            value = attr.get('value')
            devId = attr.get('devId')
            if not devId:
                devId = _devId
            k = self.single2arg.get(id, '')
            value_tran_tmp = self.value_trans.get(k, None)
            if value_tran_tmp:
                v = value_tran_tmp.get(str(value), str(value))
            else:
                v = value
            attr_info_list.append(
                {
                    'devId': devId,
                    'k': k,
                    'v': v
                }
            )
        # reply_cmd = self._reply_ack(311, _devId, _txnNo, True)
        options = {
            'attrList': [{
                'id': '05101001',
                'value': account
            }]
        }
        reply_cmd = self._send_cmd(321, _devId, options, _txnNo)
        return attr_info_list, reply_cmd

    # todo 接收告警上报
    def recv_warn_up(self, cmd):
        warn_info_list = []
        _msgType, _devId, _txnNo, _options = self._unpack_cmd(cmd)
        alarmList = _options.get('alarmList', [])
        for item in alarmList:
            warn_info_list.append({
                'devId': '',
                'warn_time': item.get('alarmTime'),
                'v': ''  # todo 转换
            })
        reply_cmd = self._reply_ack(411, _devId, _txnNo, True)
        return warn_info_list, reply_cmd

    # 接收登录上报
    def recv_login_up(self, cmd):
        login_info = {}
        _msgType, _devId, _txnNo, _options = self._unpack_cmd(cmd)

        login_info['iccid'] = _options.get('iccid')
        login_info['devType'] = _options.get('devType')
        login_info['devAttr'] = _options.get('devAttr')
        login_info['devElecAttr'] = _options.get('devElecAttr')
        login_info['softVersion'] = _options.get('softVersion')
        login_info['hardVersion'] = _options.get('hardVersion')
        login_info['protocolVersion'] = _options.get('protocolVersion')
        login_info['devList'] = _options.get('devList')

        # 对时
        timestamp = int(time.time())
        reply_cmd = self._reply_ack(111, _devId, _txnNo, True, add_options={'timestamp': timestamp})
        return login_info, reply_cmd

    # 回复确认501
    def reply_501_ack(self, devId, txnNo, success=True):
        reply_cmd = self._reply_ack(502, devId, txnNo, success)
        return reply_cmd
