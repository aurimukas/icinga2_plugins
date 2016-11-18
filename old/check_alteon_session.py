#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class AlteonSession(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.1872.2.5.4.2.5.4.0'
        response = int(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_session',
                                  response,
                                  None,
                                  context='alert_session')


def main():
    argp = SNMPSkeletton.default_args('Check sessions on Alteon.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        AlteonSession(args.host,
                      args.port,
                      args.community,
                      args.version),
        nagiosplugin.ScalarContext('alert_session',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
