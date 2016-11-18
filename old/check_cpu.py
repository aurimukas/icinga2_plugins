#!/opt/venv/bin python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Linux CPU
Method to get Linux Machine CPU activity in %
File name: check_linux_cpu.py
Author: Aurimas NAVICKAS
Date created: 27/10/2016
Python Version: 3.5.2

Method call example:
    $ python3 check_linux_cpu.py -H localhost -c bornan -v 2c

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

OS_OIDS = {
    'check_linux_cpu': '.1.3.6.1.2.1.25.3.3.1.2',
    'check_sun_cpu': '.1.3.6.1.4.1.2021.11.11.0',
    'check_windows_cpu': '.1.3.6.1.2.1.25.3.3.1.2',
    'check_fortinet_cpu': '.1.3.6.1.4.1.12356.101.4.1.3.0',
    'check_fortinet_5103_cpu': '.1.3.6.1.4.1.12356.106.4.1.2.0',
    'check_cisco_cpu': '.1.3.6.1.4.1.9.2.1.57.0',
    'check_cisco_nexus_cpu': '.1.3.6.1.4.1.9.9.305.1.1.1.0',
    'check_cisco_asa_cpu': '.1.3.6.1.4.1.9.9.109.1.1.1.1.4',
    'check_alteon_cpu': '.1.3.6.1.4.1.1872.2.5.1.2.2.3'
}

PERFDATA = {
    'oids': [],
    'data': {
        'alert_cpu_percent': {'oid': None, 'value': None, 'index_label': None}
    }
}


class CheckCPU(RequestManager):

    def __init__(self, host, port, community, version, system):
        super(CheckCPU, self).__init__(host, port, community, version)

        self.system = system
        if system in OS_OIDS:
            PERFDATA['oids'].append(OS_OIDS[system])
        else:
            PERFDATA['oids'].append(OS_OIDS[0])

    def probe(self):
        cpus = []
        self.request.fetch_table(cpus, PERFDATA['oids'])

        if len(cpus):
            PERFDATA['data']['alert_cpu_percent']['value'] = sum(float(r.value) for r in cpus) / len(cpus)

        return self.yield_metrics(PERFDATA['data'])


@guarded
def main():
    # Base function which is calling main Monitoring functions
    args = RequestManager.default_args('Check CPU')  # Initiating default args

    # Adding some extra args needed for this method
    args.add_argument('--sys', '-s', required=True, type=str, help='System Name')

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
        CheckCPU(pargs.host, pargs.port, pargs.community, pargs.version, pargs.sys),
        *resources
    )
    check.main(pargs.verbose)

if __name__ == '__main__':
    main()
