#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin
import re


class CiscoNexusTemp(SNMPProbe):
    def probe(self):
        oid_desc = '1.3.6.1.2.1.47.1.1.1.1.2'
        oid_status = '1.3.6.1.4.1.9.9.91.1.1.1.1.5'
        oid_value = '1.3.6.1.4.1.9.9.91.1.1.1.1.4'
        temps = 0.0
        i = 0

        request = self.argoss_snmp.snmp_table(oid_desc)
        oid_desc_found = {}
        for response in request:
            if re.search("module-(\d+) (CPU\dCORE\d)",
                         str(response.value)) is not None:
                temps += float(self.argoss_snmp.fetch_oid
                               (oid_value + "." + response.oid_index))
                i += 1
                if int(self.argoss_snmp.fetch_oid
                       (oid_status + "." + response.oid_index)) != 1:
                    raise nagiosplugin.CheckError
                    (response.value + ': Bad status')
                if i == 0:
                    raise nagiosplugin.CheckError('Temperature not available')
        yield nagiosplugin.Metric('alert_temp',
                                  round(temps/i),
                                  context='alert_temp')


def main():
    argp = SNMPSkeletton.default_args('Check temperature on Cisco Nexus.')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        CiscoNexusTemp(args.host,
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
