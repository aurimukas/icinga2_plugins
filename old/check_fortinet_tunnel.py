#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class FortinetTunnelContext(nagiosplugin.context.Context):
    def performance(self, metric, resource):
        return nagiosplugin.Performance('state_tunnel', int(metric.value))

    def evaluate(self, metric, resource):
        oid_name = '1.3.6.1.4.1.12356.101.12.2.2.1.3.' + resource.tunnel
        oid_ip = '1.3.6.1.4.1.12356.101.12.2.2.1.4.' + resource.tunnel
        name = str(resource.argoss_snmp.fetch_oid(oid_name))
        response = str(resource.argoss_snmp.fetch_oid(oid_ip))
        if metric.value == 2:
            return nagiosplugin.result.Result(
                        nagiosplugin.state.Ok,
                        'Tunnel UP (' + name + ' - ' + response + ')',
                        metric)
        else:
            return nagiosplugin.result.Result(
                        nagiosplugin.state.Critical,
                        'Tunnel DOWN (' + name + ' - ' + response + ')',
                        metric)


class FortinetTunnel(SNMPProbe):
    def __init__(self, *args, **kwargs):
        self.tunnel = str(args[-1])
        super(FortinetTunnel, self).__init__(*args[:-1], **kwargs)

    def probe(self):
        oid_status = '1.3.6.1.4.1.12356.101.12.2.2.1.20.' + self.tunnel
        status = int(self.argoss_snmp.fetch_oid(oid_status))

        yield nagiosplugin.Metric('state_tunnel',
                                  status,
                                  context='state_tunnel')


def main():
    argp = SNMPSkeletton.default_args('Check tunnel sessions on Fortinet.')
    argp.add_argument('--tunnel', '-T',
                      type=int,
                      required=True,
                      help='Oid tunnel Indice')

    args = argp.parse_args()
    check = nagiosplugin.Check(
        FortinetTunnel(args.host, args.port, args.community,
                       args.version, args.tunnel),
        FortinetTunnelContext('state_tunnel'))
    check.main()

if __name__ == '__main__':
    main()
