#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Support for the Sumita Glass catalog

.. Created on Tue Aug 25 22:20:20 2020

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np

from . import glass


class SumitaCatalog(glass.GlassCatalogPandas, metaclass=Singleton):

    def get_rindx_wvl(header_str):
        """Returns the wavelength value from the refractive index data header string."""
        hdr = header_str.split('n')[-1]
        try:
            h = float(hdr)
        except ValueError:
            h = hdr
        return h

    def get_transmission_wvl(header_str):
        """Returns the wavelength value from the transmission data header string."""
        return float(header_str[len('T2_'):])

    def __init__(self, fname='SUMITA.xlsx'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 2  # number of header rows in the imported spreadsheet
        category_row = 1  # row with categories
        header_row = 2  # row with data item/header info
        data_col = 'D'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', SumitaCatalog.get_rindx_wvl, 
             header_row, 'H', 'V'),
            ('dispersion coefficients', None, header_row, 'AV', 'BA'),
            ('internal transmission mm, 10', 
             SumitaCatalog.get_transmission_wvl, header_row, 'DB', 'EB'),
            ('chemical properties', None, header_row, 'BQ', 'BT'),
            ('thermal properties', None, header_row, 'BI', 'BP'),
            ('mechanical properties', None, header_row, 'BB', 'BH'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'D'),
            ('abbe number', 've', header_row, 'E'),
            ('specific gravity', 'd', header_row, 'BX'),
            ]
        kwargs = dict(
            data_extent = (3, 136, data_col, 'FC'),
            name_col_offset = 'C',
            )
        super().__init__('Sumita', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def create_glass(self, gname: str, gcat: str) -> 'SumitaGlass':
        """ Create an instance of the glass `gname`. """
        return SumitaGlass(gname)


class SumitaGlass(glass.GlassPandas):
    catalog = None

    def initialize_catalog(self):
        if SumitaGlass.catalog is None:
            SumitaGlass.catalog = SumitaCatalog()
        
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
