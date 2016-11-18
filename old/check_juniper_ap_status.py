#!/opt/venv/bin/python
import argparse
import nagiosplugin
import pymysql.cursors


class JuniperAPStatusContext(nagiosplugin.context.Context):
    def performance(self, metric, resource):
        if str(metric) == 'Up':
            return nagiosplugin.Performance('status_ap', 0)
        elif str(metric) == 'Down':
            return nagiosplugin.Performance('status_ap', 1)

    def evaluate(self, metric, resource):
        if str(metric) == 'Up':
            return nagiosplugin.result.Result(nagiosplugin.state.Ok,
                                              'Borne OK',
                                              metric)
        elif str(metric) == 'Down':
            return nagiosplugin.result.Result(nagiosplugin.state.Critical,
                                              'Borne KO',
                                              metric)
        else:
            raise nagiosplugin.CheckError('Unknown status')


class JuniperAPStatus(nagiosplugin.Resource):
    def __init__(self, ap):
        self.host = '203.0.54.147'
        self.ap = ap

    def fetch_status(self):
        connection = pymysql.connect(host=self.host,
                                     user='cosadmin',
                                     password='admincos',
                                     db='WIFI',
                                     charset='utf8',
                                     connect_timeout=4,
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM ap_alarms WHERE name LIKE %s'
            cursor.execute(sql, (self.ap))
            if cursor.rowcount == 0:
                raise nagiosplugin.CheckError('No equipment available')
            for row in cursor:
                if 'status' in row:
                    self.status = row['status']
                else:
                    raise nagiosplugin.CheckError('No status available')

    def probe(self):
        try:
            self.fetch_status()
        except pymysql.err.OperationalError as e:
            raise nagiosplugin.CheckError(e)
        yield nagiosplugin.Metric('status_ap',
                                  self.status,
                                  context='status_ap')


def main():
    argp = argparse.ArgumentParser(
      description='Check AP status on Juniper',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument('--ap',
                      required=True,
                      help='Access Point')

    args = argp.parse_args()
    check = nagiosplugin.Check(
        JuniperAPStatus(args.ap),
        JuniperAPStatusContext('status_ap'))
    check.main()

if __name__ == '__main__':
    main()
