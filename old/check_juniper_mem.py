#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin
import re


class JuniperMem(SNMPProbe):
    def probe(self):
        oid_role = '1.3.6.1.4.1.2636.3.1.8.1.12.1.1.0.0'
        raw_role = str(self.argoss_snmp.fetch_oid(oid_role))
        if("Single" in raw_role):
            role = "single"
        elif("node" in raw_role):
            role = "node"
        else:
            raise nagiosplugin.CheckError("Error: this host is a slave.")

        data = {}
        self.argoss_snmp.gather_data(data,
                                     '1.3.6.1.4.1.2636.3.1.13.1',
                                     {5: 'operatings',
                                      6: 'status',
                                      11: 'mem'})

        operatings = {}
        for index, opDesc in data['operatings'].items():
            if(role == "single"):
                m = re.search('^Routing\ Engine (\d+)$', str(opDesc))
                if m:
                    descr = 'mem_re'+m.group(1)
                    operatings[index] = [descr]
                m = re.search('^FPC:.*SPC.*\ (.*)$', str(opDesc))
                if m:
                    descr = 'mem_spc@'+m.group(1)
                    operatings[index] = [descr]
            elif("node" in role):
                m = re.search('^'+role+'\ Routing\ Engine (\d+)$', str(opDesc))
                if m:
                    descr = 'mem_re'+m.group(1)
                    operatings[index] = [descr]
                m = re.search('^'+role+'\ FPC:.*SPC.*\ (.*)$', str(opDesc))
                if m:
                    descr = 'mem_spc@'+m.group(1)
                    operatings[index] = [descr]

        total_load = 0
        for index, descr in operatings.items():
            if int(data['status'][index]) == 2:
                total_load = total_load + int(data['mem'][index])

        if not len(operatings):
            raise nagiosplugin.CheckError(
                "Impossible de trouver une carte MEM")

        alert_mem_percent = total_load / len(operatings)
        yield nagiosplugin.Metric('alert_mem_percent',
                                  alert_mem_percent,
                                  None,
                                  context='alert_mem_percent')


def main():
    argp = SNMPSkeletton.default_args('Check memory on Juniper.')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        JuniperMem(args.host, args.port, args.community, args.version),
        nagiosplugin.ScalarContext('alert_mem_percent',
                                   args.warning, args.critical))
    check.main()

if __name__ == '__main__':
    main()
