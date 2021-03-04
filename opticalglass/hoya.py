#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""

import numpy as np
from .util import Singleton

from . import glass


class HoyaCatalog(glass.GlassCatalogXLSX, metaclass=Singleton):
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


class HoyaGlass(glass.Glass):
    catalog = HoyaCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('nd', 'νd')

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.coefs
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return np.sqrt(n2)
