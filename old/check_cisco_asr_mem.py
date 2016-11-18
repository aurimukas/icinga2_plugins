#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoAsrMem(SNMPProbe):
    def probe(self):
        oid_desc = '1.3.6.1.2.1.47.1.1.1.1.2'
        oid_indice = '1.3.6.1.4.1.9.9.109.1.1.1.1.2'
        oid_value_memfree = '1.3.6.1.4.1.9.9.109.1.1.1.1.12'
        oid_value_memtotal = '1.3.6.1.4.1.9.9.109.1.1.1.1.13'

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
                ro_free = float(self.argoss_snmp.fetch_oid(
                                   oid_value_memfree + "." + indice_found))
                ro_total = float(self.argoss_snmp.fetch_oid(
                                   oid_value_memtotal + "." + indice_found))
                ro = ro_free / ro_total * 100
                i += 1
            if str(response.oid_index) == str(oid_desc_found["fo"]):
                indice_found = ((str(response.oid)).split('.'))[-1]
                fo_free = float(self.argoss_snmp.fetch_oid
                                (oid_value_memfree + "." + indice_found))
                fo_total = float(self.argoss_snmp.fetch_oid
                                 (oid_value_memtotal + "." + indice_found))
                fo = fo_free / fo_total * 100
                i += 1
        if i == 2:
            yield nagiosplugin.Metric('alert_mem_percent',
                                      round((fo+ro)/2),
                                      context='alert_mem_percent')
        else:
            raise nagiosplugin.CheckError('Mem not found')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Cisco ASR.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoAsrMem(args.host,
                    args.port,
                    args.community,
                    args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
