#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class AlteonCpu(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.1872.2.5.1.2.2.3.0'
        response = float(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_cpu_percent',
                                  response,
                                  None,
                                  context='alert_cpu_percent')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Alteon.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        AlteonCpu(args.host,
                  args.port,
                  args.community,
                  args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
