from .toolkit import SNMPToolkit
import nagiosplugin


class SNMPProbe(nagiosplugin.Resource):
    def __init__(self, host, port, community, version, *args, **kwargs):
        self.host = host
        self.community = community
        self.version = version
        self.port = port
        self.argoss_snmp = SNMPToolkit(self.host, self.port, self.community, self.version, *args, **kwargs)
