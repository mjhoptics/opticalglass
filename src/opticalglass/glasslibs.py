#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2026 Michael J. Hayford
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

import numpy as np

from typing import Any, Optional
from abc import abstractmethod

from opticalglass.spectral_lines import get_wavelength
from opticalglass import buchdahl
from opticalglass import util
from opticalglass.caselessDictionary import CaselessDictionary

logger = logging.getLogger(__name__)


class GlassLibrary():
    """ A collection of libs or catalogs. """
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
        return list(self._lib.items())

    def keys(self):
        return list(self._lib.keys())

    def values(self):
        return list(self._lib.values())
        
    def __iter__(self):
        def gen() -> Any:
            """ generator for the library items in search order """
            for key in self.search_order:
                yield self._lib[key]

        self._g = gen()
        return self
    
    def __next__(self) -> Any:
        return next(self._g)

    def find_path(self, gname) -> list[str]:
        """ find the path to the glass `gname` in the library

        Args:
            gname (str): the glass name to find

        Returns:
            list[str]: the path to the glass as a list of library/catalog names
        """
        for lib_key in self.search_order:
            lib = self._lib[lib_key]
            if gname in lib:
                try:
                    lib_path = lib.find_path(gname)
                except AttributeError:  # lib is actually a catalog
                    return [lib.name, self.name]
                else:
                    lib_path.append(self.name)
                    return lib_path
        return []
    
    def find_glass(self, gname) -> Optional['OpticalMedium']:
        """ find the path to the glass `gname` in the library

        Args:
            gname (str): the glass name to find

        Returns:
            list[str]: the path to the glass as a list of library/catalog names
        """
        glass = None
        for lib_key in self.search_order:
            lib = self._lib[lib_key]
            if gname in lib:
                try:
                    glass = lib.find_glass(gname)
                except AttributeError:  # lib is actually a catalog
                    return lib.create_glass(gname, lib.name)
                else:
                    break
        return glass
    
    def find_catalog(self, cat_name: str) -> list['GlassCatalogProto']:
        """ find all occurences of `cat_name` in the library

        Args:
            cat_name (str): the glass catalog to find

        Returns:
            list[str]: the path to the glass as a list of library/catalog names
        """
        def find_catalogs(library, cat_name: str, cat_list):
            for lib_key in library.search_order:
                lib = library._lib[lib_key]
                if lib.name.lower() == cat_name_lc:
                    cat_list.append(lib)
                    continue
                if cat_name in lib:
                    cat_list = find_catalogs(lib, cat_name, cat_list)
            return cat_list
        
        cat_list = []
        cat_name_lc = cat_name.lower()
        return find_catalogs(self, cat_name, cat_list)


class GlassCatalogProto():
    """ Prototype for a glass catalog. """
    @abstractmethod
    def __contains__(self, gname: str) -> bool:
        pass

    @abstractmethod
    def __getitem__(self, key: str) -> Any:
        pass

    @abstractmethod
    def create_glass(self, gname: str, gcat: str) -> 'OpticalMedium':
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
    
    def create_glass(self, gname: str, gcat: str) -> 'OpticalMedium':
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
