#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：hardware_api.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/12/31 12:07 
@Description :   感觉没必要再封装一层
'''

# import cmdFunc
# from app.shell.handle_cmd2 import req_term
from app.shell import req_term

class HardwareApi:
    def __init__(self):
        # self.terminal_address = terminal_address
        pass
    def get_comm_paras(self, terminal_address):
        paras = {
            'number': '0A01',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_domain(self, terminal_address):
        paras = {
            'number': '0A02',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_signal_strength(self, terminal_address):
        paras = {
            'number': '0A03',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_power_range(self, terminal_address):
        paras = {
            'number': '0A17',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_settle_config(self, terminal_address):
        paras = {
            'number': '0A18',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_pile_status(self, terminal_address):
        paras = {
            'number': '0A19',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_socket_status(self, terminal_address):
        paras = {
            'number': '0A20',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_QRCode(self, terminal_address):
        paras = {
            'number': '0A21',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)


    def get_total_electricity(self, terminal_address):
        paras = {
            'number': '0A41',
            'terminal_address': terminal_address,
            'Special_data': {}
        }
        req_term(paras)

    # ---------------------

    def set_comm_paras(self, terminal_address, Special_data):
        paras = {
            'number': '0401',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_domain(self, terminal_address, Special_data):
        paras = {
            'number': '0402',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_power_range(self, terminal_address, Special_data):
        paras = {
            'number': '0417',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_settle_config(self, terminal_address, Special_data):
        paras = {
            'number': '0418',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_pile_status(self, terminal_address, Special_data):
        paras = {
            'number': '0419',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_socket_status(self, terminal_address, Special_data):
        paras = {
            'number': '0420',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)

    def set_QRCode(self, terminal_address, Special_data):
        paras = {
            'number': '0421',
            'terminal_address': terminal_address,
            'Special_data': Special_data
        }
        req_term(paras)