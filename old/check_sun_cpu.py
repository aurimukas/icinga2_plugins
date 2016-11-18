#!/opt/venv/bin/python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Sun CPU
Method to get Sun Machine CPU activity in %
File name: check_sun_cpu.py
Author: Aurimas NAVICKAS
Date created: 04/11/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_sun_cpu.py -H localhost -c bornan -v 2c

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
    ScalarContext,
    guarded
)
import logging

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"

INDEXES = {
    'oids': [],
    'values': {}
}

PERFDATA = {
    'oids': ['1.3.6.1.4.1.2021.11.11.0'],   # Getting CPU Idle
    'data': {
        'alert_cpu_percent': {'oid': None, 'value': None, 'index_label': None}
    }
}


class SunCPU(RequestManager):

    def probe(self):
        # Getting CPU Idle
        idle = self.request.fetch_oid(PERFDATA['oids'][0])

        try:
            if idle:
                PERFDATA['data']['alert_cpu_percent']['value'] = 100 - int(idle)
        except Exception as e:
            raise CheckError('CPU not available. Exception: %s' % e)

        try:
            yield Metric('alert_cpu_percent', PERFDATA['data']['alert_cpu_percent']['value'], None,
                         context='alert_cpu_percent')
        except Exception as e:
            raise CheckError(e)


@guarded
def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check Sun CPU')  # Initiating default args

    pargs = args.parse_args()  # Parsing given args
    resources = []

    # Creating Context Params array to pass to Nagiosplugin check function
    for res in PERFDATA['data'].keys():
        if not res.find('alert') == -1:
            resources.append(ScalarContext(res, pargs.warning, pargs.critical))
        else:
            resources.append(ScalarContext(res))

    # Calling Nagiosplugin Check function to get translated monitoring data
    check = Check(
        SunCPU(pargs.host, pargs.port, pargs.community, pargs.version),
        *resources
    )
    check.main(pargs.verbose)

if __name__ == '__main__':
    main()
