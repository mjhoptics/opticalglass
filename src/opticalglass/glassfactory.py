#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Interfaces for commercial glass catalogs

    The glassfactory module is intended to be the primary method by which glass
    instances are created. The :func:`create_glass` is the public factory
    function for this purpose.

    opticalglass provides a common API to a number of different optical material data sources. These include
    - interfaces to vendor supplied Excel spreadsheets with glass data.
    - ability to import material files in the Zemax .agf data format.
    - ability to import material data from the RefractiveIndex.INFO database.

    These and other sources of data are organized into libraries. Each library contains one or more catalogs, and each catalog contains one or more glasses. The glass catalog of particular vendors (e.g. Hoya, Ohara, Schott) will be found in multiple libraries. The user can control the order in which the libraries are searched, as well as the order of the catalogs available from each library.

    The global variable og_glass_libs is an instance of the CentralGlassLibrary class that contains the various libraries and catalogs. 
    
    Users may utilize the custom glass collection by using the 
    :func:`register_glass` function. Glasses, specified by name and catalog 
    name, can be used in the create_glass function. The collection may be saved 
    and restored via a json file.

.. codeauthor: Michael J. Hayford
"""
import logging
from typing import Optional, Any

from pathlib import Path
import json_tricks

from . import glass as cat_glass
from . import agf_glass as agf
from . import glasserror as ge
from . import rindexinfo
from .opticalmedium import OpticalMedium
from .glasslibs import (GlassLibrary, GlassCatalog, GlassCatalogProto, 
                        calc_glass_map_arrays)

from .caselessDictionary import CaselessDictionary

logger = logging.getLogger(__name__)

libraries = ['user', 'agf', 'xls', 'rii', 'robb']

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
    num_glasses = 0
    for lib in og_glass_libs['user']:
        num_glasses += len(lib.catalog)
    if num_glasses > 0:
        print("Medium         Catalog")
    else:
        print("None")

    for lib in og_glass_libs['user']:
        for g in lib.catalog.values():
            print(f"{g.name():12s}   {g.catalog_name():10s}")


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
    if not isinstance(medium, OpticalMedium):
        raise TypeError('medium must be an instance of OpticalMedium')
    
    user_lib = og_glass_libs['user']
    cat_name = medium.catalog_name()
    if cat_name in user_lib:
        user_lib[cat_name].catalog.update({medium.name(): medium})
    else:
        # user_lib[cat_name] = CustomGlassCatalog(cat_name, 
        user_lib[cat_name] = GlassCatalog(cat_name, 
                                                {medium.name(): medium})


class CustomGlassCatalog(GlassCatalogProto):

    def __init__(self, catalog_name: str, catalog: dict[str, Any]):
        self.name: str = catalog_name
        self.catalog: dict[str, Any] = catalog

    def catalog_name(self):
        return self.name

    def __contains__(self, gname: str) -> bool:
        return gname in self.catalog
    
    def __getitem__(self, key: str) -> Any:
        return self.catalog[key]

    def create_glass(self, gname: str) -> OpticalMedium|None:
        """ Create an instance of the glass `gname`. """
        return self.catalog[gname]
    
    def glass_map_data(self, wvl='d', **kwargs):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        glasses = list(self.catalog.values())
        return calc_glass_map_arrays(glasses, wvl, 'F', 'C', **kwargs)


def save_custom_glasses(dirname: str|Path):
    '''
    Save the custom glasses to the specified directory.
    '''
    dirpath = Path(dirname)
    if not dirpath.exists():
        dirpath.mkdir()

    filename = dirpath / 'user_glass_lib.json'
    with open(filename, 'w') as f:
        json_tricks.dump(og_glass_libs['user'], f, indent=4)


def load_custom_glasses(dirname: str|Path):
    '''
    Load custom glasses from the specified directory.
    '''
    dirpath = Path(dirname)
    if not dirpath.exists():
        raise FileNotFoundError(f'Directory {dirname} does not exist')
    
    user_lib_path = dirpath / 'user_glass_lib.json'
    custom_lib_path = dirpath / 'custom_glasses.json'

    if user_lib_path.exists():
        with open(user_lib_path, 'r') as f:
            user_lib = json_tricks.load(f)
            og_glass_libs['user'] = user_lib
    elif custom_lib_path.exists():
        imported_glasses = []
        with open(custom_lib_path, 'r') as f:
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
    def _create_glass(gname: str, catalog: str):
        if catalog == "rindexinfo":
            material = rindexinfo.create_glass(gname)
            og_glass_libs['rii']['rindexinfo'][gname] = material
            return material
        else:
            cat_list = og_glass_libs.find_catalog(catalog)
            if len(cat_list) == 0:
                raise ge.GlassCatalogNotFoundError(catalog)
            for glass_cat in cat_list:
                if gname in glass_cat:
                    medium = glass_cat.create_glass(gname)
                    return medium
        raise ge.GlassNotFoundError(catalog, gname)

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
        return GlassCatalog(cat_name)
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

libraries = ['user', 'xls', 'agf', 
             'rii', 
            #  'rii-main', 'rii-specs', 'rii-other', 'rii-organic', 'rii-glass', 
             'robb']

class CentralGlassLibrary(GlassLibrary):
    def __init__(self, search_order: Optional[list[str]] = None):
        if search_order is None:
            search_order = list(libraries)
        glass_libs = {}
        for lib in libraries:
            match lib:
                case 'user':
                    # custom_cat = CustomGlassCatalog('custom', 
                    custom_cat = GlassCatalog('custom', 
                                                    _custom_glass_registry)
                    user_lib = GlassLibrary('user', 
                                            {'custom': custom_cat}, 
                                            ['custom'])
                    glass_libs.update({lib: user_lib})
                case 'xls':
                    glass_cats = fill_catalog_list()
                    _lib = GlassLibrary(lib, glass_cats, _cat_names)
                    glass_libs.update({lib: _lib})
                case 'agf':
                    agf_lib = agf.get_agf_lib()
                    glass_libs.update({lib: agf_lib})
                case 'rii':
                    rii_cat = GlassCatalog('rindexinfo', {})
                    rii_lib = GlassLibrary('rii', 
                                           {'rindexinfo': rii_cat}, 
                                           ['rindexinfo'])
                    glass_libs.update({lib: rii_lib})
                    rii_libs = rindexinfo.get_rii_libs()
                    glass_libs.update(rii_libs)
                    search_order.extend(rii_libs.keys())
                case 'robb':
                    robb_lib = cat_glass.get_robb_lib()
                    glass_libs.update({lib: robb_lib})
                case _:
                    _lib = GlassLibrary(lib, {}, [])
                    glass_libs.update({lib: _lib})

        super().__init__('glass library', glass_libs, search_order)

og_glass_libs: CentralGlassLibrary = CentralGlassLibrary()
