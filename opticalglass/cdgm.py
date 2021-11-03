#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the CDGM Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np

from . import glass


class CDGMCatalogExcel(glass.GlassCatalogXLS, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'t': 'nt',
                 's': 'ns',
                 'r': 'nr',
                 'C': 'nc',
                 "C'": "nc'",
                 'D': 'nD',
                 'd': 'nd',
                 'e': 'ne',
                 'F': 'nF',
                 "F'": "nF'",
                 'g': 'ng',
                 'h': 'nh',
                 'i': 'ni'}

    def __init__(self, fname='CDGM.xls'):
        super().__init__('CDGM', fname, 'Glass', 'A0', 'nt',
                         transmission_offset=106, num_wvls=34,
                         transmission_header_offset=1)

    def get_glass_names(self):
        """ returns a list of glass names """
        gnames = super().get_glass_names()
        # filter out any empty cells at the end
        while gnames and (len(gnames[-1]) == 0 or gnames[-1] == 'Over!'):
            gnames.pop()
        return gnames

    def create_glass(self, gname, gcat):
        return CDGMGlass(gname)


class CDGMCatalog(glass.GlassCatalogPandas, metaclass=Singleton):

    def __init__(self, fname='CDGM.xls'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 2  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 2  # row with data item/header info
        data_col = 'B'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', (lambda h: h.split('n')[-1]), 
             category_row, 'C', 'P'),
            ('dispersion coefficients', None, category_row, 'V', 'AA'),
            ('internal transmission mm, 10', None, header_row, 'DC', 'EK'),
            ('chemical properties', None, category_row, 'AW', 'BA'),
            ('thermal properties', None, category_row, 'BB', 'BI'),
            ('mechanical properties', None, category_row, 'BJ', 'BO'),
            ]
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
        super().__init__('CDGM', fname, series_mappings, item_mappings, 
                         *args, **kwargs)


    def create_glass(self, gname, gcat):
        return CDGMGlass(gname)


class CDGMGlass(glass.GlassPandas):
    catalog = None

    def __init__(self, gname):
        if CDGMGlass.catalog is None:
            CDGMGlass.catalog = CDGMCatalog()
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
