#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class AlteonMem(SNMPProbe):
    def probe(self):
        oid_total = '1.3.6.1.4.1.1872.2.5.1.2.8.1.0'
        oid_free = '1.3.6.1.4.1.1872.2.5.1.2.8.3.0'
        total_mem = float(self.argoss_snmp.fetch_oid(oid_total))
        free_mem = float(self.argoss_snmp.fetch_oid(oid_free))
        yield nagiosplugin.Metric('alert_mem_percent',
                                  100 - (free_mem * 100 / total_mem),
                                  None,
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Alteon.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        AlteonMem(args.host,
                  args.port,
                  args.community,
                  args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
