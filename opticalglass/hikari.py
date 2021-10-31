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


class HikariCatalogExcel(glass.GlassCatalogXLSX, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'t': "ｔ\n1.01398",
                 's': "ｓ\n0.85211",
                 'r': 'r\n0.706519',
                 'C': 'C\n0.656273',
                 "C'": "C'\n0.643847",
                 'D': 'D\n0.589294',
                 'd': 'd\n0.587562',
                 'e': 'e\n0.546074',
                 'F': 'F\n0.486133',
                 "F'": "F'\n0.479992",
                 'g': 'g\n0.435835',
                 'h': 'h\n0.404656',
                 'i': 'i\n0.365015'}

    def __init__(self, fname='HIKARI.xlsx'):
        super().__init__('Hikari', fname, '硝種  Glass type', 'A0', 2.05809,
                         data_header_offset=1, glass_name_offset=2,
                         num_coefs=9,
                         transmission_offset=103, num_wvls=32)

    def create_glass(self, gname, gcat):
        return HikariGlass(gname)

    def get_transmission_wvl(self, header_str):
        """Returns the wavelength value from the transmission data header string."""
        return float(header_str[:-len('nm')])




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

    def create_glass(self, gname, gcat):
        return HikariGlass(gname)


class HikariGlass(glass.Glass):
    catalog = HikariCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
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
