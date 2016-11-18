#!/opt/venv/bin python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Interface Traffic
Method to get Machine Traffic activity
File name: check_interface_traffic.py
Author: Aurimas NAVICKAS
Date created: 27/10/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_interface_traffic.py -H localhost -c bornan -v 2c -d eth0

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
    Check,
    ScalarContext,
    Result,
    state,
    guarded
)
import logging
from pprint import pprint

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"


class InterfaceStatusContext(ScalarContext):

    def __init__(self, name, warning=None, critical=None, fmt_metric=None, result_cls=Result):
        super(InterfaceStatusContext, self).__init__(name=name, warning=warning, critical=critical,
                                                     fmt_metric=fmt_metric, result_cls=result_cls)


    def evaluate(self, metric, resource):
        if int(metric.value) == 1:
            return self.result_cls(state.Ok, metric=metric)
        else:
            hint = ('There is a problem with your interface status')
            return self.result_cls(state.Critical, hint=hint, metric=metric)


INDEXES = {
    'oids': ['1.3.6.1.2.1.31.1.1.1.1', '1.3.6.1.2.1.2.2.1.2'],  # IfName and IfDescr
    'values': {}
}

ARCH = 64

COMPARISON_TTL = 180

multiple_perfdata = {
    64: {
        'PERFDATA': {
            'oids': [],
            'data': {
                'alert_traffic_in_percent': { 'oid': '.1.3.6.1.2.1.31.1.1.1.6', 'value': None, 'index_label': None },
                'alert_traffic_out_percent': { 'oid': '.1.3.6.1.2.1.31.1.1.1.10', 'value': None, 'index_label': None },
                'traffic_in_bps': { 'oid': '.1.3.6.1.2.1.31.1.1.1.6', 'value': None, 'index_label': None },
                'traffic_out_bps': { 'oid': '.1.3.6.1.2.1.31.1.1.1.10', 'value': None, 'index_label': None },
                'if_status': { 'oid': '.1.3.6.1.2.1.2.2.1.8', 'value': None, 'index_label': None,
                            'context': InterfaceStatusContext },
                'speed': { 'oid': '.1.3.6.1.2.1.31.1.1.1.15', 'meta': True, 'value': None, 'index_label': None }
            }
        }
    },
    32: {
        'PERFDATA': {
            'oids': [],
            'data': {
                'alert_traffic_in_percent': { 'oid': '.1.3.6.1.2.1.2.2.1.10', 'value': None, 'index_label': None },
                'alert_traffic_out_percent': { 'oid': '.1.3.6.1.2.1.2.2.1.16', 'value': None, 'index_label': None },
                'traffic_in_bps': { 'oid': '.1.3.6.1.2.1.2.2.1.10', 'value': None, 'index_label': None },
                'traffic_out_bps': { 'oid': '.1.3.6.1.2.1.2.2.1.16', 'value': None, 'index_label': None },
                'if_status': { 'oid': '.1.3.6.1.2.1.2.2.1.8', 'value': None, 'index_label': None,
                            'context': InterfaceStatusContext },
                'speed': { 'oid': '.1.3.6.1.2.1.2.2.1.5', 'meta': True, 'value': None, 'index_label': None }
            }
        }
    },
}


class InterfaceTraffic(RequestManager):

    def __init__(self, host, port, community, version, interface=None, bandw=None):
        """
        Class Initialization
        :param host: hostname of the machine
        :param port: port number of SNMP in the machine
        :param community: SNMP community
        :param version: SNMP version (1, 2c, 3)
        :param interface: Selected interface to monitor
        """
        super(InterfaceTraffic, self).__init__(host=host, port=port, community=community, version=version)

        if not interface:
            raise ValueError('Interface name should be provided!')

        self.interface = interface
        self.bandw = bandw
        self.arch_key = '%s:arch' % self.host
        self.traffic_compare_key = '%s:traffic_compare' % self.host

        INDEXES['values'][interface] = None
        for arch in [32, 64]:
            for key, item in multiple_perfdata[arch]['PERFDATA']['data'].items():
                item['index_label'] = interface

    def probe(self):
        """
        Query system state and return metrics. Extending from Nagiosplugin->resource
        :return: yields Nagios Metric params with defined variables and their values
        """
        global ARCH

        exists, contains = self.cache.check_if_exists_and_contains(self.arch_key, ARCH, value_type='val')
        if exists:
            if not contains:
                ARCH = self.cache.get_value(self.arch_key)

        try:
            index, perfdata = self.update_performance_data(indexes=INDEXES,
                                                           perfdata=multiple_perfdata[ARCH]['PERFDATA'],
                                                           force_update_perfdata_from_host=True)
        except Exception as e:
            try:
                ARCH = 64 if ARCH == 32 else 32
                index, perfdata = self.update_performance_data(indexes=INDEXES,
                                                               perfdata=multiple_perfdata[ARCH]['PERFDATA'],
                                                               force_update_perfdata_from_host=True)
            except Exception as ee:
                raise CheckError(ee)

        self.cache.set_value(self.arch_key, ARCH)

        if not int(perfdata['data']['if_status']['value']) == 1:
            return self.yield_metrics(perfdata['data'])

        perfdata['timestamp'] = time.time()

        exists, contains = self.cache.check_if_exists_and_contains(self.traffic_compare_key)
        if exists:
            compare_perfdata = self.cache.get_pickled_dict(self.traffic_compare_key)
            self.cache.set_pickled_dict(self.traffic_compare_key, perfdata, expire=COMPARISON_TTL)
        else:
            self.cache.set_pickled_dict(self.traffic_compare_key, perfdata, expire=COMPARISON_TTL)
            raise CheckError('No comparison data yet')

        _log.info('Getting Results after comparing')
        results = self.digest_results(perfdata, compare_perfdata)
        _log.debug(results)

        return self.yield_metrics(results)

    def digest_results(self, current_perfdata, compare_perfdata):
        time_delta = current_perfdata['timestamp'] - compare_perfdata['timestamp']
        results = {}
        results['traffic_in_bps'] = round(float((int(current_perfdata['data']['traffic_in_bps']['value'])
                                     - int(compare_perfdata['data']['traffic_in_bps']['value'])) / time_delta), 2)
        results['traffic_out_bps'] = round(float((int(current_perfdata['data']['traffic_out_bps']['value'])
                                      - int(compare_perfdata['data']['traffic_out_bps']['value'])) / time_delta), 2)

        speed = self.bandw
        if not speed:
            speed = float(current_perfdata['data']['speed']['value'])
            speed *= 1000000 if ARCH == 64 else 1

        results['alert_traffic_in_percent'] = round(results['traffic_in_bps'] / speed * 100, 2)
        results['alert_traffic_out_percent'] = round(results['traffic_out_bps'] / speed * 100, 2)

        results['if_status'] = current_perfdata['data']['if_status']['value']

        return results


@guarded
def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check Interface Traffic')    # Initiating default args

    # Adding some extra args needed for this method
    args.add_argument('--descr', '-d',type=str, required=True, help='Interface description')
    args.add_argument('--bandwidth', '-b', type=float, help='Interface bandwidth')

    pargs = args.parse_args()   # Parsing given args
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for key, val in multiple_perfdata[ARCH]['PERFDATA']['data'].items():
        if not 'meta' in val:
            CONTEXT = ScalarContext
            if 'context' in val:
                CONTEXT = val['context']
            if not key.find('alert') == -1:
                resources.append(CONTEXT(key, pargs.warning, pargs.critical))
            else:
                resources.append(CONTEXT(key))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = Check(
                InterfaceTraffic(pargs.host, pargs.port, pargs.community, pargs.version,
                       interface=pargs.descr, bandw=pargs.bandwidth),
                *resources,
            )

    check.main(pargs.verbose)


if __name__ == '__main__':
    # Calling a main method function
    main()
