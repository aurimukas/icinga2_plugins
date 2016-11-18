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
from argoss_libs.snmp.perfdata import PerfDataItem
from nagiosplugin import CheckError
from nagiosplugin import Check
from nagiosplugin import ScalarContext
from nagiosplugin import guarded

import pandas
import logging

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"

INDEXES = {
    'oids': [],
    'values': {
        'memIndex': '0'
    }
}

PERFDATA = [
    PerfDataItem(key='mem_total', oid='.1.3.6.1.4.1.2021.4.5', index_label='memIndex', calculation='mem_total * 1024',
                          return_value=True),
    PerfDataItem(key='mem_free', oid='.1.3.6.1.4.1.2021.4.6', index_label='memIndex', calculation='mem_free * 1024',
                         return_value=False),
    PerfDataItem(key='mem_used', priority=1, calculation='mem_total - mem_free', return_value=True),
    PerfDataItem(key='alert_mem_percent', priority=2, calculation='(mem_used / mem_total) * 100', value_type='%f',
                 return_value=True)
]


class CheckMemory(RequestManager):

    def probe(self):
        try:
            self.update_performance_data(force_update_perfdata_from_host=True, update_indexes=False)
        except Exception as e:
            raise CheckError("Memory Check Error. %s", e)

        _log.info('Memory Check Perfdata')
        _log.debug(self.perfdata)

        sorted_perfdata = sorted(self.perfdata, key=lambda i: i.priority)
        _log.info('Creating Sorted perfdata')
        _log.debug(sorted_perfdata)

        _log.info('Preparing DataFrame cols and values')
        values = list((tuple(data() for data in sorted_perfdata),))
        cols = list(data.key for data in sorted_perfdata)
        _log.info('Cols')
        _log.debug(cols)
        _log.info('Values')
        _log.debug(values)

        _log.info('Creating Pandas DataFrame')
        dataFrame = pandas.DataFrame(data=values, columns=cols)
        _log.debug(dataFrame)

        _log.info('Pandas Expressions evaluation')
        for data in sorted_perfdata:
            if data.calculation:
                dataFrame.eval("%s=%s" % (data.key, data.calculation), inplace=True)
        _log.info('DataFrame after calculations')
        _log.debug(dataFrame)

        self.update_perfdata_from_dataframe(dataFrame)

        return self.yield_metrics()

    def update_perfdata_from_dataframe(self, dataFrame, index=0):
        for pd in self.perfdata:
            pd.value = dataFrame[pd.key][index]


@guarded()
def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check Linux Memory')  # Initiating default args

    pargs = args.parse_args()  # Parsing given args
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for pd in PERFDATA:
        if pd.return_value:
            CONTEXT = ScalarContext
            if pd.context:
                CONTEXT = pd.context
            if not pd.key.find('alert') == -1:
                resources.append(CONTEXT(pd.key, pargs.warning, pargs.critical))
            else:
                resources.append(CONTEXT(pd.key))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = Check(
        CheckMemory(pargs.host, pargs.port, pargs.community, pargs.version, perfdata=PERFDATA, indexes=INDEXES),
        *resources,
    )

    check.main(pargs.verbose)

if __name__ == '__main__':
    main()
