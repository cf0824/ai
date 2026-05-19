# 模拟django后台向通讯机发交易
import socket
import datetime


if __name__ == '__main__':
    data = 'TERMFF1234567890{33333333333333333}'
    print(datetime.datetime.now(), data)
    obj = socket.socket()
    obj.connect(('122.51.168.229', 9009))
    obj.sendall(data.encode(encoding='utf-8'))
    ret = str(obj.recv(1024), encoding='utf-8')
    print(datetime.datetime.now(), ret)

