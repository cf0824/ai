#coding:utf-8
# -*- coding: utf-8 -*-
# cython: language_level=3
from distutils.core import setup
from Cython.Build import cythonize
import json
import datetime

ht_item= {'prd_name': '单项', 'prd_num': '123', 'prd_hardversion': '321', 'prd_pcbversion': '2222', 'prd_shellinfo': '22', 'prd_macinfo': ''}
print('ht_item=', ht_item)
print(ht_item.get('prd_name'))



