# -*- coding: utf-8 -*-
# coding:utf-8
#################################################################
# 模块名称: Tcp长连接，转https通讯
# 版    本: V1.0
# 作    者: 栗天正
# 创建日期: 2024-10-27
#################################################################
import sys
import os
import time
import json
import datetime
import socket
import select
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)
from utils import pubpara
from utils import publog
from utils import MyLog
from utils.redis_package.handle_cmd import get_cmd_S2T, get_cmd_detail, Byte2Hex, Hex2Byte
from utils.redis_package import cmdFunc

from tools.MessageApi import Message

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger
log.info(f'充电桩通讯机：启动')

# 终端->服务器 的请求
def Proc_T2S(sock_client, data):
    message = Message(log)
    dict_data = message.Message_parsing(data)
    terminal_address = dict_data['address_region'].get('address_term_r')
    hexcmd = Byte2Hex(data)

    AFN = dict_data['app_region'].get('app_region_function_code')
    Fn = dict_data['app_region']['Data_unit_identification'].get('Fn')
    pseq_rseq = dict_data['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')

    try:
        name1 = pubpara.Function_Name[AFN]['FF']
        name2 = pubpara.Function_Name[AFN][Fn]
        # log.info(f'终端:{terminal_address}->服务器,{hexcmd}==>{name1}-{name2},帧序号:{pseq_rseq}')
        log.info(f'终端{terminal_address}->服务器,{hexcmd}==>{name1}-{name2}')
    except KeyError:
        # log.info(f'终端:{terminal_address}->服务器,{hexcmd}==>未匹配到接口名称, AFN:{AFN},Fn:{Fn},帧序号:{pseq_rseq}')
        log.info(f'终端{terminal_address}->服务器,{hexcmd}==>未匹配到接口名称, AFN:{AFN},Fn:{Fn}')

    # 获取该充电桩最近的一次命令
    key = 'term_last_' + terminal_address
    res = cmdFunc.get_last_term_cmd(key)
    if res == hexcmd:
        # log.info(f'设备：{terminal_address},命令重复：{hexcmd}')
        return

    key = {
        'head': 'cmdT2S'
    }
    value = {
        'cmd': hexcmd
    }
    cmdFunc.add_command(key, value)

    # 更新该设备最新命令
    key = 'term_last_' + terminal_address
    value = hexcmd
    cmdFunc.add_last_term_cmd(key, value)
    # log.info(f'T2S cmd 命令已添加')

    # 获取到term_no, 将term_no更新到pubpara.regist_connect_term中
    sock_client_upd(inputs, terminal_address, sock_client)


# 服务端->终端 的请求
def Proc_S2T(t_term_no, senddata):
    message = Message(log)
    hexcmd = Hex2Byte(senddata)

    dict_data = message.Message_parsing(hexcmd)
    terminal_address = dict_data['address_region'].get('address_term_r')

    AFN = dict_data['app_region'].get('app_region_function_code')
    Fn = dict_data['app_region']['Data_unit_identification'].get('Fn')
    pseq_rseq = dict_data['app_region']['app_region_SEQ'].get('PSEQ_RSEQ')

    try:
        name1 = pubpara.Function_Name[AFN]['FF']
        name2 = pubpara.Function_Name[AFN][Fn]
        # log.info(f'服务器:{t_term_no}={terminal_address}->终端,{senddata}==>{name1}-{name2},帧序号:{pseq_rseq}')
        log.info(f'服务器->终端{t_term_no},{senddata}==>{name1}-{name2}')
    except KeyError:
        # log.info(f'服务器->终端{t_term_no},{senddata}==>未匹配到接口名称, AFN:{AFN},Fn:{Fn},帧序号:{pseq_rseq}')
        log.info(f'服务器->终端{t_term_no}=,{senddata}==>未匹配到接口名称, AFN:{AFN},Fn:{Fn}')
    # 获取发送对象
    regist_connect = pubpara.regist_connect_term.get(t_term_no) # 通过终端号找连接字典
    if not regist_connect:
        log.info(f'根据终端号[{t_term_no}]无法查找到socket句柄')
        # sock_src.send('sendfail'.encode())
        return
    sock_client = regist_connect.get('sock_client')
    try:
        ip, port = sock_client.getpeername()

        # log.info(f'开始发送命令[{ip},{port}],sock={str(sock_client)},cmd={hexcmd}')
        sock_client.send(hexcmd)
        # log.info(f'发送命令完毕')

    except Exception as x:
        log.error("select error. %s" % str(x), exc_info=True)
        # sock_src.send('senderror'.encode())

# socket句柄删除
def sock_client_del(inputs, sock_client):
    try:
        regist_connect_old = pubpara.regist_connect_sock.get(sock_client)
        if regist_connect_old:
            pubpara.regist_connect_term.pop(regist_connect_old.get('term_no'))

        pubpara.regist_connect_sock.pop(sock_client)
    except:
        pass
    try:
        inputs.remove(sock_client)
    except:
        pass
    try:
        sock_client.close()
    except:
        pass

# socket句柄更新
def sock_client_upd(inputs, term_no, sock_client):
    upd_flag = False
    # 注册的连接字典：
    regist_connect = {
        'sock_client': sock_client,  # socket句柄
        'term_no': term_no,  # 终端编号
        'last_time': datetime.datetime.now()  # 最后通讯时间
    }

    # 如果一个终端编号原来有链接，把原来的关掉，用最新的。
    regist_connect_old = pubpara.regist_connect_term.get(term_no)
    if regist_connect_old and regist_connect_old.get('sock_client') != sock_client:
        sock_client_old = regist_connect_old.get('sock_client')
        try:
            sock_client_old.close()
        except:
            pass
        pubpara.regist_connect_term.pop(term_no)
        pubpara.regist_connect_sock.pop(sock_client_old)
        inputs.remove(sock_client_old)
        upd_flag = True

    # 把最开始连接进来 没有term_no时的socket句柄字典删除
    regist_connect_old = pubpara.regist_connect_term.get(sock_client)
    if regist_connect_old and regist_connect_old.get('term_no') != term_no:
        pubpara.regist_connect_term.pop(sock_client)
        inputs.remove(sock_client)
        upd_flag = True

    # 再新增一个
    pubpara.regist_connect_sock[sock_client] = regist_connect   # 通过socket句柄找字典
    pubpara.regist_connect_term[term_no] = regist_connect   # 通过终端找字典
    if upd_flag or sock_client == term_no:
        inputs.append(sock_client)

    # log.info('-----------------------------')
    # log.info(f'regist_connect_sock:{len(pubpara.regist_connect_sock)},{str(pubpara.regist_connect_sock)}')
    # log.info(f'regist_connect_term:{len(pubpara.regist_connect_term)},{str(pubpara.regist_connect_term)}')
    # log.info(f'inputs:{len(inputs)},{str(inputs)}')
    # log.info('-----------------------------')

# socket句柄清理, 间隔X秒执行一次
def sock_client_clear(inputs):
    regist_connect_sock_new = {}
    for item in pubpara.regist_connect_sock.keys():
        regist_connect = pubpara.regist_connect_sock.get(item)
        diff_second = (datetime.datetime.now() - regist_connect.get('last_time')).seconds
        # log.info(f'{diff_second} > {pubpara.client_quittime}?')
        if diff_second > pubpara.client_quittime:
            # socket链接在指定时间内未响应，退出
            sock_client_old = regist_connect.get('sock_client')
            pubpara.regist_connect_term.pop(regist_connect.get('term_no'))
            inputs.remove(sock_client_old)
            try:
                sock_client_old.close()
            except:
                pass
        else:
            regist_connect_sock_new[item] = pubpara.regist_connect_sock[item]
    pubpara.regist_connect_sock = regist_connect_sock_new
    # 打印一下，都有哪些连接，调试使用。
    log.info(f'当前终端连接数：%s' % len(pubpara.regist_connect_sock))
    for item in pubpara.regist_connect_sock:
        log.info(f'当前终端连接明细-->：%s' % str(item))

if __name__ == "__main__":
    # log, fh = publog.loger_init(pubpara.log_name)
    HOST = '0.0.0.0'
    PORT = pubpara.listen_port
    LISTENNUM = pubpara.listen_maxnum
    BUFSIZ = pubpara.recvbuff_size

    # Create a TCP/IP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
    server.setblocking(False)  # 非阻塞模式

    # Bind the socket to the port
    server_address = (HOST, PORT)
    # print('starting up on %s port %s' % server_address)
    server.bind(server_address)

    # Listen for incoming connections
    server.listen(LISTENNUM)

    # Sockets from which we expect to read
    inputs = [server]

    # mycont= 1
    while inputs:
        # mycont = mycont + 1

        # Wait for at least one of the sockets to be ready for processing
        # log.info('waiting for the next event')
        # 开始select 监听, 对input_list 中的服务器端server 进行监听
        # 一旦调用socket的send, recv函数，将会再次调用此模块
        #  检测是否有已经关闭的连接，在inputs和outputs中去掉
        for item in inputs:
            # print(datetime.datetime.now().strftime("%H:%M:%S.%f"), 'item in=', item, type(item), 'fileno()=', item.fileno())
            if item.fileno() == -1:
                inputs.remove(item)
        try:
            readable, writable, exceptional = select.select(inputs, [], [], 0.2)
            # log.info(f'readable={readable}, writable={writable}, exceptional={exceptional}')
        except Exception as e:
            log.error("select error. %s" % str(e), exc_info=True)
            log.info("inputs=[%s]" % inputs)
            time.sleep(1)

        # Handle inputs
        # 循环判断是否有客户端连接进来, 当有客户端连接进来时select 将触发
        for s in readable:
            try:
                # 判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
                # 表示有新用户来连接
                if s is server:
                    # A "readable" socket is ready to accept a connection
                    connection, client_address = s.accept()
                    # print('connection from %s' % str(client_address) )
                    # log.info('connection from %s' % str(client_address))

                    # 开发跟踪使用，生产关掉
                    # for item in inputs:
                    #     print(datetime.datetime.now().strftime("%H:%M:%S.%f"), 'item in=', item, type(item), 'fileno()=', item.fileno())
                    # this is connection not server
                    connection.setblocking(0)
                    # 将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                    sock_client_upd(inputs, connection, connection)
                else:
                    # 有老用户发消息, 处理接受
                    # 由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(input_list), 客户端发送消息将触发
                    # 所以判断是否是客户端对象触发
                    try:
                        data = s.recv(BUFSIZ)
                    except Exception as ex:
                        log.error('s.recv error! %s' % str(ex))
                        if 'Bad file descriptor' in str(ex):
                            sock_client_del(inputs, s)
                            continue
                    # 客户端未断开
                    if not data:
                        # 客户端断开了连接, 将客户端的监听从input列表中移除
                        log.info('closing %s' % str(client_address))
                        # Stop listening for input on the connection
                        sock_client_del(inputs, s)
                    else:
                        try:
                            ip, port = s.getpeername()
                        except:
                            ip, port = '', ''

                        # log.info(f'接收到{ip},{port},报文:{data}')
                        # log.info(f'data=,{type(data)}, data')
                        Proc_T2S(s, data)

            except Exception as e:
                log.error("system error. %s" % str(e), exc_info=True)

        # 获取所有 服务器->终端 的命令的键
        cmds = get_cmd_S2T()
        # if len(cmds) != 0:
            # log.info(f'命令列表:{cmds},counts:{len(cmds)}')
        for cmd in cmds:  # 这里的cmd是键
            try:
                cmd_detail = get_cmd_detail(cmd)
                # log.info(f'指令详情：{cmd_detail}, 类型：{type(cmd_detail)}')
                term_no = cmd_detail.get('term_no')
                send_data = cmd_detail.get('cmd')
                Proc_S2T(term_no, send_data)
            except Exception as e:
                log.error("system error. %s" % str(e), exc_info=True)


        # Handle "exceptional conditions"
        # 处理异常的情况
        for s in exceptional:
            try:
                log.info('exception condition on', s.getpeername())
                # Stop listening for input on the connection
                inputs.remove(s)
                s.close()
            except Exception as e:
                try:
                    log.error("%s Exception %s " % (s.getpeername(), str(e)), exc_info=True)
                except:
                    log.error("%s Exception %s " % ('error', str(e)), exc_info=True)

        # 清理长时间未使用的socket链接
        try:
            if not pubpara.last_clear_time:
                pubpara.last_clear_time = datetime.datetime.now()
            if (datetime.datetime.now() - pubpara.last_clear_time).seconds > pubpara.div_clear_time:
                sock_client_clear(inputs)
                pubpara.last_clear_time = datetime.datetime.now()
        except Exception as e:
            log.error("sock_client_clear error. %s" % str(e), exc_info=True)

        # 打印一下句柄情况，方便查找原因
        # if mycont > 30:
        #     mycont = 1
            # log.info(f'regist_connect_sock:{len(pubpara.regist_connect_sock)},{str(pubpara.regist_connect_sock)}')
            # log.info(f'regist_connect_term:{len(pubpara.regist_connect_term)},{str(pubpara.regist_connect_term)}')

        # if fh: # 清一下句柄，方便切换日期时日志的更换。
        #     fh.close()
        #     log.removeHandler(fh)
        time.sleep(0.1)  # 每次循环有点儿小间隔，让CPU歇息一下下。
