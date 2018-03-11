#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 13:09:15 2018

@author: Mike
"""


class GlassError(Exception):
    """ Exception raised when interrogating glass database """


class GlassNotFoundError(GlassError):
    """ Exception raised when glass name not found """
    def __init__(self, catalog, name):
        self.catalog = catalog
        self.name = name


class GlassDataNotFoundError(GlassError):
    """ Exception raised when glass data item not found """
    def __init__(self, catalog, data):
        self.catalog = catalog
        self.data = data
