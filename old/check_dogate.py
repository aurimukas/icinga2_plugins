#!/opt/venv/bin/python
import argparse
import nagiosplugin
import requests
import re
#from bs4 import BeautifulSoup
import xmltodict


class Dogate(nagiosplugin.Resource):
    def __init__(self, url, metric):
        self.url = url
        self.metric = metric

    def probe(self):
        r = None

        proxies = {
            'http': '',
            'https': ''
        }
        try:
            r = requests.get(self.url, proxies=proxies, timeout=2)
        except requests.exceptions.ConnectionError:
            print("Connection refused")

        if r:
            """soup = BeautifulSoup(r.content, "lxml")
            parsed = soup.find(re.compile('int|real'))

            try:
                val = float(parsed['val'])
            except (KeyError, TypeError):
                raise nagiosplugin.CheckError(
                    'Value not available')"""
            parsed = xmltodict.parse(r.content)

            try:
                val = float(parsed[list(parsed.keys())[0]]['@val']) 
            except (KeyError, TypeError):
                raise nagiosplugin.CheckError('Value is not available')

            yield nagiosplugin.Metric(self.metric, val,
                                      context='alert_dogate_'+self.metric)


def main():
    argp = argparse.ArgumentParser(
      description='Check Dogate URL.',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument('--url', '-u',
                      required=True,
                      help='Dogate URL')
    argp.add_argument('--metric', '-m',
                      required=True,
                      help='Metric returned')
    argp.add_argument('--warning', '-w',
                      default=80.0,
                      type=float,
                      help='Warning')
    argp.add_argument('--critical', '-c',
                      default=90.0,
                      type=float,
                      help='Critical')

    args = argp.parse_args()
    check = nagiosplugin.Check(
        Dogate(args.url, args.metric),
        nagiosplugin.ScalarContext('alert_dogate_'+args.metric,
                                   args.warning, args.critical))

    check.main()

if __name__ == '__main__':
    main()
