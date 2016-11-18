#!/opt/venv/bin/python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Disk I/O
Method to Monitor Machine's Memory
File name: check_disk_io.py
Author: Aurimas NAVICKAS
Date created: 03/11/2016
Python Version: 3.5.2
"""
import importlib
time = importlib.import_module('time')
rm = importlib.import_module('.request_manager', 'argoss_libs.snmp')
pd_class = importlib.import_module('.perfdata', 'argoss_libs.snmp')
PerfDataItem = pd_class.PerfDataItem
nagios = importlib.import_module('nagiosplugin')

logging = importlib.import_module('logging')

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"


class CheckDiskIo(rm.RequestManager):
    """
    Check Machine's Disk I/O Metrics Method

    Extra parameters to pass:

    :param --disk, -d: Disk name. Required

    Static Parameters:

    :param COMPARISON_TTL: a time in seconds which is used to set cache existence for the comparison\
    data in redis.
    """

    COMPARISON_TTL = 180

    def __init__(self, params, *args, **kwargs):
        """
        Class initialization.

        :param params: Args list to pass to argsParser.
        :param args: Extra Args
        :param kwargs: Extra kwargs
        """
        # Getting default args defined in RequestManager Class
        argsp = self.default_args("Check Disk IO")
        # Extra args definition
        argsp.add_argument('--disk', '-d', required=True, type=str, help='Disk name')
        # Parsing passed params with argsParser
        self.pargs = argsp.parse_args(params)
        # Redis key to store machine's disk IO comparison data
        self.io_key = '{0.host}:check_disk_io:{0.disk}'.format(self.pargs)

        # Indexes primary definition
        indexes = {
            'oids': ['.1.3.6.1.4.1.2021.13.15.1.1.2'],
            'values': {}
        }
        # Setting current timestamp
        timestamp = time.time()
        # Perfdata definition
        perfdata = [
            # Time delta from Now and time cached in Redis of last check.
            PerfDataItem(key='delta', return_value=False, value_type='%f', value=timestamp, priority=0,
                         calculation="delta-delta_cache"),
            PerfDataItem(key='alert_ioread', oid='.1.3.6.1.4.1.2021.13.15.1.1.5', return_value=True, value_type='%f',
                         calculation="(alert_ioread-alert_ioread_cache)/delta", priority=0),
            PerfDataItem(key='alert_iowrite', oid='.1.3.6.1.4.1.2021.13.15.1.1.6', return_value=True, value_type='%f',
                         calculation="(alert_iowrite-alert_iowrite_cache)/delta", priority=0),
        ]
        # Setting PerfDataItems index_label to passed disk name
        indexes['values'][self.pargs.disk] = None
        for pd in perfdata:
            if pd.return_value:
                pd.index_label = self.pargs.disk

        # Init a Super Class
        super(CheckDiskIo, self).__init__(self.pargs.host, self.pargs.port, self.pargs.community, self.pargs.version,
                                          indexes=indexes, perfdata=perfdata, *args, **kwargs)

    def probe(self):
        """Query system state and return metrics.

        This is the only method called by the check controller.
        It should trigger all necessary actions and create metrics.

        :return: list of :class:`~nagiosplugin.metric.Metric` objects,
            or generator that emits :class:`~nagiosplugin.metric.Metric`
            objects, or single :class:`~nagiosplugin.metric.Metric`
            object
        """
        # Updating Perfdata and indexes
        try:
            self.update_performance_data(force_update_perfdata_from_host=True)
        except Exception as e:
            raise nagios.CheckError("Memory Check Error. %s", e)

        # Preparing perfdata data to cache for future runs
        perfdata_to_cache  = self.prepare_cache_perfdata(self.perfdata)
        # Checking if we have a cached data from previous run
        exists, contains = self.cache.check_if_exists_and_contains(self.io_key, value_type='val')
        if exists:
            # Getting cached data from Redis
            c_perfdata = self.cache.get_pickled_dict(self.io_key)
            if isinstance(c_perfdata, list) and len(c_perfdata):
                # Applying cache data to perfdata
                self.apply_cached_perfdata(c_perfdata)
        # Setting a new cache data for next run
        self.cache.set_pickled_dict(self.io_key, perfdata_to_cache, expire=self.COMPARISON_TTL)

        if not exists:
            # No data in Cache. Nothing to compare. Exit
            raise nagios.CheckError('No Data to compare with')

        # _log.debug(self.perfdata)
        # Evaluate calculations defined in Perfdata
        self.eval_expressions()
        # Generate Nagios Metrics list and return it
        return self.yield_metrics()
