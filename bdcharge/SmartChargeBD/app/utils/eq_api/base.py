"""
BaseApi
"""

import random


class BaseApi:
    def __init__(self):
        pass

    # 临时
    def get_seq_no(self):
        return str(random.randint(1000000, 9999999))