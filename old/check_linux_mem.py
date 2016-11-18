#!/opt/venv/bin/python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Linux Memory
Method to Monitor Machine's Memory
File name: check_linux_mem.py
Author: Aurimas NAVICKAS
Date created: 03/11/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_linux_mem.py -H localhost -c bornan -v 2c

Method Static Attributes:
    INDEXES (dict) - a dictionary which keeps needed elements indexes and SNMP Oid's to get them,
    which are needed to get needed info from SNMP tables.
        oids    -> SNMP Oid's list, which will be parsed and stocked in cache.
        values  -> SNMP label: index dictionary
    PERFDATA (dict) (performance data) - a dictionary which keeps SNMP Oid's of the needed data,
    and defined variables which are related to SNMP labels.
        oids    -> SNMP Oid's list, which will be parsed and stocked in cache.
        data    -> local_variable: index mapping, value, dedicated oid dict
"""
from argoss_libs.snmp.request_manager import RequestManager
from nagiosplugin import (
    CheckError,
    Check,
    ScalarContext,
    guarded
)
import logging

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"

INDEXES = {
    'oids': [],
    'values': {
        'memIndex': '0'
    }
}

PERFDATA = {
    'oids': [],
    'data': {
        'mem_total': {'oid': '.1.3.6.1.4.1.2021.4.5', 'value': None, 'index_label': 'memIndex'},
        'mem_used': {'oid': None, 'value': None, 'index_label': None},
        'mem_free': {'oid': '.1.3.6.1.4.1.2021.4.6', 'meta': True, 'value': None, 'index_label': 'memIndex'},
        'alert_mem_percent': {'oid': None, 'value': None, 'index_label': None}
    }
}


class CheckMemory(RequestManager):

    def probe(self):
        try:
            index, perfdata = self.update_performance_data(INDEXES, PERFDATA, force_update_perfdata_from_host=True,
                                                           update_indexes=False)
        except Exception as e:
            raise CheckError("Memory Check Error. %s", e)

        _log.info('Memory Check Perfdata')
        _log.debug(perfdata)

        results = self.digest_results(perfdata['data'])

        return self.yield_metrics(results)

    def digest_results(self, perfdata):
        results = {}
        results['mem_total'] = int(perfdata['mem_total']['value']) * 1024
        results['mem_used'] = results['mem_total'] - (int(perfdata['mem_free']['value']) * 1024)
        results['alert_mem_percent'] = round((results['mem_used'] / results['mem_total']) * 100, 2)

        return results


@guarded()
def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check Memory')  # Initiating default args

    pargs = args.parse_args()  # Parsing given args
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for key, val in PERFDATA['data'].items():
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
        CheckMemory(pargs.host, pargs.port, pargs.community, pargs.version),
        *resources,
    )

    check.main(pargs.verbose)

if __name__ == '__main__':
    main()
