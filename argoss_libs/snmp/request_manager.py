# -*- coding: UTF-8
""" Request Manager module
Request Manager which manages all methods calls to get SNMP monitoring data from cache or from the Machine.

File name: request_manager.py
Author: Aurimas NAVICKAS
Date created: 19/10/2016
Python Version: 3.5.2
"""
import argparse
from .probe import SNMPProbe
from .toolkit import SNMPToolkit
from ..config import DEV
from ..cache.basic_cache import Cache
from nagiosplugin.error import CheckError

__author__ = "Aurimas NAVICKAS"
__copyright__ = "Copyright 2016, DISIT, La Poste, France"
__version__ = "0.1"
__email__ = "aurimas.navickas-prestataire@laposte.fr"
__maintainer__ = "Aurimas NAVICKAS"
__status__ = "Dev"


class RequestManager(SNMPProbe):
    """
    RequestManager class to manage every SNMP call to host/equipment or getting info from REDIS/Cache
    Attributes:
        INDEX_TTL (int) - Time in seconds to keep index table cached
        PERFDATA_TTL (int) - Time in seconds to keep Perfdata table in cache
    """

    INDEX_TTL = 24 * 60 * 60     # Indexes Cache Exists 1 day in seconds
    PERFDATA_TTL = 2 * 60     # Performance data Cache Exists 2 Minutes in seconds

    def __init__(self, host, port, community, version, *args, **kwargs):
        super(RequestManager, self).__init__(host=host, port=port, community=community,
                                             version=version, *args, **kwargs)
        """
        Class Initialization
        :param host: hostname of the machine
        :param port: port number of SNMP in the machine
        :param community: SNMP community
        :param version: SNMP version (1, 2c, 3)
        :param *args: extra arguments
        :param **kwargs: extra keyword args
        """
        self.request = Request(self.host, self.port, self.community, self.version)
        self.cache = Cache()
        self.indexes_key = '%s:indexes' % self.host
        self.perfdata_key = '%s:perfdata' % self.host

    def update_indexes(self, indexes, update_from_host=False):
        """
        Method to update indexes using cache or SNMP call
        :param indexes: indexes dictionary
        :param update_from_host: bool which tells to update indexes from SNMP
        :return: Updated indexes dict with index values
        """
        if update_from_host:
            self._get_indexes_from_host(indexes)

        for label in indexes['values']:
            exist, contains = self.cache.check_if_exists_and_contains(self.indexes_key, label)

            if not (exist and contains):
                if not update_from_host:
                    self.update_indexes(indexes, update_from_host=True)
                    break
                else:
                    raise CheckError('Error while fetching Indexes. Label: %s' % label)

            indexes['values'][label] = self.cache.get_hash_value(self.indexes_key, label)

        return indexes

    def update_performance_data(self, indexes, perfdata, force_update_perfdata_from_host=False):
        """
        Method to update performance data dictionary from cache or SNMP
        :param indexes: indexes dictionary
        :param perfdata: performance data dictionary
        :param force_update_perfdata_from_host: Bool which tells to update perfdata from SNMP
        :return: Updated perfdata and indexes
        """
        self.update_indexes(indexes=indexes)

        if force_update_perfdata_from_host:
            self._update_perfdata_from_host(perfdata=perfdata)

        for key, val in perfdata['data'].items():
            perfdata_key = '%s:%s' % (self.perfdata_key, val['oid'] if val['oid'] else perfdata['oids'][0])
            exist, contains = self.cache.check_if_exists_and_contains(perfdata_key,
                                                                      indexes['values'][val['index_label']])

            if not (exist and contains):
                self._get_indexes_from_host(indexes)
                self._update_perfdata_from_host(perfdata)
                exist, contains = self.cache.check_if_exists_and_contains(perfdata_key,
                                                                          indexes['values'][val['index_label']])
                if not (exist or contains):
                    raise CheckError('Error While trying to fetch data for perfdata %s.' % key)

            perfdata['data'][key]['value'] = self.cache.get_hash_value(perfdata_key,
                                                                       indexes['values'][val['index_label']])

        return indexes, perfdata

    def _get_indexes_from_host(self, indexes):
        """
        Method to update indexes from SNMP call
        :param indexes: indexes dictionary
        :return: True
        """
        indexes_request = self.request.snmp_table(indexes['oids'])
        pipe = self.cache.redis.pipeline()

        for request in indexes_request:
            pipe.hset(self.indexes_key, request.value, request.oid_index)

        pipe.expire(self.indexes_key, self.INDEX_TTL)
        pipe.execute(raise_on_error=False)

        return True

    def _update_perfdata_from_host(self, perfdata):
        """
        Method to update performance data table in cache using SNMP
        :param perfdata: performance data dict
        :return: bool - successfully updated?
        """
        oids = perfdata['oids']
        oids += [val['oid'] for key, val in perfdata['data'].items() if val['oid']]

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
        argp.add_argument('--host', '-H',
                          required=True,
                          help='Host target')
        argp.add_argument('--port', '-p',
                          default=port,
                          type=int,
                          help='Port')
        argp.add_argument('--version', '-v',
                          default=version,
                          help='SNMP Version')
        argp.add_argument('--community', '-C',
                          help='SNMP Community',
                          default='bornan')
        argp.add_argument('--warning', '-w',
                          default=warning,
                          help='Warning')
        argp.add_argument('--critical', '-c',
                          default=critical,
                          help='Critical')
        return argp


class Request(SNMPToolkit):
    """
    Extended EasySNMP class to make queries to SNMP
    """

    def __init__(self, host, port, community, version, *args, **kwargs):
        """Class initialization"""
        super(Request, self).__init__(host, port, community, version, *args, **kwargs)
        self.host = host
        self.cache = Cache()
