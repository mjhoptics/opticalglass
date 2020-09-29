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

from . import glass as cat_glass
from . import glasserror as ge

from .caselessDictionary import CaselessDictionary

_catalog_list = CaselessDictionary({
    'CDGM': c.CDGMCatalog(),
    'Hikari': hi.HikariCatalog(),
    'Hoya': h.HoyaCatalog(),
    'Ohara': o.OharaCatalog(),
    'Schott': s.SchottCatalog(),
    'Sumita': su.SumitaCatalog(),
    })

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
        if catalog in _catalog_list:
            return _catalog_list[catalog].create_glass(name, catalog)
        elif "Robb1983" in catalog:
            return cat_glass.Robb1983Catalog().create_glass(name, catalog)
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
    if catalog in _catalog_list:
        return _catalog_list[catalog]
    else:
        logging.info('glass catalog %s not found', catalog)
        raise ge.GlassCatalogNotFoundError(catalog)
        return None
