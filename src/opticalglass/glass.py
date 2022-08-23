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
import importlib
import itertools
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from typing import Union
from numpy.typing import NDArray
from abc import abstractmethod

from . import buchdahl
from . import util
from . import glasserror as ge
from .opticalmedium import OpticalMedium
from .util import Singleton, Counter
from .spectral_lines import get_wavelength

from .caselessDictionary import CaselessDictionary


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


def get_glass_map_arrays(cat, d_str, F_str, C_str, **kwargs):
    """ return index and dispersion data arrays for input spectral range

    Args:
        cat: glass catalog instance, source for returned data
        d_str (str): central wavelength string
        F_str (str): blue end wavelength string
        C_str (str): red end wavelength string
        partials (tuple): kwarg if present, 2 wvls, wl4 and wl5, wl4 < wl5

    Returns:
        index, V-number, partial dispersion, Buchdahl coefficients, and
        glass names
    """
    names = cat.get_glass_names()

    nd = cat.df['refractive indices'][d_str].to_numpy(dtype=float)
    nF = cat.df['refractive indices'][F_str].to_numpy(dtype=float)
    nC = cat.df['refractive indices'][C_str].to_numpy(dtype=float)

    nd, coefs = buchdahl.calc_buchdahl_coords(
        nd, nF, nC, wlns=(d_str, F_str, C_str), **kwargs)

    if 'partials' in kwargs:
        wl_a, wl_b = kwargs['partials']
        na = cat.df['refractive indices'][wl_a].to_numpy(dtype=float)
        nb = cat.df['refractive indices'][wl_b].to_numpy(dtype=float)
        nd, vd, PFd, Pab = util.calc_glass_constants(nd, nF, nC, na, nb)
    else:
        vd, Pab = util.calc_glass_constants(nd, nF, nC)

    return nd, vd, Pab, coefs[0], coefs[1], names


def glass_catalog_factory(cat_name, mod_name=None, cls_name=None):
    """ Function returning a glass catalog instance.

    Arguments:
        catalog: name of supported catalog (CDGM, Hoya, Ohara, Schott)
        mod_name: the module name of the glass catalog
        cls_name: the class name of the glass catalog

    Raises:
        GlassCatalogNotFoundError: if catalog isn't found
    """
    catalog = None
    if mod_name is None:
        mod_name = 'opticalglass.' + cat_name.lower()
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError:
        logging.info(f'glass catalog module {mod_name} not found')
        raise ge.GlassCatalogNotFoundError(cat_name)
    else:
        if cls_name is None:
            cls_name = cat_name + 'Catalog'
        try:
            cat_class = getattr(mod, cls_name)
        except AttributeError:
            logging.info(f'glass catalog class {cls_name} not found')
            # try forcing cat_name to be capitalized
            cat_name_cap = cat_name.capitalize()
            cls_name = cat_name_cap + 'Catalog'
            try:
                cat_class = getattr(mod, cls_name)
            except AttributeError:
                logging.info(f'glass catalog class {cls_name} not found')
                raise ge.GlassCatalogNotFoundError(cat_name)
            else:
                catalog = cat_class()
        else:
            catalog = cat_class()
    return catalog


def xl_cols():
    """ Generate Excel column labels, A thru ZZ. """
    caps_word = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    cols = list(caps_word)
    
    for c1 in caps_word:
        for c2 in caps_word:
            cols.append(c1 + c2)
    return cols


def xl2df(fname):
    """ Read Excel fname into a dataframe and apply Excel based column names. """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        xl_df = pd.read_excel(get_filepath(fname), header=None)
    shape = xl_df.shape
    xl_df.index = pd.RangeIndex(start=1, stop=shape[0]+1, step=1)
    xl_df.columns = xl_cols()[:shape[1]]
    return xl_df


def build_glass_cat(xl_df, series_mappings, item_mappings, 
                    *args, **kwargs):
    """ Apply series and item mappings to xl_df, and return catalog df. """
    num_rows, category_row , header_row, data_col = args
    r0, rk, c0, ck = kwargs['data_extent']

    # generate data headers again; should be all unique
    headers = xl_df.loc[1:num_rows].copy().astype('object')

    for m in series_mappings:
        category, action, row, col1, colk = m
        for idx in headers.loc[row].loc[col1:colk].index:
            if action is not None:
                headers.at[header_row, idx] = action(headers.loc[row, idx])
            else:
                headers.at[header_row, idx] = headers.loc[row, idx]
            headers.at[category_row, idx] = category

    for m in item_mappings:
        category, hdr, row, col = m
        item = headers.loc[row, col]
        if callable(hdr):
            h_item = hdr(item)
        elif hdr is not None:
            h_item = hdr
        else:
            h_item = item
        headers.at[header_row, col] = h_item
        headers.at[category_row, col] = category

    mindx = pd.MultiIndex.from_arrays([headers.loc[category_row, data_col:ck],
                                       headers.loc[header_row, data_col:ck]],
                                      names=['category', 'data item'])

    # make a new df from the data area of the worksheet
    glass_cat = xl_df.loc[r0:rk, c0:ck]
    glass_cat.index = xl_df.loc[r0:rk, kwargs['name_col_offset']]
    glass_cat.index.name = 'glass'
    glass_cat.columns = mindx

    # weed out any duplicate or empty columns
    if glass_cat.columns.has_duplicates:
        dups = glass_cat.columns.duplicated()
        dups1 = [glass_cat.columns[i] for i, b in enumerate(dups) if b == True]
        glass_cat.drop(columns=dups1, inplace=True)

    # infer dtypes so that downstream numpy routines don't 
    #  complain about object data
    glass_cat = glass_cat.convert_dtypes()

    return glass_cat


class GlassCatalogPandas():
    """ Pandas-based glass catalog
    
    Optical glass manufacturers have settled on Excel spreadsheets as a means 
    of documenting the technical details of their glass products. The formats
    are broadly similar but different in the details. This class and related
    functions provide a means of mapping the Excel data into a pandas dataframe
    that has some categories relabeled to take advantage of commonalities.
    
    The class is adapted to a specific catalog by defining the position and
    size of the data areas in the original Excel spreadsheet. Pandas is used to 
    read the spreadsheet into a dataframe, xl_df. xl_df has 
    indices and columns that match the Excel worksheet border.
    
    - the index runs from 1 to xl_df.shape[0]
    - the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
    
    This facilitates transferring areas on the spreadsheet to areas in the 
    catalog DataFrame.
    
    Manufacturers spreadsheets have a header area and a data area. First, a
    set of parameters are defined for the header. Data that are spread over 
    multiple columns form a category, often readily identified in the 
    spreadsheet layout. 
    ::

        num_rows = 2  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 2  # row with data item/header info
        data_col = 'B'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col

    
    The location of the different categories in the spreadsheet is defined in
    the series_mapping list.
    ::
        
        series_mappings = [
            ('refractive indices', (lambda h: h.split('n')[-1]), 
             category_row, 'C', 'P'),
            ('dispersion coefficients', None, category_row, 'V', 'AA'),
            ('internal transmission mm, 10', None, header_row, 'DC', 'EK'),
            ('chemical properties', None, category_row, 'AW', 'BA'),
            ('thermal properties', None, category_row, 'BB', 'BI'),
            ('mechanical properties', None, category_row, 'BJ', 'BO'),
            ]

    There are common items of interest, that correspond to a single column.
    These are defined in the item_mappings list.
    ::

        item_mappings = [
            ('refractive indices', 'C', header_row, 'F'),
            ('refractive indices', "C'", header_row, 'G'),
            ('abbe number', 'vd', header_row, 'R'),
            ('abbe number', 've', header_row, 'S'),
            ('specific gravity', 'd', header_row, 'BP'),
            ]
        kwargs = dict(
            data_extent = (3, 242, data_col, 'FZ'),
            name_col_offset = 'A',
            )

    Attributes:
        name: the glass catalog name
        df: the |DataFrame| containing the catalog data
        glass_list: 
        glass_lookup:
    """

    def __init__(self, name, fname, series_mappings, item_mappings, 
                 *args, **kwargs):
        """

        Args:
            name: name of the glass catalog
            fname: excel filename, located in ``data`` directory
            series_mappings: the header string for the Glass column in fname
            item_mappings: the header string for the first refractive index coefficient
                      column in fname
            args: the header string for the first refractive index value
                        column in fname
        """
        self.name = name
        # Open the workbook
        xl_df = xl2df(fname)
        self.df = build_glass_cat(xl_df, series_mappings, item_mappings, 
                                  *args, **kwargs)

        # build an alphabetical list of decoded glass names
        gnames = self.df.index.array
        glass_list = [(decode_glass_name(gn), gn, name)
                      for gn in gnames]
        glass_list = sorted(glass_list, key=lambda glass: glass[0][0])
        # build a lookup dict of the glass defs keyed to decoded glass names
        glass_lookup = {gn_decode: (gn, gc)
                        for gn_decode, gn, gc in glass_list}
        # attach these 'static' lists to class variables
        self.__class__.glass_list = glass_list
        self.__class__.glass_lookup = glass_lookup

    @abstractmethod
    def create_glass(self, gname: str, gcat: str) -> OpticalMedium:
        """ Create an instance of the glass `gname`. 
        
        Must be implemented by the subclasses.
        """
        pass

    def catalog_name(self):
        return self.name

    def get_glass_names(self):
        """ returns a list of glass names """
        return self.df.index.array

    def get_column_names(self):
        """ returns a list of column headers """
        return self.df.columns.levels[0]

    def glass_index(self, gname):
        """ returns the glass index (row) for glass name `gname`

        Args:
            gname (str): glass name

        Returns:
            int: the 0-based index (row) of the requested glass
        """
        return self.df.index.get_loc(gname)

    def data_index(self, dname):
        """ returns the data index (column) for data `dname`

        Args:
            dname (str): header string for data

        Returns:
            int: the 1-based index (column) of the requested data

        Raises:
            GlassDataNotFoundError: if *dname* doesn't match any header string
        """
        dname_iloc = self.df.columns.get_loc(dname)
        if isinstance(dname_iloc, int):
            return dname_iloc
        for i, b in enumerate(dname_iloc, start=1):
            if b:
                break
        return i

    def get_data_for_glass(self, gname, dindex=None, num=None):
        """ returns an array of glass data for the glass at *gname*

        Args:
            gname: glass index into spreadsheet
            dindex: the starting column of the desired data
            num: number of data items (cells) to retrieve

        Returns: list of data items
        """
        if isinstance(gname, int):
            gname = self.df.index[gname]
        glass_data = self.df.loc[gname]
        if dindex is not None:  # get a partial row of at least 1 item
            num = num if num is not None else 1
            if isinstance(dindex, str):
                dindex = glass_data.index.get_loc(dindex)
            glass_data = glass_data.iloc[dindex:dindex+num]

        return glass_data

    def glass_data(self, gindex):
        """ returns an array of data for the glass at *gindex* """
        glass_data = self.get_data_for_glass(gindex)
        return glass_data

    def glass_coefs(self, gname):
        """ returns an array of glass coefficients for the glass at *gname* """
        glas = self.df.loc[gname]
        coefs = glas['dispersion coefficients'].to_numpy(dtype=float)
        return coefs

    def catalog_data(self, dindex):
        """ returns an array of data at column *dindex* for all glasses """
        dname = self.ws.columns[dindex]
        return self.ws[dname]

    def transmission_data(self, gname):
        """ returns an array of transmission data for the glass at *gindex*

        Args:
            gname: glass name

        Returns:
            list of wavelength, transmittance pairs
        """
        gla = self.df.loc[gname]
        return gla['internal transmission mm, 10'].array

    def glass_map_data(self, wvl='d', **kwargs):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        return get_glass_map_arrays(self, wvl, 'F', 'C', **kwargs)


class GlassPandas(OpticalMedium):
    """ base optical glass, for use with pandas

    Attributes:
        gname: the glass name
        catalog: the GlassCatalog this glass is associated with.
                 **Must be provided by the derived class**
        coefs: list of coefficients for calculating refractive index vs wv
    """

    def __init__(self, gname):
        self.gname = gname
        self.coefs = self.catalog.glass_coefs(gname)

    def __str__(self):
        return self.catalog.name + ' ' + self.name() + ': ' + self.glass_code()

    def __repr__(self):
        return "{!s}('{}')".format(type(self).__name__, self.gname)

    def sync_to_restore(self):
        """ hook routine to restore coefs, if needed """
        self.initialize_catalog()
        if not hasattr(self, 'coefs'):
            self.coefs = self.catalog.glass_coefs(self.gname)
        if hasattr(self, 'gindex'):
            delattr(self, 'gindex')

    def initialize_catalog(self):
        """ subclass initialization of glass catalog instance, as needed. """
        pass

    def glass_code(self, d_str='d', vd_str='vd'):
        """ returns the 6 digit glass code, combining index and V-number """
        glas = self.glass_data()
        nd = glas['refractive indices'][d_str]
        vd = glas['abbe number'][vd_str]
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def glass_data(self):
        """ returns the raw spreadsheet data for the glass as a Series """
        return self.catalog.df.loc[self.gname]

    def name(self):
        """ returns the glass name, :attr:`gname` """
        return self.gname

    def catalog_name(self):
        """ returns the glass name, :attr:`gname` """
        return self.catalog.catalog_name()

    def meas_rindex(self, wvl):
        """ returns the measured refractive index at wvl

        Args:
            wvl: a string with a spectral line identifier

        Returns:
            float: the refractive index at wvl

        Raises:
            KeyError: if *wvl* is not in the spectra dictionary
        """
        rindx = self.glass_data()['refractive indices'][wvl]
        return rindx

    def rindex(self, wvl) -> float:
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

    def calc_rindex(self, wv_nm: Union[float, NDArray]) -> Union[float, NDArray]:
        """ returns the interpolated refractive index at wv_nm

        **Must be provided by the derived class**

        Args:
            wv_nm (float or numpy array): wavelength in nm for the refractive index query

        Returns:
            float or numpy array: the refractive index at wv_nm
        """
        pass

    def transmission_data(self):
        """ returns an array of transmission data for the glass

        Returns: np.arrays of wavelength and transmission for 10mm sample
        """
        glas = self.glass_data()
        t10 = glas['internal transmission mm, 10']
        # coerce non-numeric values to NaN, then convert NaN to 0.
        t10_flt = pd.to_numeric(t10, errors='coerce').fillna(0)
        t10_np = t10_flt.to_numpy(dtype=float)

        t10_wvls = t10.index.to_numpy(dtype=float)
        return t10_wvls, t10_np


def decode_glass_name(glass_name):
    """Split glass_name into prefix, group, num, suffix.

    Manufacturers glass names follow a common pattern. At the simplest, it is
    a short character string, typically used to identify a particular glass
    composition, with a numeric qualifier. The composition group and product
    serial number are combined to form the basic product id, the group_num:

        - F2
        - SF56

    Manufacturers will often use a single character prefix to indicate
    different categories of glasses, e.g. moldable or "New":

        - N-BK7
        - P-LASF50

    Similarly, a suffix with one or more characters is often used to
    differentiate between different variations of the same base material.

        - N-SF57
        - N-SF57HT
        - N-SF57HTultra

    This function takes an input glass name and returns a tuple of strings. A
    valid glass_name should always have a non-null group_num; prefixes and
    suffixes are optional and used differently by different manufacturers.

        * group_num, prefix, suffix
        * group, num = group_num

    Args:
        glass_name (str): a glass manufacturer's glass name

    Returns: group_num, prefix, suffix, where group_num = group, num

    Returned strings are uppercase.

    """
    gn = glass_name.upper().split('-')
    suffix = ''
    if len(gn) == 1:
        prefix = ''
        gn2 = gn[0]
    elif len(gn) == 3:
        prefix = gn[0]
        suffix = gn[2]
        gn2 = gn[1]
    elif len(gn) == 2:
        if len(gn[0]) < 3:
            prefix = gn[0]
            gn2 = gn[1]
        else:
            prefix = ''
            gn2 = gn[0]
            suffix = gn[1]

    group = gn2
    num = ''
    for i, char in enumerate(gn2):
        if char.isdigit():
            start = i
            while i < len(gn2) and gn2[i].isdigit():
                i += 1
            group = gn2[:start].rstrip()
            num = gn2[start:i]
            break
    suffix = gn2[i:] if suffix == '' else suffix
    group_num = group, num
    return group_num, prefix, suffix


def glass_catalog_stats(glass_list, do_print=False):
    """Decode all of the glass names in glass_cat_name.

    Print out the original glass names and the decoded version side by side.

    Args:
        glass_list: ((group, num), prefix, suffix), glass_name, glass_cat_name
        do_print (bool): if True, print the glass name and the decoded version

    Returns:
        groups (dict): all catalog groups
        group_num (dict): all glasses with multiple variants
        prefixes (dict): all the non-null prefixes used
        suffixes (dict): all the non-null suffixes used
    """
    groups = Counter()
    group_nums = Counter()
    prefixes = Counter()
    suffixes = Counter()
    for g in glass_list:
        (group_num, prefix, suffix), gn, gc = g
        group, num = group_num
        if prefix != '':
            prefixes[prefix] += 1
        if suffix != '':
            suffixes[suffix] += 1
        groups[group] += 1
        group_nums[group_num] += 1
        if do_print:
            fmt_3 = "{:14s} {:>2s}  {:8s}  {:12s}"
            print(fmt_3.format(gn, prefix, group+num, suffix))
    # filter group_nums to include only multi-use items
    group_nums = {k: v for k, v in group_nums.items() if v > 1}
    return groups, group_nums, prefixes, suffixes


class Robb1983Catalog(metaclass=Singleton):
    """ glass catalog based on data in Robb, et als 1983 paper on Buchdahl's
    chromatic coordinate

    The data used by this class is from the 1983 paper by Paul N. Robb and
    R. I. Mercado, `Calculation of refractive indices using Buchdahl’s
    chromatic coordinate <https://doi.org/10.1364/AO.22.001198>`_ . The
    copyright date for all 5 catalogs cited was 1980.

    Args:
        fname: filename, located in ``data`` directory

    Attributes:
        glass_db: dict lookup by catalog and glass name, value is decoded
                  glassname and Buchdahl coefficients
        glass_list: list of decoded_glassname, glassname, and catalog per glass

    """

    _cat_names = ["SCHOTT", "OHARA", "HOYA", "CORNING-FRANCE", "CHANCE"]

    def __init__(self, fname='robb1983_data_final.txt'):
        # Open the workbook
        glass_db = CaselessDictionary()
        glass_list = []
        rndx_list = []
        nu1_list = []
        nu2_list = []
        with get_filepath(fname).open() as f_input:
            for line in f_input:
                if line[0] == '#':
                    if 'GLASS CATALOGUE' in line:
                        tokens = line[1:].split()
                        catalog = 'Robb1983.' + tokens[0]
                        glass_db[catalog] = {}
                else:
                    tokens = line.split()
                    gname = tokens[0]
                    try:
                        gname_decode = decode_glass_name(gname)
                    except UnboundLocalError:
                        print(catalog, gname)
                    else:
                        rndx = float(tokens[1])
                        nu1 = float(tokens[2])
                        nu2 = float(tokens[3])
                        glass_db[catalog][gname] = (
                            gname_decode, rndx, nu1, nu2)
                        glass_list.append((gname_decode, gname, catalog))
                        rndx_list.append(rndx)
                        nu1_list.append(nu1)
                        nu2_list.append(nu2)

        glass_lookup = {gn_decode: (gn, gc)
                        for gn_decode, gn, gc in glass_list}
        self.glass_db = glass_db
        self.glass_list = glass_list
        self.glass_lookup = glass_lookup
        self._glass_data = CaselessDictionary()

    @property
    def glass_data(self):
        if len(self._glass_data) == 0:
            for rbk, rbv in self.glass_db.items():
                gnames = list(rbv.keys())
                gdata = np.array([[d[1], d[2], d[3]] for d in rbv.values()])
                self._glass_data[rbk] = gnames, gdata
        return self._glass_data

    def create_glass(self, gname: str, gcat: str) -> OpticalMedium:
        catalog = gcat if 'Robb1983.' in gcat else 'Robb1983.' + gcat
        try:
            gdata = self.glass_db[catalog][gname]
        except KeyError:
            return None
        else:
            wv0 = buchdahl.get_wv('d')
            gname_decode, rndx, nu1, nu2 = gdata
            g = buchdahl.Buchdahl(wv0, rndx, (nu1, nu2), mat=gname, cat=gcat)
            return g

    def catalog_name(self):
        return 'Robb1983'

    def get_glass_names(self, gcat=None):
        """ returns a list of glass names """
        if gcat is not None:
            return self.glass_data[gcat][0]
        else:  # return all of the catalogs' names
            gnames = [gn[0] for gn in self.glass_data.values()]
            return list(itertools.chain.from_iterable(gnames))

    def glass_map_data(self, wvl='d', **kwargs):
        """ return index and dispersion data for all glasses in the catalog

        Args:
            wvl (str): the central wavelength for the data, either 'd' or 'e'

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        return self.get_glass_map_arrays(wvl, 'F', 'C', **kwargs)

    def get_glass_map_arrays(self, d_str, F_str, C_str, **kwargs):
        """ return index and dispersion data arrays for input spectral range

        Args:
            nd_str (str): central wavelength string
            nf_str (str): blue end wavelength string
            nc_str (str): red end wavelength string

        Returns:
            index, V-number, partial dispersion, Buchdahl coefficients, and
            glass names
        """
        wv_0 = buchdahl.get_wv('d')
        wv_d = buchdahl.get_wv(d_str)
        wv_F = buchdahl.get_wv(F_str)
        wv_C = buchdahl.get_wv(C_str)

        om_d = buchdahl.omega(wv_d - wv_0)
        om_F = buchdahl.omega(wv_F - wv_0)
        om_C = buchdahl.omega(wv_C - wv_0)

        gnames, gdata = self.glass_data[kwargs['cat_name']]

        omm_d = np.array([om_d, om_d**2])
        nd = np.matmul(gdata[:, 1:], omm_d) + gdata[:, 0]

        omm_F = np.array([om_F, om_F**2])
        nF = np.matmul(gdata[:, 1:], omm_F) + gdata[:, 0]

        omm_C = np.array([om_C, om_C**2])
        nC = np.matmul(gdata[:, 1:], omm_C) + gdata[:, 0]

        vd, PCd = util.calc_glass_constants(nd, nF, nC)

        coefs = np.array(gdata[:, 1:3])
        ctype = kwargs.get('ctype', None)
        if ctype == "disp_coefs":
            coefs[:, 0] /= (nd - 1)
            coefs[:, 1] /= (nd - 1)

        return nd, vd, PCd, coefs[:, 0], coefs[:, 1], gnames
