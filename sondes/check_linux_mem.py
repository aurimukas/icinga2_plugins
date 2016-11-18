#!/opt/venv/bin/python3
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Linux Memory
Method to Monitor Linux Machine's Memory
File name: check_linux_mem.py
Author: Aurimas NAVICKAS
Date created: 03/11/2016
Python Version: 3.5.2
"""
import importlib

rm = importlib.import_module('.request_manager', 'argoss_libs.snmp')
pd_class = importlib.import_module('.perfdata', 'argoss_libs.snmp')
PerfDataItem = pd_class.PerfDataItem
snmp_nagios = importlib.import_module('.snmp_nagios', 'argoss_libs.snmp')
nagios = importlib.import_module('nagiosplugin')

logging = importlib.import_module('logging')
pd = importlib.import_module('pandas')

_log = logging.getLogger('nagiosplugin')

__author__ = "Aurimas NAVICKAS"


class CheckLinuxMem(rm.RequestManager):
    """
    Check Linux Machine's Memory Metrics Method
    """

    def __init__(self, params, *args, **kwargs):
        """
        Class initialization.

        :param params: Args list to pass to argsParser.
        :param args: Extra Args
        :param kwargs: Extra kwargs
        """
        # Getting default args defined in RequestManager Class
        argsp = self.default_args("Check Linux Memory")
        # Parsing passed params with argsParser
        self.pargs = argsp.parse_args(params)
        # Indexes primary definition (In this method indexes are static, don'ts need to be updated.)
        indexes = {
            'oids': [],
            'values': {
                'memIndex': '0'
            }
        }
        # Perfdata definition
        perfdata = [
            PerfDataItem(key='mem_total', oid='.1.3.6.1.4.1.2021.4.5', index_label='memIndex', return_value=True,
                         calculation='mem_total * 1024'),
            PerfDataItem(key='mem_free', oid='.1.3.6.1.4.1.2021.4.6', index_label='memIndex', return_value=False,
                         calculation='mem_free * 1024'),
            PerfDataItem(key='mem_used', priority=1, calculation='mem_total - mem_free', return_value=True),
            PerfDataItem(key='alert_mem_percent', priority=2, calculation='(mem_used / mem_total) * 100',
                         value_type='%f', return_value=True)
        ]

        # Init a Super Class
        super(CheckLinuxMem, self).__init__(self.pargs.host, self.pargs.port, self.pargs.community, self.pargs.version,
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
        try:
            # Updating Perfdata without indexes being updated.
            self.update_performance_data(force_update_perfdata_from_host=True, update_indexes=False)
        except Exception as e:
            raise nagios.CheckError("Memory Check Error. %s", e)

        # Evaluate calculations defined in Perfdata
        self.eval_expressions()
        # Generate Nagios Metrics list and return it
        return self.yield_metrics()
