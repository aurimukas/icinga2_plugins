#!/opt/venv/bin/python
import argoss_libs.snmp.tools
import argparse
import nagiosplugin


class FortinetSession(nagiosplugin.Resource):
    def __init__(self, host, community, port):
        self.host = host
        self.community = community
        self.port = port

    def probe(self):
        oid = '1.3.6.1.4.1.12356.101.4.1.8'
        request = argoss_libs.snmp.tools.snmp_table(oid,
                                                    self.community,
                                                    self.host,
                                                    self.port)
        value = None
        for errorIndication, errorStatus, errorIndex, varBinds in request:
            if errorIndication:
                raise nagiosplugin.CheckError(errorIndication)
            elif errorStatus:
                raise nagiosplugin.CheckError(errorStatus)
            value = varBinds[0][1]
        if value is None:
            raise nagiosplugin.CheckError('Session not found')
        yield nagiosplugin.Metric('alert_session',
                                  value,
                                  None,
                                  context='alert_session')


def main():
    argp = argparse.ArgumentParser(
      description='Check sessions on Fortinet.',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument('--host', '-H',
                      required=True,
                      help='Host target')
    argp.add_argument('--port', '-p',
                      default=161,
                      type=int,
                      help='Port')
    argp.add_argument('--community', '-C',
                      help='SNMP Community',
                      default='bornan')
    argp.add_argument('--warning', '-w',
                      type=float,
                      help='Warning')
    argp.add_argument('--critical', '-c',
                      type=float,
                      help='Critical')

    args = argp.parse_args()
    check = nagiosplugin.Check(
        FortinetSession(args.host, args.community, args.port),
        nagiosplugin.ScalarContext('alert_session',
                                   args.warning,
                                   args.critical))
    check.main()

if __name__ == '__main__':
    main()
