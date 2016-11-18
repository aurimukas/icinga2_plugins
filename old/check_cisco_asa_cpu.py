#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoAsaCpu(SNMPProbe):
    def probe(self):
        oid = '1.3.6.1.4.1.9.9.109.1.1.1.1.4'
        cpu_values = 0
        i = 0
        request = self.argoss_snmp.snmp_table(oid)
        for response in request:
            i += 1
            cpu_values += int(response.value)
        if i == 0:
            raise nagiosplugin.CheckError('CPU not available')
        yield nagiosplugin.Metric('alert_cpu_percent',
                                  round(cpu_values / i),
                                  None,
                                  context='alert_cpu_percent')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Cisco ASA.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoAsaCpu(args.host,
                    args.port,
                    args.community,
                    args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
