# -*- coding: UTF-8
"""
    File name: helpers.py
    Author: Aurimas NAVICKAS
    Date created: 19/10/2016
    Date last modified: 24/10/2016 09:56
    Python Version: 3.5.2
"""
import _pickle as cPickle

__author__ = "Aurimas NAVICKAS"
__copyright__ = "Copyright 2016, DISIT, La Poste, France"
__version__ = "1"
__email__ = "aurimas.navickas-prestataire@laposte.fr"
__maintainer__ = "Aurimas NAVICKAS"
__status__ = "Dev"


def pickle_data(data=None, protocol=2):
    """
    Pickle data

    :param data: Data to pickle
    :param protocol: Pickle compression protocol
    :return: Pickled data
    """
    if data:
        return cPickle.dumps(data, protocol=protocol)


def unpickle_data(data=None):
    """
    Unpickle data

    :param data: Pickled data
    :return: Unpickled data
    """
    if data:
        return cPickle.loads(data)


def decode_from_b(value=None):
    """
    Decode Bytes Value to String

    :param value: Bytes value
    :return: Decoded String
    """
    if value and isinstance(value, bytes):
        return value.decode('unicode_escape')

    return value


def strip_string(s):
    """
    Strip strings from non-ASCII chars

    :param s: String to strip
    :return: Stripped string
    """
    return "".join(i for i in s if 31 < ord(i) < 127)


def camelize(phrase):
    """
    Convert string to Camel Case string

    :param phrase: String to Camel Case
    :return: Camel Case string

    Example:

    >>> camelize("string_to_camelize")
    "StringToCamelize"
    """
    return ''.join(x.capitalize() or '_' for x in phrase.split('_'))
