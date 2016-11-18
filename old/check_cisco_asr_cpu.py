#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoAsrCpu(SNMPProbe):
    def probe(self):
        oid_desc = '1.3.6.1.2.1.47.1.1.1.1.2'
        oid_indice = '1.3.6.1.4.1.9.9.109.1.1.1.1.2'
        oid_value = '1.3.6.1.4.1.9.9.109.1.1.1.1.7'

        fo = 0.0
        ro = 0.0
        i = 0

        request = self.argoss_snmp.snmp_table(oid_desc)
        oid_desc_found = {}
        for response in request:
            if 'CPU 0 of module R0' in str(response.value):
                oid_desc_found["ro"] = ((str(response.oid)).split('.'))[-1]
            if 'CPU 0 of module F0' in str(response.value):
                oid_desc_found["fo"] = ((str(response.oid)).split('.'))[-1]

        request = self.argoss_snmp.snmp_table(oid_indice)

        for response in request:
            if str(response.oid_index) == str(oid_desc_found["ro"]):
                indice_found = ((str(response.oid)).split('.'))[-1]
                ro = float(self.argoss_snmp.fetch_oid
                           (oid_value + "." + indice_found))
                i += 1
            if str(response.oid_index) == str(oid_desc_found["fo"]):
                indice_found = ((str(response.oid)).split('.'))[-1]
                fo = float(self.argoss_snmp.fetch_oid
                           (oid_value + "." + indice_found))
                i += 1
        if i == 2:
            yield nagiosplugin.Metric('alert_cpu_percent',
                                      (fo+ro)/2,
                                      context='alert_cpu_percent')
        else:
            raise nagiosplugin.CheckError('CPU not found')


def main():
    argp = SNMPSkeletton.default_args('Check CPU on Cisco ASR.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoAsrCpu(args.host,
                    args.port,
                    args.community,
                    args.version),
        nagiosplugin.ScalarContext('alert_cpu_percent',
                                   args.warning,
                                   args.critical,
                                   fmt_metric='alert_cpu_percent is {value}%'))
    check.main()

if __name__ == '__main__':
    main()
