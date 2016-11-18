#!/opt/venv/bin/python3
# -*- coding: UTF-8
import importlib
json = importlib.import_module('json')
os = importlib.import_module('os')
sys = importlib.import_module('sys')
hashlib = importlib.import_module('hashlib')
time = importlib.import_module('time')
basic_cache = importlib.import_module('argoss_libs.cache.basic_cache')
helper = importlib.import_module('.helpers', 'argoss_libs.cache')

TOTAL_MAX_TIME = 50  # MAX Function execution time 15s
TAP = 0.1            # Make a a call each 0.2s to check results


def create_hashed_key(hash_string):
    """Creates a hash key string from given string using md5"""
    return hashlib.md5(hash_string.encode()).hexdigest()


class Task(object):
    calls_pool_key = 'pool:calls'

    def __init__(self, args=None, key=None):
        if not args or not key:
            raise AttributeError("Args or Key values are required!")

        self.cache = basic_cache.Cache()
        self.args = args
        self.key = key
        self.response_key = 'pool:response:{0}'.format(self.key)

    def create_queue(self):
        self.args.append('key')
        self.args.append(self.response_key)
        #self.args = helper.pickle_data(self.args, protocol=0)
        self.args = json.dumps(self.args)

        self.cache.add_to_list(self.calls_pool_key, self.args)

        return self

    def check_response(self):
        exists, contains = self.cache.check_if_exists_and_contains(self.response_key, value_type='val')
        if exists:
            #return self.cache.get_pickled_dict(self.response_key)
            results = self.cache.get_value(self.response_key)
            return json.loads(results)
        return None


def main():
    args = sys.argv[1:]
    key = create_hashed_key("{0}#{1}".format(time.time(), os.getpid()))
    task = Task(args=args, key=key).create_queue()

    time_left = TOTAL_MAX_TIME
    response = None

    while time_left > 0 and response is None:
        response = task.check_response()
        time_left -= TAP
        time.sleep(TAP)

    if response and len(response):
        code, res = helper.decode_from_b(response['response']).split(':', maxsplit=1)
        print('{0}'.format(res), end='', file=sys.stdout)
        sys.exit(int(code))
    else:
        raise TimeoutError("Call Timeout. No response in given time.")


if __name__ == '__main__':
    main()
