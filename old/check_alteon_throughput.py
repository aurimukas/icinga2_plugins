#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class AlteonThroughput(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.1872.2.5.1.2.12.2.0'
        response = int(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_throughput',
                                  response,
                                  None,
                                  context='alert_throughput')


def main():
    argp = SNMPSkeletton.default_args('Check sessions on Alteon.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        AlteonThroughput(args.host,
                         args.port,
                         args.community,
                         args.version),
        nagiosplugin.ScalarContext('alert_throughput',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
