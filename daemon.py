#!/opt/venv/bin/python3
# -*- coding: UTF-8
import os
import importlib
from argoss_libs.cache.basic_cache import Cache
from argoss_libs.cache.helpers import decode_from_b
from argoss_libs.cache.helpers import unpickle_data
from celery_tasks import call_method
import json
importlib.import_module('sondes')
importlib.import_module('argoss_libs')
importlib.import_module('.snmp', 'argoss_libs')
importlib.import_module('.cache', 'argoss_libs')
importlib.import_module('.request_manager', 'argoss_libs.snmp')
importlib.import_module('pandas')

__path__ = os.path.abspath(os.path.dirname(__file__))


if __name__ == '__main__':
    """
    Daemon which is listening Redis pool to get methods to execute and passed them to Celery.
    """
    # Initializing Redis cache module
    c = Cache()
    # Start infinite cycle to listen Redis tasks pool
    while True:
        try:
            # Getting Task from Redis tasks pool
            key, data = c.redis.blpop('pool:calls')
            # Unpickle data
            #data = unpickle_data(data)
            data = json.loads(decode_from_b(data))
            method = ''

            # Removing method param passed through command line and parsing method name
            if '-m' in data:
                try:
                    method_klass = importlib.import_module('sondes.check_linux_mem')
                    method = data[data.index('-m') + 1]
                    data.pop(data.index('-m'))
                    data.pop(data.index(method))
                except KeyError as e:
                    print('Error:', e)
            else:
                print('No method value presented')
            # Calling Celery Task to execute method
            call_method.delay(data, method)
        except Exception as e:
            print(e)
