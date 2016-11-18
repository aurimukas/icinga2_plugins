# -*- coding: UTF-8
"""
    File name: basic_cache.py
    Author: Aurimas NAVICKAS
    Date created: 14/10/2016
    Date last modified: 19/10/2016 11:53
    Python Version: 3.5.2
"""
import redis
import hashlib
from .helpers import pickle_data, unpickle_data, decode_from_b
from ..config import REDIS as redis_cfg

__author__ = "Aurimas NAVICKAS"
__copyright__ = "Copyright 2016, DISIT, La Poste, France"
__version__ = "1"
__email__ = "aurimas.navickas-prestataire@laposte.fr"
__maintainer__ = "Aurimas NAVICKAS"
__status__ = "Dev"
__package__ = 'cache'


class Cache:
    def __init__(self, *args, **kwargs):
        """Cache class initialization"""
        self.host = kwargs['host'] if 'host' in kwargs else redis_cfg['host']
        self.port = kwargs['port'] if 'port' in kwargs else redis_cfg['port']
        self.db = kwargs['db'] if 'db' in kwargs else redis_cfg['db']
        pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db)
        self.redis = redis.Redis(connection_pool=pool, decode_responses=True)

    def delete(self, key):
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print("Error while trying to delete Redis key:", e)
            return False

    def get_value(self, key):
        if key:
            return decode_from_b(self.redis.get(key))

    def set_value(self, key, value, ex=None, px=None, nx=False, xx=False):
        if key and value:
            self.redis.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def set_hash_value(self, key, field, value):
        if key and field:
            self.redis.hset(key, field, value)

    def get_hash_value(self, key, field):
        if key and field:
            return decode_from_b(self.redis.hget(key, field))

    def set_pickled_dict(self, key, value, expire=None, protocol=2):
        if key and value:
            self.set_value(key, pickle_data(value, protocol=protocol), ex=expire)

    def get_pickled_dict(self, key):
        try:
            res = self.redis.get(key)
            return unpickle_data(res)
        except Exception as e:
            print('No Data in Redis', e)
            return False

    def check_if_exists_and_contains(self, key=None, val=None, value_type='hash'):
        exists, contains = False, False
        values_check_types = {'hash': self.is_in_hash,
                              'list': self.is_in_list,
                              'val': self.is_value}

        if key:
            exists = self.redis.exists(key)
            if val and exists:
                contains = values_check_types[value_type](key, val)

        return exists, contains

    def is_in_hash(self, key, value):
        return self.redis.hexists(key, value)

    def is_value(self, key, val):
        return self.redis.get(key) == val

    def is_in_list(self, key=None, value=None):
        if key:
            return self.redis.sismember(key, value)
        return None

    def add_to_set(self, key, *value):
        if key:
            return self.redis.sadd(key, *value)
        return None

    def add_to_list(self, key, *value, append=True):
        if key:
            if append:
                return self.redis.rpush(key, *value)
            else:
                return self.redis.lpush(key, *value)
        return None

    def scan_data(self, match='*'):
        return decode_from_b(self.redis.scan(match=match))

    def delete_keys(self, *keys):
        self.redis.delete(*keys)

    def get_cached_index(self, base_key, label):
        try:
            return self.get_value('%s:indexes:%s' % (base_key, label))
        except Exception:
            return None

    def set_expire(self, key, ex_time=30):
        if key:
            return self.redis.expire(key, ex_time)

    @staticmethod
    def create_hashed_key(hash_string):
        """Creates a hash key string from given string using md5"""
        return hashlib.md5(hash_string.encode()).hexdigest()
