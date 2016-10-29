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


def pickle_data(data=None):
    if data:
        return cPickle.dumps(data)


def unpickle_data(data=None):
    if data:
        return cPickle.loads(data)


def get_unique_items_from_lists(*lists):
    result = []
    if len(lists):
        for l in lists:
            result = list(set(l) - set(result))

    return result

def decode_from_b(value=None):
    if value and isinstance(value, bytes):
        return value.decode('unicode_escape')

    return value
