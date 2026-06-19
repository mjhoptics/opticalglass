#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2026 Michael J. Hayford
""" Interfaces for optical material data sources, catalogs, and libraries.

    The glasslibs module defines the GlassLibrary and GlassCatalog classes, which provide a common interface for accessing optical glass data from various sources. The GlassLibrary class represents a collection of glass catalogs and other libraries, while the GlassCatalog class represents a specific catalog of optical glasses. 

.. codeauthor: Michael J. Hayford
"""
import logging

import numpy as np

from typing import Any
from abc import abstractmethod
from collections.abc import MutableMapping

from opticalglass.opticalmedium import OpticalMedium
from opticalglass.spectral_lines import get_wavelength
from opticalglass import buchdahl
from opticalglass import util
from opticalglass.caselessDictionary import CaselessDictionary

logger = logging.getLogger(__name__)


class GlassCatalogBase():
    """ Prototype for a glass catalog. 
    
    A `GlassCatalogBase` defines the interface for a glass catalog, which is a collection of optical glasses. Subclasses should mix in the `Mapping` protocol to provide dictionary-like access to the glasses in the catalog. Immutable mappings are used for vendor catalogs and other imported datasets. `MutableMapping` can be used for user constructed catalogs or other types of grouping, e.g. plastics or IR materials.

    The `create_glass` method will return a subclass of `OpticalMedium` for the input glass name. The [] access will return either an `OpticalMedium` subclass or data directly related to the data source.

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
    def create_glass(self, gname: str) -> OpticalMedium:
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


class GlassLibrary(MutableMapping):
    """ A collection of libraries or catalogs. 
    
    This class acts like a dictionary of libraries or catalogs. Each entry in the `GlassLibrary` is accessed using its name as the key. The library maintains a search order for the mapped items that is used when looking for a catalog or glass. A `GlassLibrary` supports iteration and uses the search order when iterating over its contents. Libraries or catalogs can be excluded from the search by changing their active_state to False. The library can contain any number of nested libraries and catalogs, and the search will be performed recursively through the nested structure.
    
    The :meth:`find_path_to_glass` method can be used to find all paths to a specific glass in the library, and the :meth:`find_catalog` method can be used to find all occurrences of a specific catalog in the library.

    Args:
        name (str): the name of the library
        lib (dict[str, Any]): a dictionary of libraries or catalogs
        search_order (list[str]): the order used when iterating over the contents of the library
        active_cltns (list[str]): an optional list of library or catalog names that are active, i.e. included in the search. All items are active by default.

    Attributes:
        name (str): the name of the library
        active_state (dict[str, bool]): a dictionary of the entries in this library where the value is whether an entry is active or not, Only active entries are included when iterating over the library.
        search_order (list[str]): the order used when iterating over the contents of the library. The search order can omit entries in the library.
    """
    def __init__(self, name: str, lib: dict[str, Any], 
                 search_order: list[str],
                 *active_cltns: list[str],
                 ):
        self.name: str = name
        self._lib: dict[str, Any] = CaselessDictionary(lib)

        if len(active_cltns) > 0:
            self.active_cltns = active_cltns[0]
        else:
            self.active_state: dict[str, bool] = CaselessDictionary({key: True 
                                                  for key in self._lib.keys()})

        self.search_order: list[str] = search_order

    def __str__(self) -> str:
        return f"{self.name} library with {len(self._lib)} entries"
    
    @property
    def active_cltns(self) -> list[str]:
        """ list of the active entries in the library. """
        return [key for key, value in self.active_state.items() if value]

    @active_cltns.setter
    def active_cltns(self, new_active_cltns: list[str]):
        active_state = CaselessDictionary({key: False 
                                           for key in self._lib.keys()})
        for key in new_active_cltns:
            active_state[key] = True
        self.active_state = active_state

    def __getitem__(self, key: str) -> Any:
        return self._lib[key]

    def __setitem__(self, key: str, new_value: Any):
        if key not in self._lib:
            self.search_order.append(key)
            self.active_state[key] = True
        self._lib[key] = new_value

    def __delitem__(self, key: str):
        del self._lib[key]
        del self.active_state[key]
        del self.search_order[self.search_order.index(key)]

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
        
    def __iter__(self):
        def gen() -> Any:
            """ generator for the library items in search order """
            for key in self.search_order:
                if self.active_state[key]:
                    yield key

        return gen()
    
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
                    if isinstance(lib, GlassCatalogBase):
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

    def find_catalog(self, cat_name: str) -> list[
        tuple[GlassCatalogBase, list[str]]
        ]:
        """ find all occurences of `cat_name` in the library

        Args:
            cat_name (str): the glass catalog to find

        Returns:
            list[tuple[GlassCatalogBase, list[str]]]: list of tuples consisting of a `GlassCatalog` and the path to the catalog as a list of library/catalog names
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


class GlassCatalog(MutableMapping, GlassCatalogBase):
    """ A collection of `OpticalMedium`

    This is the basic implementation of the `GlassCatalogBase` protocol.

    Attributes:
        name (str): the name of the catalog
        catalog (dict[str, OpticalMedium]): a dict of `OpticalMedium` keyed by glass name

    In this implementation, the [] operator and the :meth:`create_glass` method return the same thing, an `OpticalMedium` instance for the input glass name.

    This collection is mutable, so glasses can be added, removed, or modified using the [] operator.
    """
    def __init__(self, catalog_name: str, catalog: dict[str, OpticalMedium]):
        self.name: str = catalog_name
        self.catalog: dict[str, OpticalMedium] = catalog

    def __str__(self) -> str:
        return f"{self.name} catalog with {len(self)} entries"

    def __contains__(self, gname: str) -> bool:
        return gname in self.catalog

    def __getitem__(self, key: str) -> OpticalMedium:
        return self.catalog[key]

    def __setitem__(self, key: str, new_value: OpticalMedium):
        self.catalog[key] = new_value

    def __delitem__(self, key: str):
        del self.catalog[key]
        
    def __iter__(self):
        return self.catalog.__iter__()

    def __len__(self) -> int:
        return len(self.catalog)  

    def create_glass(self, gname: str) -> OpticalMedium:
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


def calc_glass_map_arrays(glasses: list[OpticalMedium], 
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
    wl_d = get_wavelength(d_str)
    wl_F = get_wavelength(F_str)
    wl_C = get_wavelength(C_str)
    eval_wvls = [wl_d, wl_F, wl_C]
    if 'partials' in kwargs:
        wl_a, wl_b = kwargs['partials']
        wl_a = get_wavelength(wl_a)
        wl_b = get_wavelength(wl_b)
        eval_wvls = [*eval_wvls, wl_a, wl_b]
    eval_wvls = np.array(eval_wvls)

    ref_indices = []
    gnames_used = []
    for glass in glasses:
        wvls = np.array(glass.get_wl_range())
        if (np.min(eval_wvls) >= np.min(wvls) and 
            np.max(eval_wvls) <= np.max(wvls)):
            rindex_results = glass.calc_rindex(eval_wvls)
            ref_indices.append(rindex_results)
            gnames_used.append(glass.name())

    if len(ref_indices) == 0:
        return np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), []
    else:
        ref_indices = np.array(ref_indices).T
        nd = ref_indices[0]
        nF = ref_indices[1]
        nC = ref_indices[2]

        nd, coefs = buchdahl.calc_buchdahl_coords(
            nd, nF, nC, wlns=eval_wvls, **kwargs)

        if 'partials' in kwargs:
            n4 = ref_indices[3]
            n5 = ref_indices[4]
            nd, vd, PFd, Pab = util.calc_glass_constants(nd, nF, nC, n4, n5)
        else:
            vd, Pab = util.calc_glass_constants(nd, nF, nC)

        return nd, vd, Pab, coefs[0], coefs[1], gnames_used
