import argparse


class SNMPSkeletton:
    @staticmethod
    def default_args(description,
                     port=161,
                     version=2,
                     warning=80.0,
                     critical=90.0):
        argp = argparse.ArgumentParser(
          description=description,
          formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        argp.add_argument('--host', '-H',
                          required=True,
                          help='Host target')
        argp.add_argument('--port', '-p',
                          default=port,
                          type=int,
                          help='Port')
        argp.add_argument('--version', '-v',
                          default=version,
                          help='SNMP Version')
        argp.add_argument('--community', '-C',
                          help='SNMP Community',
                          default='bornan')
        argp.add_argument('--warning', '-w',
                          default=warning,
                          type=float,
                          help='Warning')
        argp.add_argument('--critical', '-c',
                          default=critical,
                          type=float,
                          help='Critical')
        return argp
