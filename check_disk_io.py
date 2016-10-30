#!/opt/venv/bin/python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Disk I/O
Method to get Machine Disk I/O activity
File name: check_disk_io.py
Author: Aurimas NAVICKAS
Date created: 27/10/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_disk_io.py -H localhost -c bornan -v 2c -d sda

Method Static Attributes:
    INDEXES (dict) - a dictionary which keeps needed elements indexes and SNMP Oid's to get them,
    which are needed to get needed info from SNMP tables.
        oids    -> SNMP Oid's list, which will be parsed and stocked in cache.
        values  -> SNMP label: index dictionary
    PERFDATA (dict) (performance data) - a dictionary which keeps SNMP Oid's of the needed data,
    and defined variables which are related to SNMP labels.
        oids    -> SNMP Oid's list, which will be parsed and stocked in cache.
        data    -> local_variable: index mapping, value, dedicated oid dict
    COMPARISON_TTL (int) - it's a time in seconds which is used to set cache existence for the comparison data.

"""
import time
from argoss_libs.snmp.request_manager import RequestManager
from nagiosplugin import (
    CheckError,
    Metric,
    Check,
    ScalarContext
)

__author__ = "Aurimas NAVICKAS"

INDEXES = {
    'oids': ['.1.3.6.1.4.1.2021.13.15.1.1.2'],
    'values': {}
}

PERFDATA = {
    'oids': [],
    'data': {
        'alert_ioread': {'oid': '.1.3.6.1.4.1.2021.13.15.1.1.5', 'value': None, 'index_label': 'Load-1'},
        'alert_iowrite': {'oid': '.1.3.6.1.4.1.2021.13.15.1.1.6', 'value': None, 'index_label': 'Load-5'}
    }
}

COMPARISON_TTL = 180    # 3 min in seconds


class DiskIO(RequestManager):
    # Data Request Manager Class

    def __init__(self, host, port, community, version, disk, sleep):
        """
        Class Initialization
        :param host: hostname of the machine
        :param port: port number of SNMP in the machine
        :param community: SNMP community
        :param version: SNMP version (1, 2c, 3)
        :param disk: label of the disk in the machine to monitor
        :param sleep: sleep time to get I/O differences if there are no history in cache
        """
        super(DiskIO, self).__init__(host, port, community, version)

        self.disk = disk
        INDEXES['values'][disk] = None
        for key, item in PERFDATA['data'].items():
            item['index_label'] = disk

        self.sleep = sleep
        self.io_key = '%s:check_disk_io:%s' % (self.host, self.disk)

    def check_diff(self, primary_index, primary_perfdata):
        """
        Method to compare I/O data monitored at different times
        :param primary_index: currently monitored indexes dictionary
        :param primary_perfdata: currently monitored perfdata dictionary
        :return: dictionary with the difference of the activity in time delta
        """
        exist, contains = self.cache.check_if_exists_and_contains(self.io_key)
        compare_results = {}

        if exist:
            result_to_compare = self.cache.get_pickled_dict(self.io_key)
            compare_results['result1'] = result_to_compare
            compare_results['result2'] = primary_perfdata
        else:
            time.sleep(self.sleep)
            prim_pd = primary_perfdata.copy()
            index_to_compare, perfdata_to_compare = self.update_performance_data(primary_index, primary_perfdata)
            perfdata_to_compare['timestamp'] = time.time()
            compare_results['result1'] = prim_pd
            compare_results['result2'] = perfdata_to_compare

        self.cache.set_pickled_dict(self.io_key, compare_results['result2'])
        self.cache.set_expire(self.io_key, COMPARISON_TTL)

        return self.compare_results_data(compare_results['result1'], compare_results['result2'])

    @staticmethod
    def compare_results_data(result1, result2):
        """
        A Static comparison method to compare values in time delta
        :param result1: older monitoring data
        :param result2: latest monitoring data
        :return: dictionary with the difference of the activity in time delta
        """
        def average(r1, r2, delta):
            return (r2 - r1) / delta

        if (result1 and result2) and (len(result1) and len(result2)):
            results = result1.copy()

            time_delta = round(float(result2['timestamp']) - float(result1['timestamp']))
            results['time_delta'] = time_delta

            for key in result1['data'].keys():
                if key in result2['data']:
                    results['data'][key]['value'] = round(
                        average(float(result1['data'][key]['value']), float(result2['data'][key]['value']), time_delta),
                        2)

            results['timestamp'] = time.time()

            return results
 
        return {}

    def probe(self):
        """
        Query system state and return metrics. Extending from Nagiosplugin->resource
        :return: yields Nagios Metric params with defined variables and their values
        """
        index, perfdat = self.update_performance_data(indexes=INDEXES, perfdata=PERFDATA, force_update_perfdata_from_host=True)   # Getting Monitoring Data
        perfdat['timestamp'] = time.time()

        diff_results = self.check_diff(primary_index=index, primary_perfdata=perfdat)

        try:
            for label in diff_results['data'].keys():
                yield Metric(label, float(diff_results['data'][label]['value']), None, context=label)
        except Exception as e:
            raise CheckError(e)


def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check Disk I/O')    # Initiating default args

    # Adding some extra args needed for this method
    args.add_argument('--disk', '-d',
                      required=True,
                      type=str, help='Disk name')
    args.add_argument('--sleep-time', '-s',
                      required=False,
                      type=float, help="Sleep time",
                      default=10.0)

    pargs = args.parse_args()   # Parsing given args
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for res in PERFDATA['data'].keys():
        if not res.find('alert') == -1:
            resources.append(ScalarContext(res, pargs.warning, pargs.critical))
        else:
            resources.append(ScalarContext(res))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = Check(
                DiskIO(pargs.host, pargs.port, pargs.community, pargs.version,
                       disk=pargs.disk, sleep=getattr(pargs, 'sleep-time', 10)),
                *resources
            )
    check.main()


if __name__ == '__main__':
    # Calling a main method function
    main()
