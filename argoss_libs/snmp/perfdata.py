# -*- coding: utf-8 -*-


class PerfDataItem(object):
    TYPES = {
        '%i': int,
        '%f': float,
        '%s': str,
        '%b': bytes
    }

    def __init__(self, key=None, oid=None, value=0, index_label=None, priority=0, calculation=False, value_type='%i',
                 return_value=False, context=False):
        if not key:
            raise AttributeError('No key value provided')

        self.key = key
        self.oid = oid
        self.value = value
        self.index_label = index_label
        self.priority = priority
        self.calculation = calculation
        self.return_value = return_value
        self.context = context
        if value_type in self.TYPES:
            self.value_type = value_type
        else:
            raise TypeError('Type is not defined in default TYPES dict.')

    def __call__(self, *args, **kwargs):
        try:
            value = self.TYPES[self.value_type](self.value)
            if self.value_type == '%f':
                value = round(value, 2)
            return value
        except Exception:
            return self.value

    def __repr__(self):
        return "{0}: (oid: {1}, value: {2}, index: {3}, return: {4})".format(self.key, self.oid, self.value,
                                                                             self.index_label, self.return_value)
