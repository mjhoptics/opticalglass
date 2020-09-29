#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the CDGM Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

from math import sqrt

from . import glass


class CDGMCatalog(glass.GlassCatalog, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'nC': 'nc',
                 'nd': 'nd',
                 'ne': 'ne',
                 'nF': 'nF',
                 'ng': 'ng',
                 'nh': 'nh',
                 'ni': 'ni'}

    def __init__(self, fname='CDGM.xls'):
        super().__init__('CDGM', fname, 'Glass', 'A0', 'nt')

    def get_glass_names(self):
        """ returns a list of glass names """
        gnames = self.xl_data.col_values(self.name_col_offset, self.data_start)
        # filter out any empty cells at the end
        while gnames and (len(gnames[-1]) == 0 or gnames[-1] == 'Over!'):
            gnames.pop()
        return gnames

    def create_glass(self, gname, gcat):
        return CDGMGlass(gname)


class CDGMGlass(glass.Glass):
    catalog = CDGMCatalog()

    def __init__(self, gname, catalog=None):
        if catalog is not None:
            self.catalog = catalog
        super().__init__(gname)

    def glass_code(self):
        return super().glass_code('nd', 'υd')

    def calc_rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return sqrt(n2)
