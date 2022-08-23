#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Support for the Hikari Glass catalog

.. Created on Tue Aug 25 22:55:44 2020

.. codeauthor: Michael J. Hayford
"""

import logging
from .util import Singleton

import numpy as np

from . import glass


class HikariCatalog(glass.GlassCatalogPandas, metaclass=Singleton):
    def get_rindx_wvl(header_str):
        """Returns the wavelength value from the refractive index data header string."""
        if isinstance(header_str, float):
            value = 1000*header_str
        else:
            value = header_str.split()[0]
        return value

    def get_transmission_wvl(header_str):
        """Returns the wavelength header string."""
        return float(header_str[:-len('nm')])

    def __init__(self, fname='HIKARI.xlsx'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 3  # number of header rows in the imported spreadsheet
        category_row = 2  # row with categories
        header_row = 3  # row with data item/header info
        data_col = 'B'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', HikariCatalog.get_rindx_wvl, 
             header_row, 'D', 'X'),
            ('dispersion coefficients', None, header_row, 'BD', 'BL'),
            ('internal transmission mm, 10', HikariCatalog.get_transmission_wvl,
             header_row, 'CY', 'ED'),
            ('chemical properties', None, header_row, 'CH', 'CL'),
            ('thermal properties', None, header_row, 'BW', 'CF'),
            ('mechanical properties', None, header_row, 'CM', 'CR'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'Y'),
            ('abbe number', 've', header_row, 'Z'),
            ('refractive indices', 't', header_row, 'I'),
            ('refractive indices', 's', header_row, 'J'),
            ('specific gravity', 'd', header_row, 'CG'),
            ]
        kwargs = dict(
            data_extent = (4, 163, data_col, 'GE'),
            name_col_offset = 'A',
            )
        super().__init__('Hikari', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def create_glass(self, gname: str, gcat: str) -> 'HikariGlass':
        """ Create an instance of the glass `gname`. """
        return HikariGlass(gname)


class HikariGlass(glass.GlassPandas):
    catalog = None

    def initialize_catalog(self):
        if HikariGlass.catalog is None:
            HikariGlass.catalog = HikariCatalog()
        
    def __init__(self, gname):
        self.initialize_catalog()
        super().__init__(gname)

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = coefs[0] + wv2*(coefs[1] + wv2*coefs[2])
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[3] +
                        wvm2*(coefs[4] +
                              wvm2*(coefs[5] +
                                    wvm2*(coefs[6] +
                                          wvm2*(coefs[7] +
                                                wvm2*coefs[8])))))
        return np.sqrt(n2)
