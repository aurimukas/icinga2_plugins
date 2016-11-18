#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoNexusMem(SNMPProbe):
    def probe(self):
        oid_mem = '1.3.6.1.4.1.9.9.305.1.1.1.0'
        alert_mem = int(self.argoss_snmp.fetch_oid(oid_mem))
        yield nagiosplugin.Metric('alert_mem_percent',
                                  int(round(alert_mem)),
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Cisco Nexus.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoNexusMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning,
                                   args.critical,
                                   fmt_metric='alert_mem_percent is {value}%'))
    check.main()

if __name__ == '__main__':
    main()
