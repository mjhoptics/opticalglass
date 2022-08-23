#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2022 Michael J. Hayford
""" Module for simple optical media definitions

.. Created on Fri Sep 15 17:06:17 2017

.. codeauthor: Michael J. Hayford
"""

import numpy as np
from typing import Protocol, Dict, List, Tuple, Union
from numpy.typing import NDArray
from abc import abstractmethod

from scipy.interpolate import interp1d

from .spectral_lines import get_wavelength


def glass_encode(n, v):
    return f'{int(1000*round((n - 1), 3)):3d}.{int(round(10*v, 3)):3d}'


def glass_decode(gc):
    return round(1.0 + (int(gc)/1000), 3), round(100.0*(gc - int(gc)), 3)

# --- material definitions
class OpticalMedium(Protocol):
    """ Protocol for media with optical properties, e.g. refractive index. """

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def catalog_name(self) -> str:
        pass

    @abstractmethod
    def calc_rindex(self, wv_nm: Union[float, NDArray]) -> Union[float, NDArray]:
        """ returns the interpolated refractive index at wv_nm

        Args:
            wv_nm (float or numpy array): wavelength in nm for the refractive index query

        Returns:
            float or numpy array: the refractive index at wv_nm
        """
        pass

    @abstractmethod
    def meas_rindex(self, wvl: str) -> float:
        """ returns the measured refractive index at wvl

        Args:
            wvl: a string with a spectral line identifier

        Returns:
            float: the refractive index at wvl

        Raises:
            KeyError: if *wvl* is not in the spectra dictionary
        """
        pass

    def rindex(self, wvl: Union[float, str]) -> float:
        """ returns the interpolated refractive index at wvl

        Args:
            wvl: either the wavelength in nm or a string with a spectral line
                 identifier. for the refractive index query

        Returns:
            float: the refractive index at wv_nm

        Raises:
            KeyError: if ``wvl`` is not in the spectra dictionary
        """
        return self.calc_rindex(get_wavelength(wvl))

    @abstractmethod
    def transmission_data(self, thi: float) -> Tuple[NDArray, NDArray]:
        """ returns an array of transmission data for the glass

        Returns: np.arrays of wavelength and transmission for `thi` mm sample
        """
        pass


class Air(OpticalMedium):
    """ Optical definition for air (low fidelity definition) """

    def name(self) -> str:
        return 'air'

    def catalog_name(self) -> str:
        return ''

    def calc_rindex(self, wv_nm) -> float:
        return 1.0

    def meas_rindex(self, wv_nm) -> float:
        return 1.0

    def rindex(self, wv_nm) -> float:
        return 1.0


class InterpolatedMedium(OpticalMedium):
    """ Optical medium defined by a list of wavelength/index pairs

    Attributes:
        label: required string identifier for the material
        wvls: list of wavelengths in nm, used as x axis
        rndx: list of refractive indices corresponding to the values in wvls
        kvals_wvls: list of wavelengths in nm, used as x axis
        kvals: list of absorption coefficents corresponding to the values in 
               kvals_wvls
        rindex_interp: the refractive index interpolation function
        kvals_interp: the kval interpolation function
    """

    def __init__(self, label, pairs=None, wvls=None, 
                 rndx=None, kvals=None, kvals_wvls=None, cat=''):
        self.label = label
        self._catalog = cat
        if pairs is not None:
            self.wvls = []
            self.rndx = []
            for w, n in pairs:
                self.wvls.append(w)
                self.rndx.append(n)
        else:
            self.wvls = wvls
            self.rndx = rndx

        self.kvals = kvals
        if kvals is not None:
            self.kvals_wvls = self.wvls if kvals_wvls is None else kvals_wvls
        else:
            self.kvals_wvls = None

        self.update()

    def __repr__(self) -> str:
        return ('InterpolatedGlass(' + f"'{self.label}'" +
                ', cat=' + f"'{self._catalog}'" +
                ', wvls=' + repr(self.wvls) +
                ', rndx=' + repr(self.rndx) +
                ', kvals_wvls=' + repr(self.kvals_wvls) +
                ', kvals=' + repr(self.kvals) + ')')

    def __json_encode__(self) -> Dict:
        attrs = dict(vars(self))
        del attrs['rindex_interp']
        del attrs['kvals_interp']
        if hasattr(self, 'yaml_data'):
            del attrs['yaml_data']
        return attrs

    def sync_to_restore(self) -> None:
        """ rebuild interpolating function """
        self.update()

    def update(self) -> None:
        if len(self.wvls) == 1:
            self.rindex_interp = lambda wv: self.rndx[0]
        else:
            self.rindex_interp = interp1d(self.wvls, self.rndx, kind='cubic',
                                      assume_sorted=False)
        if self.kvals is not None:
            if len(self.kvals_wvls) == 1:
                self.kvals_interp = lambda wv: self.kvals[0]
            else:
                self.kvals_interp = interp1d(self.kvals_wvls, self.kvals, 
                                             kind='cubic', assume_sorted=False)
        else:
            self.kvals_interp = None

    def glass_code(self) -> str:
        nd = self.rindex('d')
        nF = self.rindex('F')
        nC = self.rindex('C')
        vd = (nd - 1)/(nF - nC)
        return str(glass_encode(nd, vd))

    def name(self) -> str:
        if self.label == '':
            return self.glass_code()
        else:
            return self.label

    def catalog_name(self) -> str:
        """ returns the glass catalog name """
        return self._catalog

    def calc_rindex(self, wv_nm: Union[float, NDArray]) -> Union[float, NDArray]:
        """ returns the interpolated refractive index at wv_nm """
        return self.rindex_interp(wv_nm)

    def meas_rindex(self, wvl: str) -> float:
        """ returns the measured refractive index at wvl

        For `InterpolatedGlass` the measured index isn't directly known. The
        calculated index is used instead. Calling `rindex` handles the spectral 
        line conversion.
        """
        return self.rindex(wvl)

    def transmission_data(self, thi=10.0):
        if self.kvals is None:
            raise Exception("NoTransmissionData", 
                            f"No transmission data for {self.name()}")
        t = thi*1.0e3
        t_vals = np.exp(-4.0*np.pi*t*self.kvals/self.kvals_wvls)
        return self.kvals_wvls, t_vals
