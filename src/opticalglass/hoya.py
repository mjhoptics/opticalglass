#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""

import numpy as np
from .util import Singleton

from . import glass


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
            ('refractive index', 'd', header_row, 'E'),
            ('refractive index', 'e', header_row, 'H'),
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

    def create_glass(self, gname: str, gcat: str) -> 'HoyaGlass':
        """ Create an instance of the glass `gname`. """
        return HoyaGlass(gname)


class HoyaGlass(glass.GlassPandas):
    catalog = None

    def initialize_catalog(self):
        if HoyaGlass.catalog is None:
            HoyaGlass.catalog = HoyaCatalog()
        
    def __init__(self, gname):
        self.initialize_catalog()
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
