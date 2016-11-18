#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class CiscoMem(SNMPProbe):
    def load_memory(self):
        data = {}
        memory = {'used': 0, 'free': 0}
        self.argoss_snmp.gather_data(data,
                                     '1.3.6.1.4.1.9.9.221.1.1.1.1',
                                     {6: 'valid',
                                      18: 'used',
                                      20: 'free'})
        self.argoss_snmp.gather_data(data,
                                     '1.3.6.1.4.1.9.9.48.1.1.1',
                                     {4: 'valid',
                                      5: 'used',
                                      6: 'free'})
        for label in data:
            if label != 'valid':
                for value in data[label]:
                    if int(data['valid'][value]) == 1:
                        memory[label] = (int(memory[label]) +
                                         int(data[label][value]))
        try:
            return (
                memory['used'],
                memory['used']+memory['free'],
                round(100*(memory['used']/(memory['free']+memory['used'])), 2))
        except ZeroDivisionError:
            raise nagiosplugin.CheckError('Memory pool not available')

    def probe(self):
        try:
            mem_used, mem_total, alert_mem_percent = self.load_memory()
        except ValueError:
            raise nagioslugin.CheckError(ValueError)
        yield nagiosplugin.Metric('alert_mem_percent',
                                  alert_mem_percent,
                                  None,
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Cisco.')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        CiscoMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning, args.critical),
        nagiosplugin.ScalarContext('mem_used'),
        nagiosplugin.ScalarContext('mem_total'))
    check.main()

if __name__ == '__main__':
    main()
