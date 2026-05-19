#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：tcp_socket.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/16 15:30 
@Description :
'''
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import json


class TCPHandler():
    def __init__(self):
        # 创建socket对象
        self.socket_client = socket.socket()
        # 连接到服务器
        self.socket_client.connect(("10.155.5.10", 6999))
        self.head = 'TERM'
        self.tail = 'T'


    def tcp_send_msg(self, terminal_address, message):

        # 发送消息
        message = self.head + terminal_address + message + self.tail
        self.socket_client.send(message.encode())
        # 接受消息
        self.socket_client.settimeout(20)
        recv_data = self.socket_client.recv(1024).decode("UTF-8")  # 1024是缓冲区大小，一般就填1024， recv是阻塞式

        return recv_data


if __name__ == "__main__":
    tcp_socket = TCPHandler()
    terminal_address = '10000808'
    data = {
        'data': 'hello world'
    }
    data = json.dumps(data)
    recv_data = tcp_socket.tcp_send_msg(terminal_address, data)
    print(recv_data)

