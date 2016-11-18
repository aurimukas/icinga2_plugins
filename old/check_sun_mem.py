#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class SunMem(SNMPProbe):
    def probe(self):
        oid_totalmem = '1.3.6.1.4.1.2021.4.5.0'
        oid_availmem = '1.3.6.1.4.1.2021.4.6.0'
        alert_mem = 100 - (
            float(self.argoss_snmp.fetch_oid(oid_availmem)) *
            100 /
            float(self.argoss_snmp.fetch_oid(oid_totalmem)))
        yield nagiosplugin.Metric('alert_mem',
                                  float(round(alert_mem, 2)),
                                  context='alert_mem')
        oid_totalswap = '1.3.6.1.4.1.2021.4.3.0'
        oid_availswap = '1.3.6.1.4.1.2021.4.4.0'
        graph_swap = 100 - (
            float(self.argoss_snmp.fetch_oid(oid_availswap)) *
            100 /
            float(self.argoss_snmp.fetch_oid(oid_totalswap)))
        yield nagiosplugin.Metric('graph_swap',
                                  float(round(graph_swap, 2)),
                                  context='graph_swap')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Sun.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        SunMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem',
                                   args.warning,
                                   args.critical,
                                   fmt_metric='alert_mem is {value}%'),
        nagiosplugin.ScalarContext('graph_swap'))
    check.main()

if __name__ == '__main__':
    main()
