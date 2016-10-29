#!/opt/venv/bin python
# -*- coding: UTF-8
""" Icinga2 Plugin: Check Linux Load
Method to get Machine Disk I/O activity
File name: check_load.py
Author: Aurimas NAVICKAS
Date created: 27/10/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_load.py -H localhost -c bornan -v 2c

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
    Metric,
    Check,
    ScalarContext
)

__author__ = "Aurimas NAVICKAS"

INDEXES = {
    'oids': ['.1.3.6.1.4.1.2021.10.1.2'],
    'values': {
        'Load-1': None,
        'Load-5': None,
        'Load-15': None
    }
}
PERFDATA = {
    'oids': ['.1.3.6.1.4.1.2021.10.1.3'],
    'data': {
        'load_1': {'oid': None, 'value': None, 'index_label': 'Load-1'},
        'alert_load_5': {'oid': None, 'value': None, 'index_label': 'Load-5'},
        'load_15': {'oid': None, 'value': None, 'index_label': 'Load-15'}
    }
}


class SystemLoad(RequestManager):
    # Data Request Manager Class

    def probe(self):
        """
        Query system state and return metrics. Extending from Nagiosplugin->resource
        :return: yields Nagios Metric params with defined variables and their values
        """
        index, perfdat = self.update_performance_data(indexes=INDEXES, perfdata=PERFDATA)   # Getting Monitoring Data
        try:
            for label, value in perfdat['data'].items():
                yield Metric(label, float(value['value']), None, context=label)
        except Exception as e:
            raise CheckError(e)


def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args(description='Check Linux Load')  # Initiating default args

    # Adding some extra args needed for this method
    pargs = args.parse_args()   # Parsing given args
    req_manager = SystemLoad(host=pargs.host, port=pargs.port, community=pargs.community,
                             version=pargs.version)
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for res in PERFDATA['data'].keys():
        if not res.find('alert') == -1:
            resources.append(ScalarContext(res, pargs.warning, pargs.critical))
        else:
            resources.append(ScalarContext(res))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = Check(
                req_manager,
                *resources
            )
    check.main()

if __name__ == '__main__':
    # Calling a main method function
    main()
