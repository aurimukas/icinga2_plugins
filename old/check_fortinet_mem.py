#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class FortinetMem(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.12356.101.4.1.4.0'
        response = int(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_mem_percent',
                                  response,
                                  None,
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Fortinet.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        FortinetMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning, args.critical))
    check.main()

if __name__ == '__main__':
    main()
