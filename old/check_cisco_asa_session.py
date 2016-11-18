#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoAsaSession(SNMPProbe):
    def probe(self):
        oid_ras = '1.3.6.1.4.1.9.9.392.1.3.1.0'
        oid_ipsec = '1.3.6.1.4.1.9.9.171.1.3.1.1.0'
        oid_ssl = '1.3.6.1.4.1.3076.2.1.2.26.1.2.0'
        session_count = 0
        varBinds = None
        ras_count = float(self.argoss_snmp.fetch_oid(oid_ras))
        ipsec_count = float(self.argoss_snmp.fetch_oid(oid_ipsec))
        ssl_count = float(self.argoss_snmp.fetch_oid(oid_ssl))

        yield nagiosplugin.Metric('ras',
                                  ras_count,
                                  None,
                                  context='ras')
        yield nagiosplugin.Metric('ipsec',
                                  ipsec_count,
                                  None,
                                  context='ipsec')
        yield nagiosplugin.Metric('ssl',
                                  ssl_count,
                                  None,
                                  context='ssl')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Cisco ASA.')
    args = argp.parse_args()
    check = nagiosplugin.Check(CiscoAsaSession(args.host,
                                               args.port,
                                               args.community,
                                               args.version),
                               nagiosplugin.ScalarContext('ras',
                                                          args.warning,
                                                          args.critical),
                               nagiosplugin.ScalarContext('ipsec',
                                                          args.warning,
                                                          args.critical),
                               nagiosplugin.ScalarContext('ssl',
                                                          args.warning,
                                                          args.critical))
    check.main()

if __name__ == '__main__':
    main()
