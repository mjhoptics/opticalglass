#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Schott Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np

from . import glass


class SchottCatalog(glass.GlassCatalogPandas, metaclass=Singleton):

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
        return float(header_str[len('TAUI10/'):])

    def __init__(self, fname='SCHOTT.xls'):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame
        
        num_rows = 4  # number of header rows in the imported spreadsheet
        category_row = 3  # row with categories
        header_row = 4  # row with data item/header info
        data_col = 'B'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col
        
        series_mappings = [
            ('refractive indices', SchottCatalog.get_rindx_wvl, header_row, 
             'DM', 'EI'),
            ('dispersion coefficients', None, header_row, 'G', 'L'),
            ('internal transmission mm, 10', 
             SchottCatalog.get_transmission_wvl, header_row, 'BP', 'CS'),
            ('chemical properties', None, header_row, 'CU', 'CY'),
            ('thermal properties', None, header_row, 'DA', 'DG'),
            ('mechanical properties', None, header_row, 'DH', 'DK'),
            ]
        item_mappings = [
            ('abbe number', 'vd', header_row, 'D'),
            ('abbe number', 've', header_row, 'E'),
            ('specific gravity', 'd', header_row, 'CZ'),
            ]
        kwargs = dict(
            data_extent = (5, 127, data_col, 'FJ'),
            name_col_offset = 'A',
            )
        super().__init__('Schott', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def create_glass(self, gname: str, gcat: str) -> 'SchottGlass':
        """ Create an instance of the glass `gname`. """
        return SchottGlass(gname)


class SchottGlass(glass.GlassPandas):
    catalog = None

    def initialize_catalog(self):
        if SchottGlass.catalog is None:
            SchottGlass.catalog = SchottCatalog()
        
    def __init__(self, gname):
        self.initialize_catalog()
        super().__init__(gname)

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = 1. + coefs[0]*wv2/(wv2 - coefs[3])
        n2 = n2 + coefs[1]*wv2/(wv2 - coefs[4])
        n2 = n2 + coefs[2]*wv2/(wv2 - coefs[5])
        return np.sqrt(n2)
