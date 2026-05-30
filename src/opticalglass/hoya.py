#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""

import numpy as np

from . import xls_glass


class HoyaCatalog(xls_glass.GlassCatalogPandas):

    def __init__(self, catalog_name:str='Hoya',
                 fname:str='HOYA20260401.xlsx', 
                 last_data_row:int=242):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 4  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 3  # row with data item/header info
        data_col = 'D'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        first_data_row = 5

        series_mappings = [
            ('refractive indices', (lambda h: h.split('n')[-1]), 
             2, 'M', 'AC'),
            ('dispersion coefficients', None, 2, 'AE', 'AP'),
            ('internal transmission mm, 2', None, 4, 'NN', 'PE'),
            ('internal transmission mm, 5', None, 4, 'PF', 'QW'),
            ('internal transmission mm, 10', None, 4, 'QX', 'SO'),
            ('chemical properties', None, 4, 'BY', 'CE'),
            ('thermal properties', None, 4, 'CF', 'DG'),
            ('mechanical properties', None, 4, 'DH', 'DN'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'F'),
            ('abbe number', 've', header_row, 'J'),
            ('refractive indices', (lambda h: float(h)), header_row, 'M'),
            ('refractive indices', (lambda h: float(h)), header_row, 'N'),
            ('refractive index', 'd', header_row, 'E'),
            ('refractive index', 'e', header_row, 'I'),
            ('specific gravity', 'd', header_row, 'NF'),
            ]
        kwargs = dict(
            data_extent = (first_data_row, last_data_row, data_col, 'TC'),
            name_col_offset = 'C',
            )
        pmd = xls_glass.PandasMappingDef(catalog_name, fname, series_mappings,
                                         item_mappings, args, kwargs)

        self.pmd = pmd
        super().__init__(pmd)
        HoyaGlass.catalog = self

    def glass_coefs(self, gname):
        c = super().glass_coefs(gname)
        coefs = [x*10**y for x, y in zip(c[::2], c[1::2])]
        return coefs

    def create_glass(self, gname: str) -> 'HoyaGlass':
        """ Create an instance of the glass `gname`. """
        return HoyaGlass(gname)


class HoyaGlass(xls_glass.GlassPandas):
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
