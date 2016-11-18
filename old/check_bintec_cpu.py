#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class BintecCpu(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.272.4.17.4.1.1.18.1.0'
        response = float(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_cpu_percent',
                                  100 - response,
                                  None,
                                  context='alert_cpu_percent')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Bintec.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        BintecCpu(args.host,
                  args.port,
                  args.community,
                  args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
