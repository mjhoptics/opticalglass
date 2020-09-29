#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""
from math import sqrt
from .util import Singleton

from . import glass


class HoyaCatalog(glass.GlassCatalog, metaclass=Singleton):
    #    data_header = 1
    #    data_start = 4
    #    num_glasses = 194
    #    name_col_offset = 2
    #    coef_col_offset = 28
    #    index_col_offset = 10
    nline_str = {'nC': 'nC',
                 'nd': 'nd',
                 'ne': 'ne',
                 'nF': 'nF',
                 'ng': 'ng',
                 'nh': 'nh',
                 'ni': 'ni'}

    def __init__(self, fname='HOYA.xlsx'):
        super().__init__('Hoya', fname, 'Glass\u3000Type', 'A0', 'n1529.6',
                         data_header_offset=1)

    def glass_coefs(self, gindex):
        c = (self.xl_data.row_values(self.data_start+gindex,
                                     self.coef_col_offset,
                                     self.coef_col_offset+12))
        return [x*10**y for x, y in zip(c[::2], c[1::2])]

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
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return sqrt(n2)
