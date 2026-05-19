#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  SchoolConsumeBackend -> redisFunc.py.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   redisFunc.py.py
@Time    :   2024/5/10 10:58
@Desc    :   数据库连接池和redis连接池的实现
             ┏┓       ┏┓
            ┏┛┻━━━━━━━┛┻┓
            ┃    ☃      ┃
            ┃  ┳┛   ┗┳  ┃
            ┃     ┻     ┃
            ┗━┓       ┏━┛
              ┃       ┗━━━━┓
              ┃ 神兽保佑     ┣┓
              ┃　永无BUG！   ┏┛
              ┗┓┓┏━━━┳┓┏━━━┛
               ┃┫┫   ┃┫┫
               ┗┻┛   ┗┻┛
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
=================================================="""
from redis import StrictRedis
from admin_app.sys import public

log = public.logger

REDISConfig = {
    "host": "122.51.168.229",
    "port": 34013,
    "password": "",
    "db": 0
}


class RedisDb:
    """
        Redis的工具类
    """

    def __init__(self):
        self.db_config = REDISConfig
        self.redis = StrictRedis(**self.db_config, max_connections=2000, decode_responses=True)

    def set_value(self, key, value, ex=24 * 60 * 60):
        """
        设置用户缓存
        """
        try:
            self.redis.set(key, value, ex)  # 返回True
        except Exception as e:
            log.error(f"异常原因:{e}")
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
            log.error(f"异常原因:{e}")
            raise e
        finally:
            self.redis.close()

    def get_value(self, key):
        try:
            results = self.redis.get(key)
            return results
        except Exception as e:
            log.error(f"异常原因:{e}")
            raise e
        finally:
            self.redis.close()

    def get_keys(self, key="*"):
        try:
            results = self.redis.keys(key)
            return results
        except Exception as e:
            log.error(f"异常原因:{e}")
            raise e
        finally:
            self.redis.close()

    def ttl_key(self, key):
        try:
            ttl = self.redis.ttl(key)
            return ttl
        except Exception as e:
            log.error(f"获取缓存过期时间发生异常: {e}")
            raise e
        finally:
            self.redis.close()

    def expire_key(self, key, ex):
        try:
            result = self.redis.expire(key, ex)
            return result
        except Exception as e:
            log.error(f"设置缓存过期时间发生异常: {e}")
            raise e
        finally:
            self.redis.close()

    def check_key_exists(self, key):
        try:
            result = self.redis.exists(key)
            return result
        except Exception as e:
            log.error(f"检查缓存是否存在发生异常: {e}")
            raise e
        finally:
            self.redis.close()

    def flush_db(self):
        try:
            self.redis.flushdb()
        except Exception as e:
            log.error(f"清空当前数据库所有数据发生异常: {e}")
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
            log.error(f"清空所有缓存异常原因: {e}")
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
            log.error(f"增加缓存值异常原因: {e}")
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
            log.error(f"减少缓存值异常原因: {e}")
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
            log.error(f"关闭连接异常原因: {e}")
            raise e
        finally:
            self.redis.close()


