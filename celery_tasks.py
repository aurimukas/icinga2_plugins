# -*- coding: UTF-8
"""
Celery App Tasks module.
"""
import importlib
from celery_config import app
json = importlib.import_module('json')
celery = importlib.import_module('celery')
basic_cache = importlib.import_module('.cache.basic_cache', 'argoss_libs')
helpers = importlib.import_module('.helpers', 'argoss_libs.cache')
snmp_nagios = importlib.import_module('.snmp.snmp_nagios', 'argoss_libs')
nagios = importlib.import_module('nagiosplugin')
sondes = importlib.import_module('sondes')


class TaskCallback(celery.task.Task):
    """
    Task class which extends Celery Base Task class.

    Static Class params changed:

    :param expires: Task Expiration in queue if not launched in seconds
    :param db_expires: Redis Task will expire in given time in seconds
    :param cache: Initialized Redis management module.
    """
    expires = 50
    db_expires = 600

    cache = basic_cache.Cache()

    def on_success(self, retval, task_id, args, kwargs):
        """Success handler.

        Run by the worker if the task executes successfully.

        Arguments:
           retval (Any): The return value of the task.
           task_id (str): Unique id of the executed task.
           args (Tuple): Original arguments for the executed task.
           kwargs (Dict): Original keyword arguments for the executed task.

        Returns:
           None: The return value of this handler is ignored.
        """

        data = {
            'response': retval,
            'task_id': task_id,
            'args': args,
            'kwargs': kwargs
        }

        #self.cache.set_pickled_dict(self.response_key, data, protocol=2, expire=self.db_expires)
        self.cache.set_value(self.response_key, json.dumps(data), ex=self.db_expires)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """

        data = {
            'response': '3:{0}'.format(exc),
            'task_id': task_id,
            'args': args,
            'kwargs': kwargs,
            'einfo': einfo
        }

        self.cache.set_pickled_dict(self.response_key, data, protocol=2, expire=self.db_expires)


@app.task(base=TaskCallback, bind=True)
def call_method(self, params, method=''):
    """
    Celery task to make a SNMP method async call.

    :param self: Class
    :param params: Params passed through command line as a list
    :param method: Method name
    :return: Pickled dict with response and Celery task data
    """
    key = params.pop()
    params.pop()

    self.response_key = key

    if method:
        try:
            cls = importlib.import_module('sondes.%s' % method)
            mth = getattr(cls, helpers.camelize(method))(params)
            result_code, result = main(mth)
            return '{0}:{1}'.format(result_code, result)
        except ImportError as e:
            return '3:Error: %s' % e

    return '{0}:{1}'.format(3, 'No method implemented!')


@snmp_nagios.guarded()
def main(cls):
    """
    Creates Nagios context elements and launches Nagios check

    :param cls: Initialized Method class
    :return: Nagios check response
    """
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for pd in cls.perfdata:
        if pd.return_value:
            CONTEXT = nagios.ScalarContext
            if pd.context:
                CONTEXT = pd.context
            if not pd.key.find('alert') == -1:
                resources.append(CONTEXT(pd.key, cls.pargs.warning, cls.pargs.critical))
            else:
                resources.append(CONTEXT(pd.key))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = snmp_nagios.SnmpCheck(
        cls,
        *resources,
    )

    return check.main(cls.pargs.verbose)
