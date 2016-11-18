# -*- coding: UTF-8
""" Request Manager module
Request Manager which manages all method calls to get SNMP monitoring data from cache or from the Machine.

File name: request_manager.py
Author: Aurimas NAVICKAS
Date created: 19/10/2016
Python Version: 3.5.2
"""
import importlib
argparse = importlib.import_module('argparse')
pd_class = importlib.import_module('argoss_libs.snmp.perfdata')
from .toolkit import SNMPToolkit

basic_cache = importlib.import_module('argoss_libs.cache.basic_cache')
helper = importlib.import_module('.helpers', 'argoss_libs.cache')
nagios = importlib.import_module('nagiosplugin')
pandas = importlib.import_module('pandas')
np = importlib.import_module('nagiosplugin')
logging = importlib.import_module('logging')

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"
__copyright__ = "Copyright 2016, DISIT, La Poste, France"
__version__ = "0.1"
__email__ = "aurimas.navickas-prestataire@laposte.fr"
__maintainer__ = "Aurimas NAVICKAS"
__status__ = "Dev"


class RequestManager(nagios.Resource):
    """
    RequestManager class to manage every SNMP call to host/equipment or getting info from REDIS/Cache

    :param INDEX_TTL: Time in seconds to keep index table cached
    :param PERFDATA_TTL: Time in seconds to keep Perfdata table in cache
    """

    INDEX_TTL = 24 * 60 * 60
    PERFDATA_TTL = 2 * 60

    def __init__(self, host, port, community, version, perfdata, indexes, *args, **kwargs):
        """
        Class Initialization

        :param host: hostname of the machine
        :param port: port number of SNMP in the machine
        :param community: SNMP community
        :param version: SNMP version (1, 2c, 3)
        :param *args: extra arguments
        :param **kwargs: extra keyword args
        """
        if not perfdata or not indexes:
            raise AttributeError('Need Perdata and/or Indexes to create a RequestManager Class')
        self.host = host
        self.request = Request(host, port, community, version)

        self.perfdata = perfdata
        self.indexes = indexes
        self.cache = basic_cache.Cache()
        self.indexes_key = '%s:indexes' % self.host
        self.perfdata_key = '%s:perfdata' % self.host

    def update_indexes(self, update_from_host=False):
        """
        Method to update indexes using cache or SNMP call

        :parameter update_from_host: bool which force to update indexes from Machine's SNMP
        :return: Updated indexes dict with index values
        """
        if update_from_host:
            self._get_indexes_from_host()

        for label in self.indexes['values']:
            exist, contains = self.cache.check_if_exists_and_contains(self.indexes_key, label)

            if not (exist and contains):
                if not update_from_host:
                    self.update_indexes(update_from_host=True)
                    break
                else:
                    raise np.CheckError('Error while fetching Indexes. Label: %s' % label)

            self.indexes['values'][label] = self.cache.get_hash_value(self.indexes_key, label)

    def update_performance_data(self, force_update_perfdata_from_host=False, update_indexes=True):
        """
        Method to update performance data dictionary from cache or SNMP

        :param force_update_perfdata_from_host: Bool which tells to update perfdata from SNMP
        :param update_indexes: Do we need to update indexes while updating perfdata

        :return: Updates Perfdata and indexes (if True) in class variables.
        """
        if update_indexes:
            self.update_indexes()

        if force_update_perfdata_from_host:
            self._update_perfdata_from_host()

        for pd in self.perfdata:
            if not pd.index_label:
                continue

            perfdata_key = '%s:%s' % (self.perfdata_key, pd.oid if pd.oid else pd.key)
            exist, contains = self.cache.check_if_exists_and_contains(perfdata_key,
                                                                      self.indexes['values'][pd.index_label])
            if not (exist and contains):
                if update_indexes:
                    self._get_indexes_from_host()
                self._update_perfdata_from_host()
                exist, contains = self.cache.check_if_exists_and_contains(perfdata_key,
                                                                          self.indexes['values'][pd.index_label])
                if not (exist or contains):
                    raise np.CheckError('Error While trying to fetch data for perfdata %s.' % pd.key)

            pd.value = self.cache.get_hash_value(perfdata_key, self.indexes['values'][pd.index_label])

    def update_perfdata_from_dataframe(self, dataFrame, index=0):
        """
        Updates class perfdata from Pandas Dataframe object.

        :param dataFrame: Pandas dataframe object
        :param index: Line(index) number in dataframe which we need to use
        :return: updates class variables
        """
        for pd in self.perfdata:
            pd.value = dataFrame[pd.key][index]

    def _get_indexes_from_host(self):
        """
        Method to update indexes from SNMP call
        :param indexes: indexes dictionary
        :return: True
        """
        if len(self.indexes['oids']):
            indexes_request = self.request.snmp_table(self.indexes['oids'])
            pipe = self.cache.redis.pipeline()

            for request in indexes_request:
                pipe.hset(self.indexes_key, helper.strip_string(request.value), request.oid_index)

            pipe.expire(self.indexes_key, self.INDEX_TTL)
            pipe.execute(raise_on_error=False)

            return True

        return False

    def _update_perfdata_from_host(self):
        """
        Method to update performance data table in cache using SNMP
        :param perfdata: performance data dict
        :return: bool - successfully updated?
        """
        oids = [pd.oid for pd in self.perfdata if pd.oid]

        perfdata_requests = self.request.snmp_table(oids)

        if len(perfdata_requests):
            pipe = self.cache.redis.pipeline()
            for request in perfdata_requests:
                perfdata_key = '%s:%s' % (self.perfdata_key, request.oid)
                pipe.hset(perfdata_key, request.oid_index, request.value)
                pipe.expire(perfdata_key, self.PERFDATA_TTL)
            pipe.execute()
            return True

        return False

    def yield_metrics(self):
        """
        Yield Nagios Metric from class perfdata

        :return: Yields Nagios Metrics
        """
        results = []
        # _log.info('Yield_Metrics method perfdata')
        # _log.debug(self.perfdata)
        try:
            for pd in self.perfdata:
                if pd.return_value:
                    results.append(np.Metric(pd.key, pd(), None, context=pd.key))
        except Exception as e:
            raise np.error.CheckError(e)

        return results

    def eval_expressions(self):
        """
        Evaluates given expressions using Pandas Data Frame Object

        :return: None
        """
        sorted_perfdata = sorted(self.perfdata, key=lambda i: i.priority)
        # _log.info('Creating Sorted perfdata')
        # _log.debug(sorted_perfdata)

        # _log.info('Preparing DataFrame cols and values')
        values = list((tuple(data() for data in sorted_perfdata),))
        cols = list(data.key for data in sorted_perfdata)
        # _log.info('Cols')
        # _log.debug(cols)
        # _log.info('Values')
        # _log.debug(values)

        # _log.info('Creating Pandas DataFrame')
        data_frame = pandas.DataFrame(data=values, columns=cols)
        # _log.debug(dataFrame)

        # _log.info('Pandas Expressions evaluation')
        for data in sorted_perfdata:
            if data.calculation:
                data_frame.eval("%s=%s" % (data.key, data.calculation), inplace=True)
                # _log.info('DataFrame after calculations')
                # _log.debug(dataFrame)

        self.update_perfdata_from_dataframe(data_frame)

    def apply_cached_perfdata(self, cached_data):
        """
        Applies Cache data from redis to class perfdata List to evaluate calculations later

        :param cached_data: Cached data dictionary to apply to class perfdata
        :return: Applies class perfdata variable
        """
        for data in cached_data:
            obj = pd_class.PerfDataItem(key='start')
            for key in data:
                setattr(obj, key, data[key])
            self.perfdata.append(obj)

    @staticmethod
    def prepare_cache_perfdata(perfdata):
        """
        Prepares class perfdata variable to be cached in Redis.

        :param perfdata: Class perfdata variable
        :return: List of dictionaries of perfdata attributes.
        """
        results = []
        for pd in perfdata:
            c_pd = {
                'key': '{0}_cache'.format(pd.key),
                'oid': pd.oid,
                'value_type': pd.value_type,
                'value': pd.value
            }
            results.append(c_pd)

        return results

    @staticmethod
    def default_args(description, port=161, version=2, warning=80.0, critical=90.0):
        """
        Static Method which prepares mostly used args for the methods

        :param description: Description of the method which uses this args
        :param port: Machine's SNMP port
        :param version: SNMP version
        :param warning: warning level
        :param critical: critical level
        :return: Object with defined args
        """

        argp = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        argp.add_argument('--host', '-H', required=True, help='Host target')
        argp.add_argument('--port', '-p', default=port, type=int, help='Port')
        argp.add_argument('--version', '-v', default=version, help='SNMP Version')
        argp.add_argument('--community', '-C', help='SNMP Community', default='bornan')
        argp.add_argument('--warning', '-w', default=warning, help='Warning')
        argp.add_argument('--critical', '-c', default=critical, help='Critical')
        argp.add_argument('--verbose', '-V', action='count', default=0)

        return argp


class Request(SNMPToolkit):
    """
    Extended EasySNMP class to make queries to SNMP
    """

    def __init__(self, host, port, community, version, *args, **kwargs):
        """Class initialization"""
        super(Request, self).__init__(host, port, community, version, *args, **kwargs)
        self.host = host
        self.cache = basic_cache.Cache()
