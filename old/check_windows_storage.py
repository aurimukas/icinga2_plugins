#!/opt/venv/bin/python
from argoss_libs.snmp.probe import SNMPProbe
from argoss_libs.snmp.skeletton import SNMPSkeletton
import nagiosplugin


class WinStorage(SNMPProbe):
    def __init__(self, *args, **kwargs):
        self.label_fs = str(args[-1])[0]
        super(WinStorage, self).__init__(*args[:-1], **kwargs)

    def load_filesystem(self):
        data = {}
        self.argoss_snmp.gather_data(data,
                                     '1.3.6.1.2.1.25.2.3.1',
                                     {3: 'label',
                                      4: 'alloc',
                                      5: 'size',
                                      6: 'used'})
        id_fs = ''
        for l in data['label']:
            data['label'][l] = str(data['label'][l])
            if(data['label'][l].split(':\\')[0].lower() ==
               self.label_fs.lower()):
                id_fs = l
        if not id_fs:
            raise nagiosplugin.CheckError('Filesystem not found')

        alloc = int(data['alloc'][id_fs])
        size = int(data['size'][id_fs])
        used = int(data['used'][id_fs])

        fs_used = used * alloc
        fs_total = size * alloc
        if fs_total == 0:
            return fs_used, fs_total, 0
        alert_fs_percent = round(100 * (used / size), 2)
        return fs_used, fs_total, alert_fs_percent

    def probe(self):
        try:
            fs_used, fs_total, alert_fs_percent = self.load_filesystem()
        except ValueError:
            return None
        yield nagiosplugin.Metric('alert_fs_percent',
                                  alert_fs_percent,
                                  None,
                                  context='alert_fs_percent')
        yield nagiosplugin.Metric('fs_used',
                                  fs_used,
                                  None,
                                  context='fs_used')
        yield nagiosplugin.Metric('fs_total',
                                  fs_total,
                                  None,
                                  context='fs_total')


def main():
    argp = SNMPSkeletton.default_args('Check storage on Windows file systems.')
    argp.add_argument('--filesystem', '-f',
                      help='ID Filesystem'),
    args = argp.parse_args()
    check = nagiosplugin.Check(
        WinStorage(args.host, args.port, args.community,
                   args.version, args.filesystem),
        nagiosplugin.ScalarContext('alert_fs_percent',
                                   args.warning, args.critical),
        nagiosplugin.ScalarContext('fs_used'),
        nagiosplugin.ScalarContext('fs_total'))
    check.main()

if __name__ == '__main__':
    main()
