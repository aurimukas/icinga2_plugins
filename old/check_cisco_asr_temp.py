#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoAsrTemp(SNMPProbe):
    def probe(self):
        indices = []
        oid_indice = '1.3.6.1.2.1.47.1.1.1.1.2'
        oid_value = '1.3.6.1.4.1.9.9.91.1.1.1.1.4'
        request = self.argoss_snmp.snmp_table(oid_indice)
        temperatures = 0.0
        i = 0
        for response in request:
            if 'Temp: PEM' in str(response.value):
                temperature = float(self.argoss_snmp.fetch_oid
                                    (oid_value + "." +
                                     str(response.oid_index)))
                temperatures += temperature
                i += 1
        if i == 0:
            raise nagiosplugin.CheckError('Temp not found')
        yield nagiosplugin.Metric('alert_temp',
                                  temperatures / i,
                                  context='alert_temp')


def main():
    argp = SNMPSkeletton.default_args('Check temperature on Cisco ASR.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoAsrTemp(args.host,
                     args.port,
                     args.community,
                     args.version),
        nagiosplugin.ScalarContext('alert_temp',
                                   args.warning,
                                   args.critical,
                                   fmt_metric='alert_temp is {value}'))
    check.main()

if __name__ == '__main__':
    main()
