import re
import sys
import os
import time

import django
import datetime

# 添加当前路径到环境变量中

pwd = os.path.dirname(os.path.realpath(__file__))
pwd = pwd.replace('\charge\shell', '').replace('/charge/shell', '')
# pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings_dev')  # VueSt是自己的项目名称
django.setup()  # 更新配置


from app.utils import handle





handle.account_change(1,1,'in')
