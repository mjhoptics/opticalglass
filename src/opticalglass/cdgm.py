#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the CDGM Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np
import pandas as pd

from . import glass


def decode_dispersion_coefs(glas: pd.Series) -> tuple[list, str]:
    """ Decode CDGM dispersion to Sellmeier or Schott formula. """
    dispersion_coefs = glas['dispersion coefficients']
    if pd.notna(dispersion_coefs.loc['K1']):
        coefs = dispersion_coefs.loc['K1':'L3'].to_numpy(dtype=float)
        interp_formula = "sellmeier"
    else:  # pd.notna(glas['dispersion coefficients'].loc['A0'])
        coefs = dispersion_coefs.loc['A0':'A5'].to_numpy(dtype=float)
        interp_formula = "schott"
    return coefs, interp_formula


class CDGMCatalog(glass.GlassCatalogPandas, metaclass=Singleton):

    def __init__(self, fname='CDGM202409.xlsx'):
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
             category_row, 'C', 'V'),
            # ('dispersion coefficients', None, category_row, 'AB', 'AG'),
            # ('dispersion coefficients', None, category_row, 'AH', 'AM'),
            ('dispersion coefficients', None, category_row, 'AB', 'AM'),
            ('internal transmission mm, 10', None, header_row, 'EC', 'FK'),
            ('chemical properties', None, category_row, 'BM', 'BQ'),
            ('thermal properties', None, category_row, 'BU', 'CB'),
            ('mechanical properties', None, category_row, 'CE', 'CJ'),
            ]
        item_mappings = [
            ('refractive indices', 'C', header_row, 'J'),
            ('refractive indices', "C'", header_row, 'K'),
            ('abbe number', 'vd', header_row, 'X'),
            ('abbe number', 've', header_row, 'Y'),
            ('specific gravity', 'd', header_row, 'CK'),
            ]
        kwargs = dict(
            data_extent = (3, 323, data_col, 'HZ'),
            name_col_offset = 'A',
            )
        super().__init__('CDGM', fname, series_mappings, item_mappings, 
                         *args, **kwargs)

    def glass_coefs(self, gname):
        """ returns an array of glass coefficients for the glass at *gname* """
        glas = self.df.loc[gname]
        coefs, interp_formula = decode_dispersion_coefs(glas)
        return coefs
    
    def create_glass(self, gname: str, gcat: str) -> 'CDGMGlass':
        """ Create an instance of the glass `gname`. """
        return CDGMGlass(gname)


class CDGMGlass(glass.GlassPandas):
    catalog: CDGMCatalog | None = None

    def initialize_catalog(self):
        if CDGMGlass.catalog is None:
            CDGMGlass.catalog = CDGMCatalog()
        
    def __init__(self, gname):
        self.initialize_catalog()
        super().__init__(gname)
        glas = CDGMGlass.catalog.df.loc[gname]
        _, self.interp_formula = decode_dispersion_coefs(glas)

    def calc_rindex(self, wv_nm):
        if self.interp_formula == 'sellmeier':
            return self.calc_rindex_sellmeier(wv_nm)
        else:
            return self.calc_rindex_schott(wv_nm)

    def calc_rindex_schott(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return np.sqrt(n2)

    def calc_rindex_sellmeier(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = 1.
        for i in range(0,6,2):
            Ki, Li = coefs[i], coefs[i+1]
            n2 += Ki*wv2 / (wv2 - Li)
        return np.sqrt(n2)
