#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class Fortinet5103Cpu(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.12356.106.4.1.2.0'
        response = int(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_cpu_percent',
                                  response,
                                  None,
                                  context='alert_cpu_percent')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Fortinet 5103.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        Fortinet5103Cpu(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning, args.critical))
    check.main()

if __name__ == '__main__':
    main()
