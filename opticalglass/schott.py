#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Schott Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

from math import sqrt

from . import glass


class SchottCatalog(glass.GlassCatalog, metaclass=Singleton):
    #    data_header = 3
    #    data_start = 4
    #    num_glasses = 123
    #    name_col_offset = 0
    #    coef_col_offset = 6
    #    index_col_offset = 117
    nline_str = {'nC': '  nC',
                 'nd': '  nd',
                 'ne': '  ne',
                 'nF': '  nF',
                 'ng': '  ng',
                 'nh': '  nh',
                 'ni': '  ni'}

    def __init__(self, fname='SCHOTT.xls'):
        super().__init__('Schott', fname, 'Glass', 'B1', '  n2325.4')

    def create_glass(self, gname, gcat):
        return SchottGlass(gname)


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
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = 1. + coefs[0]*wv2/(wv2 - coefs[3])
        n2 = n2 + coefs[1]*wv2/(wv2 - coefs[4])
        n2 = n2 + coefs[2]*wv2/(wv2 - coefs[5])
        return sqrt(n2)
