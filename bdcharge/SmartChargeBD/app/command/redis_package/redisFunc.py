#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：redisFunc.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2024/10/22 9:50 
'''
import json
import os

from redis import StrictRedis
from SmartChargeBD.settings import REDISConfig_dev, REDISConfig_local
from app.utils import MyLog

# log = MyLog.log
from app.utils import MyLog


# log = MyLog.log
file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

class RedisDb:
    """
        Redis的工具类
    """

    def __init__(self):
        self.redis = StrictRedis(**REDISConfig_dev, max_connections=2000, decode_responses=True)
        # log.info(f'redis:{self.redis}---{REDISConfig_dev}')
        self.set_value('1', '2')


    def set_value(self, key, value, permanent=False, ex=24 * 60 * 60):
        """
        设置用户缓存
        """
        try:
            if permanent:
                self.redis.set(key, value)
            else:
                self.redis.set(key, value, ex)  # 返回True
        except Exception as e:
            log.error(f"异常原因:{e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def del_value(self, key):
        """
        清空用户缓存
        """
        try:
            self.redis.delete(key)  # 返回1
        except Exception as e:
            log.error(f"异常原因:{e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def get_value(self, key):
        try:
            results = self.redis.get(key)
            return results
        except Exception as e:
            log.error(f"异常原因:{e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def get_keys(self, key="*"):
        try:
            results = self.redis.keys(key)
            return results
        except Exception as e:
            log.error(f"异常原因:{e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def ttl_key(self, key):
        try:
            ttl = self.redis.ttl(key)
            return ttl
        except Exception as e:
            log.error(f"获取缓存过期时间发生异常: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def expire_key(self, key, ex):
        try:
            result = self.redis.expire(key, ex)
            return result
        except Exception as e:
            log.error(f"设置缓存过期时间发生异常: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def check_key_exists(self, key):
        try:
            result = self.redis.exists(key)
            return result
        except Exception as e:
            log.error(f"检查缓存是否存在发生异常: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def flush_db(self):
        try:
            self.redis.flushdb()
        except Exception as e:
            log.error(f"清空当前数据库所有数据发生异常: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def flush_all(self):
        """
        清空当前数据库的所有 key
        """
        try:
            return self.redis.flushall()
        except Exception as e:
            log.error(f"清空所有缓存异常原因: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def increment_value(self, key, amount=1):
        """
        将 key 对应的值增加指定的增量
        """
        try:
            return self.redis.incr(key, amount)

        except Exception as e:
            log.error(f"增加缓存值异常原因: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def decrement_value(self, key, amount=1):
        """
        将 key 对应的值减少指定的增量
        """
        try:
            return self.redis.decr(key, amount)
        except Exception as e:
            log.error(f"减少缓存值异常原因: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

    def close_connection(self):
        """
        关闭 Redis 连接
        """
        try:
            if self.redis:
                self.redis.close()
        except Exception as e:
            log.error(f"关闭连接异常原因: {e}", exc_info=True)
            raise e
        finally:
            self.redis.close()

if __name__ == '__main__':
    redis = RedisDb()
    # key = 'SEQ2'
    # value = {}
    # redis.set_value(key, json.dumps(value), permanent=True)
    # print(redis.get_value(key))
    # redis.del_value(key)
    # value = redis.get_value(key)
    # print(value)
    # value = json.loads(value)
    # if value is not None:
    #     print(f'空字典是None')
    # terminal_address = '10000810'
    # value[terminal_address] = '0000'
    # redis.set_value(key, json.dumps(value), permanent=True)
    # redis.set_value(key, json.dumps({}), permanent=True)
    # int_value = int(value_, 2)
    # print(int_value)
    # binary_value = bin(int_value)[2:]
    # print(binary_value)
    key = 'term_100008081'
    value = '1234567890'
    redis.set_value(key, value, ex=20)
    # value = redis.get_value(key)
    print(value)
    print(type(value))
