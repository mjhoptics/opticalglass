#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Interfaces for commercial glass catalogs

.. codeauthor: Michael J. Hayford
"""
import logging

from . import cdgm as c
from . import hoya as h
from . import ohara as o
from . import schott as s

from . import glasserror as ge

CDGM, Hoya, Ohara, Schott = range(4)
_cat_names = ["CDGM", "Hoya", "Ohara", "Schott"]


def create_glass(name, catalog):
    """ Factory function returning a catalog glass instance.

    Arguments:
        name: glass name
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
        GlassNotFoundError: if name isn't in the specified catalog

    """
    cat_name = catalog.capitalize()
    glass_name = name.upper()
    if catalog.upper() == _cat_names[CDGM]:
        return c.CDGMGlass(glass_name)
    elif cat_name == _cat_names[Hoya]:
        return h.HoyaGlass(glass_name)
    elif cat_name == _cat_names[Ohara]:
        return o.OharaGlass(glass_name)
    elif cat_name == _cat_names[Schott]:
        return s.SchottGlass(glass_name)
    else:
        logging.info('Glass catalog %s not found', catalog)
        raise ge.GlassCatalogNotFoundError(catalog)
        return None


def get_glass_catalog(catalog):
    """ Function returning a glass catalog instance.

    Arguments:
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
    """
    cat_name = catalog.capitalize()
    if catalog.upper() == _cat_names[CDGM]:
        return c.CDGMGlass
    elif cat_name == _cat_names[Hoya]:
        return h.HoyaGlass
    elif cat_name == _cat_names[Ohara]:
        return o.OharaGlass
    elif cat_name == _cat_names[Schott]:
        return s.SchottGlass
    else:
        logging.info('Glass catalog %s not found', catalog)
        raise ge.GlassCatalogNotFoundError(catalog)
        return None


class GlassMapModel():
    """ Simple model to support Model/View architecture for Glass map views """
    def __init__(self):
        self.dataSetList = []
        self.dataSetList.append((c.CDGMCatalog(), _cat_names[CDGM]))
        self.dataSetList.append((h.HoyaCatalog(), _cat_names[Hoya]))
        self.dataSetList.append((o.OharaCatalog(), _cat_names[Ohara]))
        self.dataSetList.append((s.SchottCatalog(), _cat_names[Schott]))

    def get_data_at(self, i):
        return self.dataSetList[i][0].glass_map_data()

    def get_data_set_label_at(self, i):
        return self.dataSetList[i][1]
