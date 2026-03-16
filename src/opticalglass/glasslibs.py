#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2026 Michael J. Hayford
""" Interfaces for optical material data sources, catalogs, and libraries.

    The glasslibs module defines the GlassLibrary and GlassCatalog classes, which provide a common interface for accessing optical glass data from various sources. The GlassLibrary class represents a collection of glass catalogs and other libraries, while the GlassCatalog class represents a specific catalog of optical glasses. 

.. codeauthor: Michael J. Hayford
"""
import logging

import numpy as np

from typing import Any, Optional
from abc import abstractmethod

from opticalglass.spectral_lines import get_wavelength
from opticalglass import buchdahl
from opticalglass import util
from opticalglass.caselessDictionary import CaselessDictionary

logger = logging.getLogger(__name__)


class GlassLibrary():
    """ A collection of libs or catalogs. 
    
    This class acts like a dictionary of libraries or catalogs. Each library or catalog is accessed by its name as the key. The library also maintains a search order for the mapped items that is used when looking for a catalog or glass. A GlassLibrary supports iteration and uses the search order when iterating over its contents. Libraries or catalogs can be excluded from the search order to limit the search to specific items. The library can contain any number of nested libraries and catalogs, and the search will be performed recursively through the nested structure.
    
    The find_path_to_glass method can be used to find all paths to a specific glass in the library, and the find_catalog method can be used to find all occurrences of a specific catalog in the library.
    """
    def __init__(self, name: str, lib: dict[str, Any], 
                 search_order: list[str]):
        self.name: str = name
        self._lib: dict[str, Any] = CaselessDictionary(lib)
        self.search_order: list[str] = search_order
        self._g: Any

    def __json_encode__(self):
        attrs = dict(vars(self))
        if hasattr(self, '_g'):
            del attrs['_g']
        return attrs

    def __getitem__(self, key: str) -> Any:
        return self._lib[key]

    def __setitem__(self, key: str, new_value: Any):
        if key not in self._lib:
            self.search_order.append(key)
        self._lib[key] = new_value

    def __len__(self) -> int:
        return len(self._lib)  
    
    def __contains__(self, key: str) -> bool:
        if key in self._lib:
            return True
        else:
            for lib_key in self.search_order:
                if key in self._lib[lib_key]:
                    return True
        return False

    def has_key(self, key):
        if self._lib.get(key):
            return True
        else:
            return False

    def items(self):
        return self._lib.items()

    def keys(self):
        return self._lib.keys()

    def values(self):
        return self._lib.values()
        
    def __iter__(self):
        def gen() -> Any:
            """ generator for the library items in search order """
            for key in self.search_order:
                yield self._lib[key]

        self._g = gen()
        return self
    
    def __next__(self) -> Any:
        return next(self._g)
    
    def find_path_to_glass(self, gname) -> list[list[str]]:
        """ find all occurances of the path to the glass `gname`

        Args:
            gname (str): the glass name to find

        Returns:
            list[list[str]]: list of paths to the glass as a list of library/catalog names
        """
        def find_paths(library, glass_name: str, path_list):
            for lib_key in library.search_order:
                lib = library._lib[lib_key]
                glasscat_path.append(lib_key)
                if glass_name in lib:
                    if isinstance(lib, GlassCatalogProto):
                        full_path = glasscat_path.copy()
                        full_path.append(glass_name)
                        full_path.reverse()
                        path_list.append(full_path)
                        glasscat_path.pop()
                        continue
                    else:
                        path_list = find_paths(lib, glass_name, path_list)
                glasscat_path.pop()
            return path_list
        
        path_list = []
        glasscat_path = []
        return find_paths(self, gname, path_list)
    
    def find_catalog(self, cat_name: str) -> list[tuple['GlassCatalogProto', list[str]]]:
        """ find all occurences of `cat_name` in the library

        Args:
            cat_name (str): the glass catalog to find

        Returns:
            list[tuple['GlassCatalogProto', list[str]]]: list of tuples consisting of a GlassCatalog and the path to the catalog as a list of library/catalog names
        """
        def find_catalogs(library, cat_name: str, cat_list):
            for lib_key in library.search_order:
                lib = library._lib[lib_key]
                glasscat_path.append(lib_key)
                if lib.name.casefold() == cat_name_cf:
                    cat_path = glasscat_path.copy()
                    cat_path.reverse()
                    cat_list.append((lib, cat_path))
                    glasscat_path.pop()
                    continue
                if cat_name in lib:
                    cat_list = find_catalogs(lib, cat_name, cat_list)
                glasscat_path.pop()
            return cat_list
        
        cat_list = []
        glasscat_path = []
        cat_name_cf = cat_name.casefold()
        return find_catalogs(self, cat_name, cat_list)


class GlassCatalogProto():
    """ Prototype for a glass catalog. 
    
    A GlassCatalogProto defines the interface for a glass catalog, which is a collection of optical glasses. 
    The create_glass method will return a subclass of OpticalMedium for the input glass name. The [] access will return either an OpticalMedium subclass or data directly related to the data source.
    The glass_map_data method will return arrays of index and dispersion data for all glasses in the catalog for a specified wavelength range. This is used to facilitate glass map displays.
    """
    @abstractmethod
    def __contains__(self, gname: str) -> bool:
        pass

    @abstractmethod
    def __getitem__(self, key: str) -> Any:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass  
    
    @abstractmethod
    def create_glass(self, gname: str) -> 'OpticalMedium':
        """ Create an instance of the glass `gname`. """
        pass

    @abstractmethod
    def glass_map_data(self, wvl='d', **kwargs):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        pass


class GlassCatalog(GlassCatalogProto):
    """ A collection of OpticalMedium."""
    def __init__(self, catalog_name: str, catalog: dict[str, 'OpticalMedium']):
        self.name: str = catalog_name
        self.catalog: dict[str, 'OpticalMedium'] = catalog

    def __contains__(self, gname: str) -> bool:
        return gname in self.catalog

    def __getitem__(self, key: str) -> Any:
        return self.catalog[key]

    def __len__(self) -> int:
        return len(self.catalog)

    def create_glass(self, gname: str) -> 'OpticalMedium':
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


def calc_glass_map_arrays(glasses: list['OpticalMedium'], 
                          d_str, F_str, C_str, **kwargs):
    """ return index and dispersion data arrays for input spectral range

    Args:
        glasses (list): input list of glass instances
        nd_str (str): central wavelength string
        nf_str (str): blue end wavelength string
        nc_str (str): red end wavelength string
        partials (tuple): kwarg if present, 2 wvls, wl4 and wl5, wl4 < wl5

    Returns:
        index, V-number, partial dispersion, Buchdahl coefficients, and
        glass names
    """
    names = [g.name()+'/'+g.catalog_name() for g in glasses]

    nd = np.array([g.rindex(d_str) for g in glasses])
    nF = np.array([g.rindex(F_str) for g in glasses])
    nC = np.array([g.rindex(C_str) for g in glasses])

    nd, coefs = buchdahl.calc_buchdahl_coords(
        nd, nF, nC, wlns=(d_str, F_str, C_str), **kwargs)

    if 'partials' in kwargs:
        wl4, wl5 = kwargs['partials']
        n4 = np.array([g.rindex(wl4) for g in glasses])
        n5 = np.array([g.rindex(wl5) for g in glasses])
        nd, vd, PFd, Pab = util.calc_glass_constants(nd, nF, nC, n4, n5)
    else:
        vd, Pab = util.calc_glass_constants(nd, nF, nC)

    return nd, vd, Pab, coefs[0], coefs[1], names
