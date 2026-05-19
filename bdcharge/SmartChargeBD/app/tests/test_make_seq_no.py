"""
测试批量并发生成流水号是否为重20211119
"""

import os
import django
import sys

# 添加当前路径到环境变量中
pwd = os.path.dirname(os.path.realpath(__file__))
pwd = pwd.replace('\charge\shell', '').replace('/charge/shell', '')
# pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd)  # 这里的路径要根据自己的目录结构来
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartChargeBD.settings_dev')  # VueSt是自己的项目名称
django.setup()  # 更新配置

from multiprocessing import Pool
from app.utils.get_seq_bak import Get_SeqNo, Get_SeqNoV2


def test():
    # 异常
    # seq_no = Get_SeqNo('TEST')
    # 正常
    seq_no = Get_SeqNoV2('TEST')
    print('seq_no=', seq_no)


def main():
    p = Pool(4)
    for i in range(10):
        p.apply_async(test, )
    p.close()
    p.join()


if __name__ == '__main__':
    main()
