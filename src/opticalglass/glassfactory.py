#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" Factory interface and central library for optical glass catalogs

    The glassfactory module is intended to be the primary method by which glass
    instances are created. The :func:`create_glass` is the public factory
    function for this purpose.

    OpticalGlass provides a common API to a number of different optical material data sources. These include

    - interfaces to vendor supplied Excel spreadsheets with glass data.
    - ability to import material files in the Zemax .agf data format.
    - ability to import material data from the |RII|_ database.

    These and other sources of data are organized into libraries. Each library contains one or more catalogs, and each catalog contains one or more glasses. The glass catalog of particular vendors (e.g. Hoya, Ohara, Schott) will be found in multiple libraries. The user can control the order in which the libraries are searched, as well as the order of the catalogs available from each library.

    The global variable |og_glass_libs| is an instance of the :class:`CentralGlassLibrary` class that contains the various libraries and catalogs. 
    
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

from . import xls_glass
from . import agf_glass as agf
from . import glasserror as ge
from . import rindexinfo
from .opticalmedium import OpticalMedium
from .glasslibs import (GlassLibrary, GlassCatalog, GlassCatalogBase, 
                        calc_glass_map_arrays)


logger = logging.getLogger(__name__)


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


class CustomGlassCatalog(GlassCatalogBase):

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


def create_glass(*name_catalog) -> OpticalMedium:
    """ Factory function returning a catalog glass instance.
    
    The create_glass function searches the libraries and catalogs for the specified glass name and catalog, and returns an instance of the glass if found. If the glass is not found, a GlassNotFoundError is raised. If the catalog is not found, a GlassCatalogNotFoundError is raised.

    The input argument list can take several forms:

        - a single string argument will be split based on ',' to separate the glass name, catalog and library. For example, "N-BK7,Schott,xls" would specify the glass "N-BK7" in the "Schott" catalog in the vendor 'xls' library.
    
    The output of the split will be processed as follows:
        - 1 string argument: glass_name
        - 2 string arguments: glass_name, catalog_name
        - 3 string arguments: glass_name, catalog_name, library.

    If 2 arguments are used and the catalog is "rindexinfo", the "name" field 
    is taken as a URL or filepath to a material in the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database.

    
    Arguments:
        *name_catalog: tuple of 1, 2 or 3 input items

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
        GlassNotFoundError: if name isn't in the specified catalog

    """
    def _create_glass(gname: str, catalog: Optional[str] = None, 
                      library: Optional[str] = None) -> OpticalMedium:
        if catalog == "rindexinfo":
            material = rindexinfo.create_glass(gname)
            og_glass_libs['rii']['rindexinfo'][gname] = material
            return material
        else:
            if library is not None:
                lib = og_glass_libs[library]
                if catalog in lib:
                    return lib[catalog].create_glass(gname)
                else:
                    raise ge.GlassCatalogNotFoundError(catalog)
            else:
                gla_paths = og_glass_libs.find_path_to_glass(gname)
                if len(gla_paths) == 0:
                    raise ge.GlassNotFoundError(catalog, gname)
                else:
                    for path in gla_paths:
                        gla, cat, lib = path
                        if catalog is None:
                            glass_cat = og_glass_libs[lib][cat]
                            return glass_cat.create_glass(gname)
                        elif catalog.casefold() == cat.casefold():
                            glass_cat = og_glass_libs[lib][catalog]
                            return glass_cat.create_glass(gname)
                    raise ge.GlassCatalogNotFoundError(catalog)

    num_args = len(name_catalog)
    if num_args == 1:
        name_catalog = name_catalog[0].split(',')
        num_args = len(name_catalog)

    catalog = library = None
    if num_args == 3:
        name, catalog, library = name_catalog
    elif num_args == 2:
        name, catalog = name_catalog
    else:
        name = name_catalog[0]

    if isinstance(name, str):
        name = name.strip()
    if isinstance(catalog, str):
        catalog = catalog.strip()

    if isinstance(catalog, list):
        for cat in catalog:
            try:
                glass = _create_glass(name, cat.strip(), library)
            except ge.GlassError:
                continue
            else:
                return glass
        logger.info(f'glass {name} not found in {catalog}')
        raise ge.GlassNotFoundError(catalog, name)
    else:
        return _create_glass(name, catalog, library)

#: list of library names to be included in the central glass library. The order of the libraries in this list determines the search order when looking for glasses. 
libraries = ['user', 'xls', 'agf', 'rii', 'robb']

class CentralGlassLibrary(GlassLibrary):
    """ Instantiates the :data:`libraries` list to create the central library, :data:`og_glass_libs`. """
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
                    xls_lib = xls_glass.get_xls_lib()
                    glass_libs.update({lib: xls_lib})
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
                    rii_idx = search_order.index('rii') + 1
                    search_order[rii_idx:rii_idx] = list(rii_libs.keys())
                case 'robb':
                    robb_lib = xls_glass.get_robb_lib()
                    glass_libs.update({lib: robb_lib})
                case _:
                    _lib = GlassLibrary(lib, {}, [])
                    glass_libs.update({lib: _lib})

        super().__init__('glass library', glass_libs, search_order)

#: The :class:`CentralGlassLibrary` instance containing the various glass libraries and catalogs
og_glass_libs: CentralGlassLibrary = CentralGlassLibrary()
