#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Support for the Sumita Glass catalog

.. Created on Tue Aug 25 22:20:20 2020

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

from math import sqrt

from . import glass


class SumitaCatalog(glass.GlassCatalog, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'nC': 'nC',
                 'nd': 'nd',
                 'ne': 'ne',
                 'nF': 'nF',
                 'ng': 'ng',
                 'nh': 'nh',
                 'ni': 'ni'}

    def __init__(self, fname='SUMITA.xlsx'):
        super().__init__('Sumita', fname, 'GNAME', 'A0', 'n1548')

    def create_glass(self, gname, gcat):
        return SumitaGlass(gname)


class SumitaGlass(glass.Glass):
    catalog = SumitaCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('nd', 'vd')

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return sqrt(n2)
