#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class BintecMem(SNMPProbe):
    def probe(self):
        oid_total = '1.3.6.1.4.1.272.4.17.4.2.1.4'
        oid_used = '1.3.6.1.4.1.272.4.17.4.2.1.5'
        value_total = 0
        values_total = []
        value_used = 0
        values_used = []
        self.argoss_snmp.fetch_table(values_total,
                                     oid_total)
        for val in values_total:
            value_total += val.value
        self.argoss_snmp.fetch_table(values_used,
                                     oid_used)
        for val in values_used:
            value_used += val.value
        if value_total == 0:
            raise nagiosplugin.CheckError('No memory pool available')
        yield nagiosplugin.Metric('alert_mem_percent',
                                  round(value_used / value_total * 100),
                                  None,
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Bintec.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        BintecMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
