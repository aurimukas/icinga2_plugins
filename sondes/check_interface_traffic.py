#!/opt/venv/bin python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Interface Traffic
Method to get Machine Traffic activity
File name: check_interface_traffic.py
Author: Aurimas NAVICKAS
Date created: 27/10/2016
Python Version: 3.5.2
"""
import importlib
time = importlib.import_module('time')
rm = importlib.import_module('.request_manager', 'argoss_libs.snmp')
pd_class = importlib.import_module('.perfdata', 'argoss_libs.snmp')
PerfDataItem = pd_class.PerfDataItem
snmp_nagios = importlib.import_module('.snmp_nagios', 'argoss_libs.snmp')
np = importlib.import_module('nagiosplugin')

logging = importlib.import_module('logging')

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"


class CheckInterfaceTraffic(rm.RequestManager):
    """
    Check Network Interfaces Traffic Metrics Method

    Static Parameters:

    :param COMPARISON_TTL: a time in seconds which is used to set cache existence for the comparison\
    data in redis.

    Extra parameters to pass:

    :param -d: Interface description. Required
    :param -b: Interface speed. Optional
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
        argsp = self.default_args("Check Interface Traffic")

        # Extra args definition
        argsp.add_argument('--descr', '-d', type=str, required=True, help='Interface description')
        argsp.add_argument('--bandwidth', '-b', type=float, help='Interface bandwidth')

        # Parsing passed params with argsParser
        self.pargs = argsp.parse_args(params)

        self.counter = 64   # Setting primary counter type
        # Redis key where pickled perfdata dictionary will be stored
        self.traffic_compare_key = '{0.host}:traffic_compare:{0.descr}'.format(self.pargs)
        # Redis counter type key for given interface
        self.counter_key = '%s:counter' % self.traffic_compare_key

        # Indexes primary definition
        indexes = {
            'oids': ['1.3.6.1.2.1.31.1.1.1.1', '1.3.6.1.2.1.2.2.1.2'],  # IfName and IfDesc
            'values': {}
        }

        # Setting Perfdata for this method for 32 and 64 bits counter
        perfdata = {
            32: [
                # Time delta from Now and time cached in Redis of last check.
                PerfDataItem(key='delta', return_value=False, value_type='%f', value=time.time(), priority=0,
                             calculation="delta - delta_cache"),
                PerfDataItem(key='alert_traffic_in_percent', value_type='%f', return_value=True, priority=2,
                             calculation='traffic_in_bps / speed * 100'),
                PerfDataItem(key='alert_traffic_out_percent', value_type='%f', return_value=True, priority=2,
                             calculation='traffic_out_bps / speed * 100'),
                PerfDataItem(key='traffic_in_bps', oid='.1.3.6.1.2.1.2.2.1.10', value_type='%f', return_value=True,
                             calculation='(traffic_in_bps - traffic_in_bps_cache) / delta', priority=1),
                PerfDataItem(key='traffic_out_bps', oid='.1.3.6.1.2.1.2.2.1.16', value_type='%f', return_value=True,
                             calculation='(traffic_out_bps - traffic_out_bps_cache) / delta', priority=1),
                PerfDataItem(key='if_status', oid='.1.3.6.1.2.1.2.2.1.8', value_type='%i', return_value=True,
                             context=snmp_nagios.InterfaceStatusContext),
                PerfDataItem(key='speed', oid='.1.3.6.1.2.1.2.2.1.5', value_type='%i', return_value=False, priority=0),
            ],
            64: [
                PerfDataItem(key='delta', return_value=False, value_type='%f', value=time.time(), priority=0,
                             calculation="delta - delta_cache"),
                PerfDataItem(key='alert_traffic_in_percent', value_type='%f', return_value=True, priority=2,
                             calculation='traffic_in_bps / speed * 100'),
                PerfDataItem(key='alert_traffic_out_percent', value_type='%f', return_value=True, priority=2,
                             calculation='traffic_out_bps / speed * 100'),
                PerfDataItem(key='traffic_in_bps', oid='.1.3.6.1.2.1.31.1.1.1.6', value_type='%f', return_value=True,
                             calculation='(traffic_in_bps - traffic_in_bps_cache)/delta', priority=1),
                PerfDataItem(key='traffic_out_bps', oid='.1.3.6.1.2.1.31.1.1.1.10', value_type='%f', return_value=True,
                             calculation='(traffic_out_bps - traffic_out_bps_cache) / delta', priority=1),
                PerfDataItem(key='if_status', oid='.1.3.6.1.2.1.2.2.1.8', value_type='%i', return_value=True,
                             context=snmp_nagios.InterfaceStatusContext),
                PerfDataItem(key='speed', oid='.1.3.6.1.2.1.31.1.1.1.15', value_type='%i', return_value=False,
                             calculation='speed * 1000000', priority=0),
            ]
        }

        # Setting PerfDataItems index_label to passed interface name
        indexes['values'][self.pargs.descr] = None
        for counter in [32, 64]:
            for pd in perfdata[counter]:
                if pd.oid:
                    pd.index_label = self.pargs.descr

        # Init a Super Class
        super(CheckInterfaceTraffic, self).__init__(self.pargs.host, self.pargs.port, self.pargs.community,
                                                    self.pargs.version, indexes=indexes, perfdata=perfdata,
                                                    *args, **kwargs)

        # Doing perfdata update from server same time updating counter type
        self.update_counter_type_and_data(perfdata=perfdata)

    def probe(self):
        """Query system state and return metrics.

        This is the only method called by the check controller.
        It should trigger all necessary actions and create metrics.

        :return: list of :class:`~nagiosplugin.metric.Metric` objects,
            or generator that emits :class:`~nagiosplugin.metric.Metric`
            objects, or single :class:`~nagiosplugin.metric.Metric`
            object
        """
        # Checking If_status. If it's not 1 will return status 3 and current perfdata (no calculations done)
        for pd in self.perfdata:
            if pd.key == 'if_status' and not pd() == 1:
                return self.yield_metrics()

        # Preparing perfdata data to cache for future runs
        perfdata_to_cache = self.prepare_cache_perfdata(self.perfdata)
        # Checking if we have a cached data from previous run
        exists, contains = self.cache.check_if_exists_and_contains(self.traffic_compare_key, value_type='val')
        if exists:
            # Getting cached data from Redis
            c_perfdata = self.cache.get_pickled_dict(self.traffic_compare_key)
            if isinstance(c_perfdata, list) and len(c_perfdata):
                # Applying cache data to perfdata
                self.apply_cached_perfdata(c_perfdata)

        # Setting a new cache data for next run
        self.cache.set_pickled_dict(self.traffic_compare_key, perfdata_to_cache, expire=self.COMPARISON_TTL)

        if not exists:
            # No data in Cache. Nothing to compare. Exit
            raise np.CheckError('No Data to compare with')

        # _log.debug(self.perfdata)

        # Evaluate calculations defined in Perfdata
        self.eval_expressions()

        # Generate Nagios Metrics list and return it
        return self.yield_metrics()

    def update_counter_type_and_data(self, perfdata):
        """
        Update perfdata and indexes and finding a counter type used in SNMP

        :param perfdata: Perfdata Dict with both counter types
        :return: Updates Class perfdata variable
        """
        # Checking do we have a counter type saved in cached for machine's network interface
        exists, contains = self.cache.check_if_exists_and_contains(self.counter_key, self.counter, value_type='val')
        if exists:
            if not contains:
                # Counter type saved in cache is not same as defined change it
                self.counter = self.cache.get_value(self.counter_key)

        try:
            # Trying to update perfdata with given counter type
            self.perfdata = perfdata[self.counter]
            self.update_performance_data(force_update_perfdata_from_host=True)

        except Exception as e:
            try:
                # Changing counter type and trying to update once again
                self.counter = 64 if self.counter == 32 else 32
                self.perfdata = perfdata[self.counter]
                self.update_performance_data(force_update_perfdata_from_host=True)

            except Exception as ee:
                # Can't update perfdata. Raise error
                raise np.CheckError(ee)

        # Updated successfully. Save in cache a counter type.
        self.cache.set_value(self.counter_key, self.counter)
