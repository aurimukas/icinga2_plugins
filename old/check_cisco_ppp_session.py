#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoPPPSession(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.9.10.24.1.1.4.1.3.2'
        alert_ppp_session = int(self.argoss_snmp.fetch_oid(oid))
        yield nagiosplugin.Metric('alert_ppp_session',
                                  alert_ppp_session,
                                  None,
                                  context='alert_ppp_session')


def main():
    argp = SNMPSkeletton.default_args('Check PPP Sessions on Cisco.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoPPPSession(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_ppp_session',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
