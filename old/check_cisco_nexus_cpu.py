#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoNexusCpu(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.9.9.305.1.1.1.0'
        alert_cpu_percent = int(self.argoss_snmp.fetch_oid(oid))

        yield nagiosplugin.Metric('alert_cpu_percent',
                                  alert_cpu_percent,
                                  None,
                                  context='alert_cpu_percent')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Cisco Nexus.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoNexusCpu(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
