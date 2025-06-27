#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Interfaces for commercial glass catalogs

    The glassfactory module is intended to be the primary method by which glass
    instances are created. The :func:`create_glass` is the public factory
    function for this purpose. The public function :func:`get_glass_catalog`
    returns the glass catalog instance corresponding to the input string.

    Users may utilize the custom glass collection by using the 
    :func:`register_glass` function. Glasses, specified by name and catalog 
    name, can be used in the create_glass function. The collection may be saved 
    and restored via a json file.

.. codeauthor: Michael J. Hayford
"""
import logging

from pathlib import Path
import json_tricks

from . import glass as cat_glass
from . import glasserror as ge
from . import rindexinfo
from .opticalmedium import OpticalMedium

from .caselessDictionary import CaselessDictionary

logger = logging.getLogger(__name__)

_catalog_list = CaselessDictionary()

CDGM, Hikari, Hoya, Ohara, Schott, Sumita = range(6)
_cat_names = ["CDGM", "Hikari", "Hoya", "Ohara", "Schott", "Sumita"]
_cat_names_uc = [cat.upper() for cat in _cat_names]

__all__ = ['create_glass', 'get_glass_catalog', 'register_glass', 
           'list_custom_glasses', 'save_custom_glasses', 'load_custom_glasses']

# A place to hold user-registered glasses:
_custom_glass_registry = {}  


def list_custom_glasses():
    """Lists the glasses registered in the custom glasses dict. """
    if len(_custom_glass_registry) > 0:
        print("Medium         Catalog")
    else:
        print("None")

    for name, cat in _custom_glass_registry.keys():
        print(f"{name:12s}   {cat:10s}")


def register_glass(medium: OpticalMedium):
    """
    Registers a custom optical glass medium in the internal registry.

    This function adds a user-defined `OpticalMedium` instance to the custom 
    glass registry, allowing it to be referenced and used elsewhere in the 
    application. The medium is indexed by a tuple of its name and catalog name. 
    If the catalog name is new, it is also added to the list of known catalog 
    names (both in original and uppercase forms).

    Parameters:
        medium (OpticalMedium): The optical medium instance to register. Must be an instance
            of the `OpticalMedium` class, and have a valid `name` and `catalog_name`.

    Raises:
        TypeError: If `medium` is not an instance of `OpticalMedium`.

    Side Effects:
        - Updates the `_custom_glass_registry` dictionary with the new medium.

    Example:
        >>> custom_medium = OpticalMedium(name="MyGlass", catalog_name="CustomCat", ...)
        >>> register_glass(custom_medium)
        >>> # Now `custom_medium` can be accessed via name and catalog
        >>> glass = create_glass("MyGlass,CustomCat")
    """
    key = (medium.name(), medium.catalog_name())
    if not isinstance(medium, OpticalMedium):
        raise TypeError('medium must be an instance of OpticalMedium')
    _custom_glass_registry[key] = medium
    if medium.catalog_name() not in _cat_names:
        _cat_names.append(medium.catalog_name())
        _cat_names_uc.append(medium.catalog_name().upper())


class CustomGlassCatalog:
    def __init__(self, cat):
        self.catalog_name = cat
        self.glass_list = [
            # should return (gname_decode, gname, catalog) but gname_decode
            # may not be defined for custom glasses. 
            # gname_decode is supposed to be group_num, prefix, suffix. 
            (('__NA__', '', ''), name, cat) for name, cat in _custom_glass_registry.keys()
            if cat == cat
        ]


def save_custom_glasses(dirname: str|Path):
    '''
    Save the custom glasses to the specified directory.
    '''
    dirpath = Path(dirname)
    if not dirpath.exists():
        dirpath.mkdir()

    filename = dirpath / 'custom_glasses.json'

    # json only supports dicts with str keys, not tuples.
    # Save glasses in a list.
    export_glasses = [val for val in _custom_glass_registry.values()]
    with open(filename, 'w') as f:
        json_tricks.dump(export_glasses, f, indent=4)


def load_custom_glasses(dirname: str|Path):
    '''
    Load custom glasses from the specified directory.
    '''
    dirpath = Path(dirname)
    if not dirpath.exists():
        raise FileNotFoundError(f'Directory {dirname} does not exist')
    
    filename = dirpath / 'custom_glasses.json'

    if filename.exists():
        imported_glasses = []
        with open(filename, 'r') as f:
            imported_glasses = json_tricks.load(f)
        for medium in imported_glasses:
            register_glass(medium)
    else:
        import os
        for root, _, files in os.walk(dirname):
            for filename in files:
                if filename.endswith('.json'):
                    with open(os.path.join(root, filename), 'r') as f:
                        medium = json_tricks.load(f)
                        register_glass(medium)


def create_glass(*name_catalog):
    """ Factory function returning a catalog glass instance.

    The input argument list can take several forms:

        - 1 string argument in the form 'glass_name,catalog_name'
        - 2 arguments. The first is a string glass name. The second is a
          string or list of strings of catalog names.
    
    If 2 arguments are used and the catalog is "rindexinfo", the "name" field 
    is taken as a URL or filepath to a material in the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database.

    Arguments:
        *name_catalog: tuple of 1 or 2 input items

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
        GlassNotFoundError: if name isn't in the specified catalog

    """
    def _create_glass(name, catalog):
        if catalog == "rindexinfo":
            return rindexinfo.create_glass(name)
        elif (name, catalog) in _custom_glass_registry:  # for custom glasses
            return _custom_glass_registry[(name, catalog)]
        else:
            gn_decode = cat_glass.decode_glass_name(name)
            if catalog not in _catalog_list:
                try:
                    cat = get_glass_catalog(catalog)
                except ge.GlassError as gerr:
                    raise gerr
            if catalog in _catalog_list:
                try:
                    # Lookup the decoded glass name. This avoids some problems
                    # with how design programs not exactly matching the
                    # manufacturer's names.
                    gn, gc = _catalog_list[catalog].glass_lookup[gn_decode]
                except KeyError:
                    raise ge.GlassNotFoundError(catalog, name)
                else:
                    return _catalog_list[catalog].create_glass(gn, gc)
            elif "Robb1983" in catalog:
                return cat_glass.Robb1983Catalog().create_glass(name, catalog)
            else:
                logger.info('glass catalog %s not found', catalog)
                raise ge.GlassCatalogNotFoundError(catalog)

    if len(name_catalog) == 2:
        name, catalog = name_catalog
    else:
        name, catalog = name_catalog[0].split(',')
    if isinstance(name, str):
        name = name.strip()

    if isinstance(catalog, str):
        return _create_glass(name, catalog.strip())

    else:  # treat catalog as a list
        for cat in catalog:
            try:
                glass = _create_glass(name, cat.strip())
            except ge.GlassError:
                continue
            else:
                return glass
        logger.info('glass %s not found in %s', name, catalog)
        raise ge.GlassNotFoundError(catalog, name)


def get_glass_catalog(cat_name, mod_name=None, cls_name=None):
    """ Function returning a glass catalog instance.

    Arguments:
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
    """
    if cat_name in _catalog_list:
        return _catalog_list[cat_name]
    elif cat_name in [cat for _, cat in _custom_glass_registry.keys()]:
        return CustomGlassCatalog(cat_name)
    else:
        try:
            if "Robb1983" in cat_name:
                glass_cat = cat_glass.glass_catalog_factory(
                    cat_name,
                    mod_name='opticalglass.glass',
                    cls_name='Robb1983Catalog')
            else:
                glass_cat = cat_glass.glass_catalog_factory(cat_name)
        except ge.GlassError as gerr:
            raise gerr
        else:
            _catalog_list[cat_name] = glass_cat
            return glass_cat


def fill_catalog_list(cat_list=None):
    """ Given a list of catalog names, populate the _catalog_list with them. """
    if cat_list is None:
        cat_list = _cat_names
    for cat in cat_list:
        get_glass_catalog(cat)
    return _catalog_list
