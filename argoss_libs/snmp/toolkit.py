# -*- coding: UTF-8
"""
    File name: toolkit.py
    Author: Sacha TREMOUREUX, Aurimas NAVICKAS
    Date created: 19/10/2016
    Date last modified: 19/10/2016 15:39
    Python Version: 3.5.2
"""

from nagiosplugin.error import CheckError
from easysnmp.exceptions import EasySNMPTimeoutError, EasySNMPNoSuchNameError
from easysnmp import Session

__author__ = "Aurimas NAVICKAS, Sacha TREMOUREUX"
__copyright__ = "Copyright 2016, DISIT, La Poste, France"
__version__ = "1"
__email__ = "aurimas.navickas-prestataire@laposte.fr"
__maintainer__ = "Aurimas NAVICKAS"
__status__ = "Dev"


class SNMPToolkit:
    """
    Initiate SNMP connection.

    Parameters
    ---
    host: str
      Host to fetch.
    port: int
      SNMP port.
    community: string
      SNMP community.
    version: int
      SNMP version.
    """
    def __init__(self, host, port, community, version, *args, **kwargs):
        if type(version) == str:
            version = int(version[0])
        try:
            self.session = Session(hostname=host+':'+str(port),
                                   community=community,
                                   use_numeric=True,
                                   version=version)
        except EasySNMPTimeoutError as e:
            raise CheckError(e)


    def snmp_table(self, oid):
        """
        Perform SNMP GETNEXT request and return a generator.
        As lexicographicMode is turned false, this generator
        stops itself when the end of the prefix is reached.


        Parameters
        ----
        oid: str
          SNMP OID Prefix.

        Returns
        ----
        An array containing raw data.
        """
        try:
            return self.session.walk(oid)
        except EasySNMPNoSuchNameError as e:
            raise CheckError(e)
        except EasySNMPTimeoutError as e:
            raise CheckError(e)

    def fetch_oid(self, oid):
        """
        Return an object containing high-level response from
        a SNMP GET request.
        SNMP errors are handled and raised in nagiosplugin.

        Parameters
        ----
        oid: string
          SNMP OID Prefix.

        Returns
        ----
        The response value.

        Example
        ----
        >>> float(fetch_oid('1.3.6.1.4.1.9.2.1.57.0',
                  'public', 'localhost', '161'))
        60.0
        """
        try:
            return self.session.get(oid).value
        except EasySNMPNoSuchNameError as e:
            raise CheckError(e)
        except EasySNMPTimeoutError as e:
            raise CheckError(e)

    def fetch_table(self, data, oid):
        """
        Append high-level response from a SNMP GETNEXT request into
        a data variable.
        SNMP errors are handled and raised in nagiosplugin.

        Parameters
        ----
        data: list
          List to append.
        oid: str
          SNMP OID Prefix.

        Example
        ----
        >>> data = []
        >>> fetch_table(data, '1.3.6.1.2.1.25.3.3.1.2',
                        'public', 'localhost', 161)
        >>> data
        [6,1,2]
        """
        request = self.snmp_table(oid)
        for response in request:
            data.append(response)

    def gather_data(self, data, oid, valid_sub_oids):
        """
        Perform a SNMP GETNEXT over an OID prefix, filter the
        response based on valid suboids and append it on a data variable.

        Parameters
        ----
        data: list
          List to append.
        oid: str
          SNMP OID Prefix.
        valid_sub_oids: dict<key, label>
          Sub OIDs to keep.

        Example:
        ----

        SNMP GETNEXT dummy response :
        1.3.5.5.1.1: 10
        1.3.5.5.1.2: 20
        1.3.5.5.2.1: 100
        1.3.5.5.2.2: 200
        1.3.5.5.3.1: 1000
        1.3.5.5.3.2: 2000

        data = {}
        >>> gather_data(data, '1.3.5.5', 'public', 'localhost', 161,
          {1: 'foo', 3: 'bar'})
        >>> data
        {'foo': {1: 10, 2: 20}, 'bar': {1: 1000, 2: 2000}}
        """
        for label_id in valid_sub_oids:
            if not valid_sub_oids[label_id] in data:
                data[valid_sub_oids[label_id]] = {}

            request = self.snmp_table(oid+'.'+str(label_id))
            for response in request:
                label = valid_sub_oids[label_id]
                data[label][response.oid_index] = response.value
