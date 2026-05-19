"""
铁塔api
"""
import copy
import time
import json
# from .base import BaseApi
from base import BaseApi


class TietaBaseApi(BaseApi):

    def __init__(self):
        super().__init__()

    # 获取消息流水号(13位时间戳)
    def _getTxnNo(self):
        return str(int(time.time() * 1000))

    # 从报文里取流水号
    def _getTxnNoFromCmd(self, cmd):
        data = json.loads(cmd)
        txnNo = data.get('txnNo')
        return txnNo

    # 通用发送命令
    def _send_cmd(self, msgType, devId, options=None, txnNo=None):
        txnNo = txnNo or self._getTxnNo()
        data = {
            'msgType': msgType,
            'devId': devId,
            'txnNo': txnNo
        }
        options = options or {}
        data.update(options)
        return json.dumps(data)

    # 通用回应确认
    def _reply_ack(self, msgType, devId, txnNo, result=True):
        options = {
            'result': 1 if result else 0
        }
        return self._send_cmd(msgType, devId, options, txnNo)

    # 远程控制
    def _ctrl_post(self, devId, paramList):
        msgType = 500
        options = {
            'paramList': paramList
        }
        return self._send_cmd(msgType, devId, options)

    # 远程控制_单个设备
    def _ctrl_post_one(self, devId, k, v):
        paramList = [
            {
                'id': k,
                'devId': 'ALL',
                'value': v
            }
        ]
        return self._ctrl_post(devId, paramList)

    # 配置查询
    def _search_attr(self, devId, paramList):
        msgType = 210
        options = {
            'paramList': paramList
        }
        return self._send_cmd(msgType, devId, options)

    # 配置查询_单个设备
    def _search_attr_one(self, devId, k):
        paramList = [
            {
                'id': k,
                'devId': devId
            }
        ]
        return self._search_attr(devId, paramList)

    # 通用解析
    def _unpack_cmd(self, cmd):
        tmp_data = json.loads(cmd)
        msgType = tmp_data.get('msgType'),
        devId = tmp_data.get('devId'),
        txnNo = tmp_data.get('txnNo')
        options = tmp_data
        del options['msgType']
        del options['devId']
        del options['txnNo']
        return msgType, devId, txnNo, options

    def _unpack_cmd_options(self, cmd):
        msgType, devId, txnNo, options = self._unpack_cmd(cmd)
        return options

    def _unpack_ctrl_post_one(self, cmd):
        options = self._unpack_cmd_options(cmd)
        try:
            paramList = options.get('paramList')
            result = paramList[0]['result']
            if result == 1:
                return True
            return False
        except:
            return False


class TietaApi(TietaBaseApi):
    # todo 信号id转参数名（键）
    single2arg = {
        '05102001': 'charge_state',
        '05104001': 'v100',
        '05105001': 'a100',
        '05108001': 'kwh1000'

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

    # todo 解析属性上报
    def unpack_attr_up(self, cmd):
        _msgType, _devId, _txnNo, _options = self._unpack_cmd(cmd)
        attrList = _options.get('attrList', [])
        res = []
        for attr in attrList:
            id = attr.get('id')
            value = attr.get('value')
            devId = attr.get('devId')
            k = self.single2arg.get(id, '')
            value_tran_tmp = self.value_trans.get(k, {})
            v = value_tran_tmp.get(str(value), str(value))
            res.append(
                {
                    'devId': devId,
                    'k': k,
                    'v': v
                }
            )
        return res

    # 回复确认
    def reply_ack(self, oldMsgType, devId, txnNo, result=True):
        # 回复处理对应函数名
        reply_kv = {
            '110': 111,
            '310': 311,
            '410': 411,
        }
        msgType = reply_kv.get(str(oldMsgType))
        if not msgType:
            return ''
        return self._reply_ack(msgType, devId, txnNo, result)

    # # 充电桩设备开关
    # def eq_open(self, devId, open=True):
    #     k = '05202001'
    #     if open:
    #         v = 2
    #     else:
    #         v = 1
    #     return self._ctrl_post_one(devId, k, v)
    #
    # # 充电桩设备重启
    # def eq_restart(self, devId):
    #     k = '05202001'
    #     v = 0
    #     return self._ctrl_post_one(devId, k, v)

    # # 解析设备重启
    # def unpack_eq_restart(self, cmd):
    #     result = self._unpack_ctrl_post_one(cmd)
    #     return result

    # # 充电开关
    # def charge_open(self, devId, open=True):
    #     k = '05201001'
    #     if open:
    #         v = 1
    #     else:
    #         v = 0
    #     return self._ctrl_post_one(devId, k, v)

    # # 解析充电开关
    # def unpack_charge_open(self, cmd):
    #     result = self._unpack_ctrl_post_one(cmd)
    #     return result
