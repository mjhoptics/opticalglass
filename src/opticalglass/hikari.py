#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Support for the Hikari Glass catalog

.. Created on Tue Aug 25 22:55:44 2020

.. codeauthor: Michael J. Hayford
"""

import logging

import numpy as np

from . import glass as xls_glass


class HikariCatalog(xls_glass.GlassCatalogPandas):
    @staticmethod
    def get_rindx_wvl(header_str):
        """Returns the wavelength value from the refractive index data header string."""
        if isinstance(header_str, float):
            value = 1000*header_str
        else:
            value = header_str.split()[0]
        return value

    @staticmethod
    def get_transmission_wvl(header_str):
        """Returns the wavelength header string."""
        return float(header_str[:-len('nm')])

    def __init__(self, catalog_name:str='Hikari',
                 fname:str='hikari_general_catalog_data.xlsx', 
                 last_data_row:int=163):
        # the xl_df has indices and columns that match the Excel worksheet border.
        # the index runs from 1 to xl_df.shape[0]
        # the columns match the pattern 'A', 'B', 'C', ... 'Z', 'AA', 'AB', ...
        # this facilitates transferring areas on the spreadsheet to areas in the catalog DataFrame

        num_rows = 3  # number of header rows in the imported spreadsheet
        category_row = 2  # row with categories
        header_row = 3  # row with data item/header info
        data_col = 'B'  # first column of data in the imported spreadsheet
        args = num_rows, category_row , header_row, data_col

        first_data_row = 4

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
            data_extent = (first_data_row, last_data_row, data_col, 'GE'),
            name_col_offset = 'A',
            )
        pmd = xls_glass.PandasMappingDef(catalog_name, fname, series_mappings,
                                         item_mappings, args, kwargs)

        self.pmd = pmd
        super().__init__(pmd)
        HikariGlass.catalog = self

    def create_glass(self, gname: str) -> 'HikariGlass':
        """ Create an instance of the glass `gname`. """
        return HikariGlass(gname)


class HikariGlass(xls_glass.GlassPandas):
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
