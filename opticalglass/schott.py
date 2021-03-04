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


class SchottCatalog(glass.GlassCatalogXLS, metaclass=Singleton):
    #    data_header = 3
    #    data_start = 4
    #    num_glasses = 123
    #    name_col_offset = 0
    #    coef_col_offset = 6
    #    index_col_offset = 117
    nline_str = {'t': '  nt',
                 's': '  ns',
                 'r': '  nr',
                 'C': '  nC',
                 "C'": "  nC'",
                 'D': '  nD',
                 'd': '  nd',
                 'e': '  ne',
                 'F': '  nF',
                 "F'": "  nF'",
                 'g': '  ng',
                 'h': '  nh',
                 'i': '  ni'}

    def __init__(self, fname='SCHOTT.xls'):
        super().__init__('Schott', fname, 'Glass', 'B1', '  n2325.4',
                         transmission_offset=67, num_wvls=30)

    def create_glass(self, gname, gcat):
        return SchottGlass(gname)

    def get_transmission_wvl(self, header_str):
        """Returns the wavelength value from the transmission data header string."""
        return float(header_str[len('TAUI10/'):])


class SchottGlass(glass.Glass):
    catalog = SchottCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('nd', 'vd')

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = 1. + coefs[0]*wv2/(wv2 - coefs[3])
        n2 = n2 + coefs[1]*wv2/(wv2 - coefs[4])
        n2 = n2 + coefs[2]*wv2/(wv2 - coefs[5])
        return np.sqrt(n2)
