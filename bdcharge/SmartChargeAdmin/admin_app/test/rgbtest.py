# -*- coding: utf-8 -*-

import sys
import os
import time
import datetime
import serial
import threading

send_data_mutex = threading.Lock()
def sender_putc(data):
    send_data_mutex.acquire()
    ser.write(data)
    # for itm in data:
    #     ser.write(itm)
    #     time.sleep(0.01)
    send_data_mutex.release()

#接收数据
def sender_getc(size):
    return ser.read(size)

ser = serial.Serial(bytesize=8, parity='N', stopbits=1, timeout=5, write_timeout=5)

def str_to_hex(s):
    return r"/x"+r'/x'.join([hex(ord(c)).replace('0x', '') for c in s])

def hex_to_str(s):
    return ''.join([chr(i) for i in [int(b, 16) for b in s.split(r'/x')[1:]]])

def rgbtest( data ):
    ser.port = "COM7"
    ser.baudrate = 19200
    if ser.is_open == False:
        ser.open()
        print('打开串口成功：', ser)
        ser.timeout = 1000

    # data=b'/x67/x65/x74/x20/x73/x6E/0D'  #"GET SN"
    # print(data)
    # sender_putc(data)

    data= data +"\r"
    print('发送数据：',data )
    sender_putc( data.encode() )
    # print('发送数据成功', datetime.datetime.now())
    time.sleep(0.2)  #延迟3秒
    # print('开始接收数据', datetime.datetime.now())
    recv=sender_getc(12)
    print(recv)

if __name__ == '__main__':
    rgbtest("GET SN")
    while True:
        rgbtest( "GET CH00.RGB" )
        time.sleep(1)
