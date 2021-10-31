#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""

import numpy as np
from .util import Singleton

from . import glass


class HoyaCatalogExcel(glass.GlassCatalogXLSX, metaclass=Singleton):
    #    data_header = 1
    #    data_start = 4
    #    num_glasses = 194
    #    name_col_offset = 2
    #    coef_col_offset = 28
    #    index_col_offset = 10
    nline_str = {'t': 'nt',
                  's': 'ns',
                  'r': 'nr',
                  'C': 'nC',
                  "C'": "nC'",
                  'D': 'nD',
                  'd': 'nd',
                  'e': 'ne',
                  'F': 'nF',
                  "F'": "nF'",
                  'g': 'ng',
                  'h': 'nh',
                  'i': 'ni'}

    def __init__(self, fname='HOYA.xlsx'):
        super().__init__('Hoya', fname, 'Glass\u3000Type', 'A0', 'n1529.6',
                          num_coefs=12, data_header_offset=1,
                          transmission_offset=464, num_wvls=44,
                          transmission_header_offset=2)

    def glass_coefs(self, gindex):
        c = super().glass_coefs(gindex)
        coefs = [x*10**y for x, y in zip(c[::2], c[1::2])]
        return coefs

    def create_glass(self, gname, gcat):
        return HoyaGlass(gname)


class HoyaCatalog(glass.GlassCatalogPandas, metaclass=Singleton):

    def __init__(self, fname='HOYA.xlsx'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 4  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 3  # row with data item/header info
        data_col = 'D'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', (lambda h: h.split('n')[-1]), 
             2, 'K', 'AA'),
            ('dispersion coefficients', None, 2, 'AC', 'AN'),
            ('internal transmission mm, 10', None, 4, 'QV', 'SM'),
            ('chemical properties', None, 4, 'BW', 'CC'),
            ('thermal properties', None, 4, 'CD', 'DE'),
            ('mechanical properties', None, 4, 'DF', 'DL'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'F'),
            ('abbe number', 've', header_row, 'I'),
            ('refractive indices', (lambda h: float(h)), header_row, 'K'),
            ('refractive indices', (lambda h: float(h)), header_row, 'L'),
            ('specific gravity', 'd', header_row, 'ND'),
            ]
        kwargs = dict(
            data_extent = (5, 198, 'D', 'TA'),
            name_col_offset = 'C',
            )
        super().__init__('Hoya', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def glass_coefs(self, gname):
        c = super().glass_coefs(gname)
        coefs = [x*10**y for x, y in zip(c[::2], c[1::2])]
        return coefs

    def create_glass(self, gname, gcat):
        return HoyaGlass(gname)


class HoyaGlass(glass.Glass):
    catalog = HoyaCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return np.sqrt(n2)
