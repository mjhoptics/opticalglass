#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Ohara Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np

from . import glass


class OharaCatalog(glass.GlassCatalogPandas, metaclass=Singleton):
    def get_rindx_wvl(header_str):
        """Returns the wavelength value from the refractive index data header string."""
        hdr = header_str.split('n')[-1]
        try:
            h = float(hdr)
        except ValueError:
            h = hdr
        return h

    def __init__(self, fname='OHARA.xlsx'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 2  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 2  # row with data item/header info
        data_col = 'C'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', OharaCatalog.get_rindx_wvl, 
             header_row, 'E', 'X'),
            ('dispersion coefficients', None, header_row, 'BI', 'BN'),
            ('internal transmission mm, 10', None, header_row, 'CC', 'DH'),
            ('chemical properties', None, header_row, 'FT', 'FY'),
            ('thermal properties', None, header_row, 'FE', 'FI'),
            ('mechanical properties', None, header_row, 'FM', 'FS'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'Y'),
            ('abbe number', 've', header_row, 'Z'),
            ('specific gravity', 'd', header_row, 'GA'),
            ]
        kwargs = dict(
            data_extent = (3, 136, data_col, 'GA'),
            name_col_offset = 'B',
            )
        super().__init__('Ohara', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def create_glass(self, gname: str, gcat: str) -> 'OharaGlass':
        """ Create an instance of the glass `gname`. """
        return OharaGlass(gname)


class OharaGlass(glass.GlassPandas):
    catalog = None

    def initialize_catalog(self):
        if OharaGlass.catalog is None:
            OharaGlass.catalog = OharaCatalog()
        
    def __init__(self, gname):
        self.initialize_catalog()
        super().__init__(gname)

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = 1 + coefs[0]*wv2/(wv2 - coefs[3])
        n2 += coefs[1]*wv2/(wv2 - coefs[4])
        n2 += coefs[2]*wv2/(wv2 - coefs[5])
        return np.sqrt(n2)
