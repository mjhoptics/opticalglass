#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Michael J. Hayford
""" Support for Glass catalogs and instances

The ``glass`` module contains the two base classes fundamental to the
:mod:`opticalglass` module. The :class:`~opticalglass.glass.GlassCatalog` class
implements as much of the common functionality needed for access to the
catalog data as possible.

The :class:`~opticalglass.glass.Glass` is an interface to the data for a particular
glass in a catalog. The primary function of interest for optical calculations
is :func:`~opticalglass.glass.Glass.rindex` which returns the refractive index at the
input wavelength (nm).

A factory interface to ``Glass`` creation is the function
:func:`~opticalglass.glassfactory.create_glass` that returns a ``Glass``
instance of the appropriate catalog type, given the glass and catalog names.

.. codeauthor: Michael J. Hayford
"""
import logging
from pathlib import Path

import xlrd
import numpy as np

from . import glasserror as ge


spectra = {'Nd': 1060.0,
           't': 1013.98,
           's': 852.11,
           'r': 706.5188,
           'C': 656.2725,
           "C'": 643.8469,
           'HeNe': 632.8,
           'D': 589.2938,
           'd': 587.5618,
           'e': 546.074,
           'F': 486.1327,
           "F'": 479.9914,
           'g': 435.8343,
           'h': 404.6561,
           'i': 365.014}
""" dict:
       - keys: spectral line labels
       - values: wavelengths in nm
"""


def get_filepath(fname):
    """ given a (spreadsheet) file name, return a complete Path to the file

    The data files included with the ``opticalglass`` package are located in
    a data directory in the package hierarchy.
    ::

        opticalglass/
            opticalglass/
                data/
                    fname

    Args:
        fname (str): the spreadsheet filename, including extender

    Returns:
        str: full path including filename for requested spreadsheet
    """
    pth = Path(__file__).resolve().parent
    return pth/'data'/fname


class GlassCatalog:
    """ base glass catalog

    Args:
        name: name of the glass catalog
        fname: excel filename, located in ``data`` directory
        glass_str: the header string for the Glass column in fname
        coef_str: the header string for the first refractive index coefficient
                  column in fname
        rindex_str: the header string for the first refractive index value
                    column in fname

    Attributes:
        num_glasses: number of glasses in the catalog
        data_header: the row containing the data header labels
        data_start: first row in the spreadsheet contain glass data
        name_col_offset: the column offset for glass_str
        coef_col_offset: the column offset for coef_str
        index_col_offset: the column offset for rindex_str
        data_header_offset: the row offset of the data headers from the
                            glass_str row
        nline_str: a dict of strings mapping header strings used for index for
                   spectral lines. **Must be provided by the derived class**
    """

    def __init__(self, name, fname, glass_str, coef_str, rindex_str,
                 data_header_offset=0):
        self.name = name
        # Open the workbook
        xl_workbook = xlrd.open_workbook(get_filepath(fname))
        self.xl_data = xl_workbook.sheet_by_index(0)

        for i in range(0, self.xl_data.nrows):
            try:
                self.name_col_offset = (self.xl_data.row_values(i, 0)
                                        .index(glass_str))
                glass_header = i
                self.data_header = i
                # the data headers may be offset from the Glass header row
                self.data_header += data_header_offset
                break
            except ValueError:
                pass

        for j in range(glass_header+1, self.xl_data.nrows):
            gname = self.xl_data.cell_value(j, self.name_col_offset)
            if len(gname) > 0:
                self.data_start = j
                break

        gnames = self.get_glass_names()
        self.num_glasses = len(gnames)

        colnames = self.xl_data.row_values(self.data_header, 0)
        self.coef_col_offset = colnames.index(coef_str)
        self.index_col_offset = colnames.index(rindex_str)

    def get_glass_names(self):
        """ returns a list of glass names """
        gnames = self.xl_data.col_values(self.name_col_offset, self.data_start)
        # filter out any empty cells at the end
        while gnames and len(gnames[-1]) is 0:
            gnames.pop()
        return gnames

    def glass_index(self, gname):
        """ returns the glass index (row) for glass name `gname`

        Args:
            gname (str): glass name

        Returns:
            int: the index (row) of the requested glass

        Raises:
            GlassNotFoundError: if **gname** doesn't match any header string
        """
        gnames = self.xl_data.col_values(self.name_col_offset, self.data_start)
        if gname in gnames:
            gindex = gnames.index(gname)
        else:
            logging.info('%s glass %s not found', self.name, gname)
            raise ge.GlassNotFoundError(self.name, gname)

        return gindex

    def data_index(self, dname):
        """ returns the data index (column) for data `dname`

        Args:
            dname (str): header string for data

        Returns:
            int: the index (column) of the requested data

        Raises:
            GlassDataNotFoundError: if **dname** doesn't match any header string
        """
        if dname in self.xl_data.row_values(self.data_header, 0):
            dindex = self.xl_data.row_values(self.data_header, 0).index(dname)
        else:
            logging.info('%s glass data type %s not found', self.name, dname)
            raise ge.GlassDataNotFoundError(self.name, dname)

        return dindex

    def glass_data(self, gindex):
        """ returns an array of data for the glass at **gindex** """
        return self.xl_data.row_values(self.data_start+gindex, 0)

    def catalog_data(self, dindex):
        """ returns an array of data at column **dindex** for all glasses """
        return self.xl_data.col_values(dindex, self.data_start,
                                       self.data_start+self.num_glasses)

    def glass_coefs(self, gindex):
        """ returns an array of glass coefficients for the glass at **gindex** """
        return (self.xl_data.row_values(self.data_start+gindex,
                                        self.coef_col_offset,
                                        self.coef_col_offset+6))

    def glass_map_data(self, wvl='d'):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, and glass names
        """
        if wvl == 'd':
            return self.get_glass_map_arrays('nd', 'nF', 'nC')
        elif wvl == 'e':
            return self.get_glass_map_arrays('ne', 'nF', 'nC')
        else:
            return None

    def get_glass_map_arrays(self, nd_str, nf_str, nc_str):
        """ return index and dispersion data arrays for input spectral range

        Args:
            nd_str (str): central wavelength string
            nf_str (str): blue end wavelength string
            nc_str (str): red end wavelength string

        Returns:
            index, V-number, partial dispersion, and glass names
        """
        nd = np.array(
                self.catalog_data(self.data_index(self.nline_str[nd_str])))
        nF = np.array(
                self.catalog_data(self.data_index(self.nline_str[nf_str])))
        nC = np.array(
                self.catalog_data(self.data_index(self.nline_str[nc_str])))
        dFC = nF-nC
        vd = (nd - 1.0)/dFC
        PCd = (nd-nC)/dFC
        names = self.catalog_data(self.name_col_offset)
        return nd, vd, PCd, names


class Glass:
    """ base optical glass

    Attributes:
        gname: the glass name
        gindex: the index into the glass list
        catalog: the GlassCatalog this glass is associated with.
                 **Must be provided by the derived class**
    """
    def __init__(self, gname):
        self.gindex = self.catalog.glass_index(gname)
        self.gname = gname

    def __str__(self):
        return self.catalog.name + ' ' + self.name() + ': ' + self.glass_code()

    def __repr__(self):
        return "{!s}('{}')".format(type(self).__name__, self.gname)

    def sync_to_restore(self):
        """ hook routine to restore the gindex given gname """
        self.gindex = self.catalog.glass_index(self.gname)

    def glass_code(self, nd_str, vd_str):
        """ returns the 6 digit glass code, combining index and V-number """
        nd = self.glass_item(nd_str)
        vd = self.glass_item(vd_str)
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def glass_data(self):
        """ returns the raw spreadsheet data for the glass """
        return self.catalog.glass_data(self.gindex)

    def name(self):
        """ returns the glass name, :attr:`gname` """
        return self.gname

    def glass_item(self, dname):
        """ return the value of the **dname** item

        Args:
            dname (str): header string for data

        Returns:
            the **dname** data

        Raises:
            GlassDataNotFoundError: if **dname** doesn't match any header string
        """
        dindex = self.catalog.data_index(dname)
        if dindex is None:
            return None
        else:
            return self.glass_data()[dindex]

    def rindex(self, wvl):
        """ returns the interpolated refractive index at wvl

        Args:
            wvl: either the wavelength in nm or a string with a spectral line
                 identifier. for the refractive index query

        Returns:
            float: the refractive index at wv_nm

        Raises:
            KeyError: if ``wvl`` is not in the spectra dictionary
        """
        if isinstance(wvl, float):
            return self.calc_rindex(wvl)
        elif isinstance(wvl, int):
            return self.calc_rindex(wvl)
        else:
            return self.calc_rindex(spectra[wvl])

    def calc_rindex(self, wv_nm):
        """ returns the interpolated refractive index at wv_nm

        **Must be provided by the derived class**

        Args:
            wv_nm (float): wavelength in nm for the refractive index query

        Returns:
            float: the refractive index at wv_nm
        """
        pass
