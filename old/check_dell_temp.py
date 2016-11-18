#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class DellTemp(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.674.10892.1.700.20.1.6.1.1'
        alert_temp = float(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_temp',
                                  round(alert_temp / 10.0, 1),
                                  None,
                                  context='alert_temp')


def main():
    argp = SNMPSkeletton.default_args('Check temperature on Dell.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        DellTemp(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_temp',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
