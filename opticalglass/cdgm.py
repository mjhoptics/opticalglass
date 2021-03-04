#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the CDGM Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from .util import Singleton

import numpy as np

from . import glass


class CDGMCatalog(glass.GlassCatalogXLS, metaclass=Singleton):
    #    data_header = 0
    #    data_start = 2
    #    num_glasses = 240
    #    name_col_offset = 0
    #    coef_col_offset = 21
    #    index_col_offset = 2
    nline_str = {'t': 'nt',
                 's': 'ns',
                 'r': 'nr',
                 'C': 'nc',
                 "C'": "nc'",
                 'D': 'nD',
                 'd': 'nd',
                 'e': 'ne',
                 'F': 'nF',
                 "F'": "nF'",
                 'g': 'ng',
                 'h': 'nh',
                 'i': 'ni'}

    def __init__(self, fname='CDGM.xls'):
        super().__init__('CDGM', fname, 'Glass', 'A0', 'nt',
                         transmission_offset=106, num_wvls=34,
                         transmission_header_offset=1)

    def get_glass_names(self):
        """ returns a list of glass names """
        gnames = super().get_glass_names()
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
        coefs = self.coefs
        n2 = coefs[0] + coefs[1]*wv2
        wvm2 = 1/wv2
        n2 = n2 + wvm2*(coefs[2] + wvm2*(coefs[3]
                        + wvm2*(coefs[4] + wvm2*coefs[5])))
        return np.sqrt(n2)
