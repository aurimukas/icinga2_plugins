#!/opt/venv/bin/python
# -*- coding: utf-8 -*-
""" Icinga2 Plugin: Check Machine's Load
Method to Monitor Machine's Load Metrics
File name: check_load.py
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


class CheckLoad(rm.RequestManager):
    """
    Check Machine's Load Metrics Method
    """

    def __init__(self, params, *args, **kwargs):
        """
        Class initialization.

        :param params: Args list to pass to argsParser.
        :param args: Extra Args
        :param kwargs: Extra kwargs
        """
        # Indexes primary definition
        indexes = {
            'oids': ['.1.3.6.1.4.1.2021.10.1.2'],
            'values': {
                'Load-1': None,
                'Load-5': None,
                'Load-15': None
            }
        }
        # Perfdata definition
        perfdata = [
            PerfDataItem(key='load_1', oid='.1.3.6.1.4.1.2021.10.1.3', index_label='Load-1', return_value=True,
                         value_type='%f'),
            PerfDataItem(key='alert_load_5', oid='.1.3.6.1.4.1.2021.10.1.3', index_label='Load-5', return_value=True,
                         value_type='%f'),
            PerfDataItem(key='load_15', oid='.1.3.6.1.4.1.2021.10.1.3', index_label='Load-15', return_value=True,
                         value_type='%f')
        ]

        # Getting default args defined in RequestManager Class
        argsp = self.default_args("Check Linux Load")
        # Perfdata definition
        self.pargs = argsp.parse_args(params)
        # Init a Super Class
        super(CheckLoad, self).__init__(self.pargs.host, self.pargs.port, self.pargs.community, self.pargs.version,
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
            # Updating Perfdata and indexes
            self.update_performance_data(force_update_perfdata_from_host=True)
        except Exception as e:
            raise nagios.CheckError("Load Check Error. %s", e)
        # Evaluate calculations defined in Perfdata
        self.eval_expressions()
        # Generate Nagios Metrics list and return it
        return self.yield_metrics()
