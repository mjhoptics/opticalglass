#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Hoya Glass catalog

.. codeauthor: Michael J. Hayford
"""
from math import sqrt

from . import glass


class HoyaCatalog(glass.GlassCatalog):
    #    data_header = 1
    #    data_start = 4
    #    num_glasses = 194
    #    name_col_offset = 2
    #    coef_col_offset = 28
    #    index_col_offset = 10

    def __init__(self, fname='HOYA.xlsx'):
        super().__init__('Hoya', fname, 'Glass\u3000Type', 'A0', 'n1529.6',
                         data_header_offset=1)

    def glass_coefs(self, gindex):
        c = (self.xl_data.row_values(self.data_start+gindex,
                                     self.coef_col_offset,
                                     self.coef_col_offset+12))
        return [x*10**y for x, y in zip(c[::2], c[1::2])]

    def glass_map_data(self, wvl='d'):
        if wvl == 'd':
            return super().glass_map_data('nd', 'nF', 'nC')
        elif wvl == 'e':
            return super().glass_map_data('ne', 'nF', 'nC')
        else:
            return None


class HoyaGlass(glass.Glass):
    catalog = HoyaCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('nd', 'νd')

    def rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return sqrt(n2)
