#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Support for the Hikari Glass catalog

.. Created on Tue Aug 25 22:55:44 2020

.. codeauthor: Michael J. Hayford
"""

import logging
from .util import Singleton

from math import sqrt

from . import glass


class HikariCatalog(glass.GlassCatalog, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'nC': 'C\n0.656273',
                 'nd': 'd\n0.587562',
                 'ne': 'e\n0.546074',
                 'nF': 'F\n0.486133',
                 'ng': 'g\n0.435835',
                 'nh': 'h\n0.404656',
                 'ni': 'i\n0.365015'}

    def __init__(self, fname='HIKARI.xls'):
        super().__init__('Hikari', fname, 'Glass type', 'A0', 2.05809,
                         data_header_offset=1, glass_name_offset=2,
                         num_coefs=9)

    def create_glass(self, gname, gcat):
        return HikariGlass(gname)


class HikariGlass(glass.Glass):
    catalog = HikariCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('d\n0.587562', 'νd')

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = coefs[0] + wv2*(coefs[1] + wv2*coefs[2])
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[3] +
                        wvm2*(coefs[4] +
                              wvm2*(coefs[5] +
                                    wvm2*(coefs[6] +
                                          wvm2*(coefs[7] +
                                                wvm2*coefs[8])))))
        return sqrt(n2)
