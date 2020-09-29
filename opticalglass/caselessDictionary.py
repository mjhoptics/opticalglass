#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Dictionary that enables case insensitive searching

    Borrowed from https://gist.github.com/babakness/3901174 and modified to
    work with Python 3 dicts.

.. Created on Thu Sep 24 13:39:31 2020

.. codeauthor: Michael J. Hayford
"""


class CaselessDictionary(dict):
    """Dictionary that enables case insensitive searching while preserving case
    sensitivity when keys are listed, ie, via keys() or items() methods.

    Works by storing a lowercase version of the key as the new key and stores
    the original key-value pair as the key's value (values become
    dictionaries).
    """

    def __init__(self, initval={}):
        if isinstance(initval, dict):
            for key, value in iter(initval.items()):
                self.__setitem__(key, value)
        elif isinstance(initval, list):
            for (key, value) in initval:
                self.__setitem__(key, value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())['val']

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), {'key': key, 'val': value})

    def get(self, key, default=None):
        try:
            v = dict.__getitem__(self, key.lower())
        except KeyError:
            return default
        else:
            return v['val']

    def has_key(self, key):
        if self.get(key):
            return True
        else:
            return False

    def items(self):
        return [(v['key'], v['val']) for v in iter(dict.values(self))]

    def keys(self):
        return [v['key'] for v in iter(dict.values(self))]

    def values(self):
        return [v['val'] for v in iter(dict.values(self))]
