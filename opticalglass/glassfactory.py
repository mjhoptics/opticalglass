#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Interfaces for commercial glass catalogs

.. codeauthor: Michael J. Hayford
"""
import logging

from . import cdgm as c
from . import hikari as hi
from . import hoya as h
from . import ohara as o
from . import schott as s
from . import sumita as su

from . import glasserror as ge

CDGM, Hikari, Hoya, Ohara, Schott, Sumita = range(6)
_cat_names = ["CDGM", "Hikari", "Hoya", "Ohara", "Schott", "Sumita"]
_cat_names_uc = [cat.upper() for cat in _cat_names]


def create_glass(name, catalog):
    """ Factory function returning a catalog glass instance.

    Arguments:
        name: glass name
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
        GlassNotFoundError: if name isn't in the specified catalog

    """
    def _create_glass(name, catalog):
        cat_name = catalog.upper()
        if cat_name == _cat_names_uc[CDGM]:
            return c.CDGMGlass(name)
        elif cat_name == _cat_names_uc[Hikari]:
            return hi.HikariGlass(name)
        elif cat_name == _cat_names_uc[Hoya]:
            return h.HoyaGlass(name)
        elif cat_name == _cat_names_uc[Ohara]:
            return o.OharaGlass(name)
        elif cat_name == _cat_names_uc[Schott]:
            return s.SchottGlass(name)
        elif cat_name == _cat_names_uc[Sumita]:
            return su.SumitaGlass(name)
        else:
            logging.info('glass catalog %s not found', catalog)
            raise ge.GlassCatalogNotFoundError(catalog)

    if isinstance(catalog, str):
        return _create_glass(name, catalog)

    else:  # treat catalog as a list
        for cat in catalog:
            try:
                glass = _create_glass(name, cat)
            except ge.GlassError:
                continue
            else:
                return glass
        logging.info('glass %s not found in %s', name, catalog)
        raise ge.GlassNotFoundError(catalog, name)


def get_glass_catalog(catalog):
    """ Function returning a glass catalog instance.

    Arguments:
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
    """
    cat_name = catalog.upper()
    if cat_name == _cat_names_uc[CDGM]:
        return c.CDGMCatalog()
    elif cat_name == _cat_names_uc[Hikari]:
        return hi.HikariCatalog()
    elif cat_name == _cat_names_uc[Hoya]:
        return h.HoyaCatalog()
    elif cat_name == _cat_names_uc[Ohara]:
        return o.OharaCatalog()
    elif cat_name == _cat_names_uc[Schott]:
        return s.SchottCatalog()
    elif cat_name == _cat_names_uc[Sumita]:
        return su.SumitaCatalog()
    else:
        logging.info('glass catalog %s not found', catalog)
        raise ge.GlassCatalogNotFoundError(catalog)
        return None


class GlassMapModel():
    """ Simple model to support Model/View architecture for Glass map views """

    def __init__(self):
        self.dataSetList = []
        self.dataSetList.append((c.CDGMCatalog(), _cat_names[CDGM]))
        self.dataSetList.append((hi.HikariCatalog(), _cat_names[Hikari]))
        self.dataSetList.append((h.HoyaCatalog(), _cat_names[Hoya]))
        self.dataSetList.append((o.OharaCatalog(), _cat_names[Ohara]))
        self.dataSetList.append((s.SchottCatalog(), _cat_names[Schott]))
        self.dataSetList.append((su.SumitaCatalog(), _cat_names[Sumita]))

    def get_data_at(self, i, **kwargs):
        return self.dataSetList[i][0].glass_map_data(**kwargs)

    def get_data_set_label_at(self, i):
        return self.dataSetList[i][1]
