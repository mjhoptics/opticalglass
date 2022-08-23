#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Support for Glass catalog exception handling

.. codeauthor: Michael J. Hayford
"""


class GlassError(Exception):
    """ Exception raised when interrogating glass database """


class GlassCatalogNotFoundError(GlassError):
    """ Exception raised when glass catalog name not found """

    def __init__(self, catalog):
        self.catalog = catalog


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
