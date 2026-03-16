#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interface to the the ZemaxGlass AGF file importer

.. Created on Sun Nov 14 21:03:50 2021

.. codeauthor: Michael J. Hayford
"""
from typing import Any, Optional
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d

from numpy.typing import NDArray

import ZemaxGlass as zg

from opticalglass.opticalmedium import OpticalMedium, InterpolatedMedium
from opticalglass.glasserror import GlassDBNotSupported
from opticalglass.spectral_lines import get_wavelength
from opticalglass import buchdahl
from opticalglass import util
from opticalglass.glasslibs import GlassCatalogProto, GlassLibrary
from opticalglass.caselessDictionary import CaselessDictionary

import logging
logger = logging.getLogger(__name__)


def get_glass_map_arrays(cat: 'AGFCatalog', d_str, F_str, C_str, **kwargs):
    """ return index and dispersion data arrays for input spectral range

    Args:
        cat:  an agf catalog dictglass catalog instance, source for returned data
        d_str (str): central wavelength string
        F_str (str): blue end wavelength string
        C_str (str): red end wavelength string
        partials (tuple): kwarg if present, 2 wvls, wl4 and wl5, wl4 < wl5

    Returns:
        index, V-number, partial dispersion, Buchdahl coefficients, and
        glass names
    """
    catalog = cat.catalog
    names = catalog.keys()
    wl_d = get_wavelength(d_str)
    wl_F = get_wavelength(F_str)
    wl_C = get_wavelength(C_str)
    wvls = [wl_d, wl_F, wl_C]
    if 'partials' in kwargs:
        wl_a, wl_b = kwargs['partials']
        wvls = [*wvls, wl_a, wl_b]
    wv_um = np.array(wvls)/1000.    
    ref_indices = []
    for gname, glass_rec in catalog.items():
        ref_indices.append(zg.get_dispersion(gname, cat.name, glass_rec, wv_um))

    rindex_vs_glass = np.array(ref_indices).T
    nd = rindex_vs_glass[0]
    nF = rindex_vs_glass[1]
    nC = rindex_vs_glass[2]
    nd, coefs = buchdahl.calc_buchdahl_coords(
        nd, nF, nC, wlns=(d_str, F_str, C_str), **kwargs)

    if 'partials' in kwargs:
        wl_a, wl_b = kwargs['partials']
        na = rindex_vs_glass[3]
        nb = rindex_vs_glass[4]
        nd, vd, PFd, Pab = util.calc_glass_constants(nd, nF, nC, na, nb)
    else:
        vd, Pab = util.calc_glass_constants(nd, nF, nC)

    return nd, vd, Pab, coefs[0], coefs[1], names


def summary_plots(opt_medium, opt_medium_yaml=None):
    """ plot refractive index and thruput data, when available. """
    import matplotlib.pyplot as plt
    if opt_medium_yaml is None:
        if hasattr(opt_medium, 'yaml_data'):
            opt_medium_yaml = opt_medium.yaml_data
    if opt_medium_yaml is not None:
        print(f"{[d['type'] for d in opt_medium_yaml['DATA']]}")

    plt.plot(opt_medium.wvls, opt_medium.calc_rindex(opt_medium.wvls), 
             label='ref index')

    if getattr(opt_medium, 'kvals', None) is not None:
        plt.plot(opt_medium.kvals_wvls, opt_medium.kvals, label='k value')
        plt.plot(*opt_medium.transmission_data(), label='T @ 10mm')

    plt.title(f"{opt_medium.catalog_name()}: {opt_medium.name()}")
    plt.xlabel('wavelength (nm)')

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()


class AGFCatalog(GlassCatalogProto):
    def __init__(self, catalog_name: str, catalog: dict):
        self.name = catalog_name
        self.catalog = CaselessDictionary(catalog)

    def __contains__(self, gname: str) -> bool:
        return gname in self.catalog

    def __getitem__(self, gname: str) -> Any:
        return self.catalog[gname]
        
    def create_glass(self, gname: str) -> 'AGFMedium':
        """ Create an instance of the glass `gname`. """
        return AGFMedium(gname, self.name, self.catalog[gname])

    def glass_map_data(self, wvl='d', **kwargs):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        return get_glass_map_arrays(self, wvl, 'F', 'C', **kwargs)


def get_agf_lib(agf_path: Optional[str] = None, 
                cat_list: list[str]|str = 'all') -> GlassLibrary:
    
    if agf_path is None:
        zg_path = Path(zg.__file__)
        agf_path = zg_path.parent / 'AGF_files'

    cat_list = cat_list if cat_list is not None else 'all'
    agf_library = zg.read_library(agf_path, catalog=cat_list)
    agf_cats = {cat_name: AGFCatalog(cat_name, cat_data) 
                for cat_name, cat_data in agf_library.items()}
    agf_srch = [cat_name for cat_name in agf_cats.keys()]
    agf_lib = GlassLibrary('agf', agf_cats, agf_srch)
    return agf_lib


class AGFMedium(OpticalMedium):
    """  wrapper class to ZemaxGlass """
    def __init__(self, gname, catalog, glass_rec):
        """
        Parameters
        ----------
        gname : str
            a string label returned from the name() fct.
        catalog : str
            a string label returned from the catalog_name() fct.
        glass_rec: dict
            the glass record (dict) as read from the agf file
        """

        self.label = gname
        self._catalog_name = catalog

        self.glass_rec = glass_rec
        self.abs_coefs = self.calc_absorption_coefs()

    def name(self) -> str:
        return self.label

    def catalog_name(self) -> str:
        return self._catalog_name

    def glass_code(self) -> str:
        nd = self.rindex('d')
        nF = self.rindex('F')
        nC = self.rindex('C')
        vd = (nd - 1)/(nF - nC)
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def rindex(self, wvl: float | str) -> float:
        """Returns the refractive index from the quadratic model at wvl."""
        return self.calc_rindex(get_wavelength(wvl))

    def calc_rindex(self, wv_nm: float | NDArray) -> float | NDArray:
        wv_um = wv_nm / 1000.
        indices = zg.get_dispersion(self.name(), self.catalog_name(), 
                                    self.glass_rec, wv_um)
        return indices
    
    def get_wl_range(self):
        """ returns the wavelength range in nm for the medium definition """
        wvls = 1000.0 * np.array(self.glass_rec['ld'])
        return np.min(wvls), np.max(wvls)

    def meas_rindex(self, wvl: str) -> float:
        """ returns the measured refractive index at wvl

        For `InterpolatedMedium` the measured index isn't directly known. The
        calculated index is used instead. Calling `rindex` handles the spectral 
        line conversion.
        """
        return self.rindex(wvl)

    def transmission_data(self) -> tuple[NDArray, NDArray]:
        """ returns an array of transmission data for the glass

        Returns: np.arrays of wavelength and transmission for 10mm sample
        """
        wvls = 1000.0 * np.array(self.glass_rec['it']['wavelength'])
        t_vals = np.array(self.glass_rec['it']['transmission'])
        return wvls, t_vals
    
    def calc_absorption_coefs(self) -> NDArray:
        t_vals = np.array(self.glass_rec['it']['transmission'])
        meas_thi = np.array(self.glass_rec['it']['thickness'])
        abs_coefs = -np.log(t_vals)/meas_thi
        return abs_coefs

    def summary_plots(self):
        """ plot refractive index and thruput data, when available. """
        import matplotlib.pyplot as plt

        wvl_min, wvl_max = self.glass_rec['ld'][0], self.glass_rec['ld'][1]
        wvls = 1000. * np.linspace(wvl_min, wvl_max, 100)

        plt.plot(wvls, self.calc_rindex(wvls), 
                label='ref index')

        meas_thi = self.glass_rec['it']['thickness'][0]
        t_wvls, t_vals = self.transmission_data()
        kvals = (1e-6 * t_wvls) * self.abs_coefs/ (4*np.pi)
        plt.plot(t_wvls, kvals, label='k value')
        plt.plot(t_wvls, t_vals, label=f'T @ {meas_thi:2.0f}mm')
        plt.plot(t_wvls, self.abs_coefs, label='absorption coef')

        plt.title(f"{self.catalog_name()}: {self.name()}")
        plt.xlabel('wavelength (nm)')

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()
