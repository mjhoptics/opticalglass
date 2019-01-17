#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Support for the Ohara Glass catalog

.. codeauthor: Michael J. Hayford
"""
import logging
from pathlib import Path

from math import sqrt
import xlrd
import numpy as np

from . import glasserror as ge


def get_filepath(fname):
    pth = Path(__file__).resolve()
    try:
        root_pos = pth.parts.index('opticalglass')
    except ValueError:
        logging.debug("Can't find opticalglass: path is %s", pth)
    else:
        path = Path(*pth.parts[:root_pos+1])
        return path/'data'/fname


class OharaCatalog:
    #    data_header = 1
    #    data_start = 2
    #    num_glasses = 134
    #    name_col_offset = 1
    #    coef_col_offset = 60
    #    index_col_offset = 4

    def __init__(self, fname='OHARA.xlsx'):
        # Open the workbook
        xl_workbook = xlrd.open_workbook(get_filepath(fname))
        self.xl_data = xl_workbook.sheet_by_index(0)
        for i in range(0, self.xl_data.nrows):
            try:
                self.name_col_offset = (self.xl_data.row_values(i, 0)
                                        .index('Glass '))
                glass_header = i
                self.data_header = i
                break
            except ValueError:
                pass

        for j in range(glass_header+1, self.xl_data.nrows):
            gname = self.xl_data.cell_value(j, self.name_col_offset)
            if len(gname) > 0:
                self.data_start = j
                break

        gnames = self.get_glass_names()
        self.num_glasses = len(gnames)

        colnames = self.xl_data.row_values(self.data_header, 0)
        self.coef_col_offset = colnames.index('A1')
        self.index_col_offset = colnames.index('n2325')

    def get_glass_names(self):
        """ returns a list of glass names """
        gnames = self.xl_data.col_values(self.name_col_offset, self.data_start)
        # filter out any empty cells at the end
        while gnames and len(gnames[-1]) is 0:
            gnames.pop()
        return gnames

    def glass_index(self, gname):
        gnames = self.xl_data.col_values(self.name_col_offset, self.data_start)
        if gname in gnames:
            gindex = gnames.index(gname)
        else:
            logging.info('Ohara glass %s not found', gname)
            raise ge.GlassNotFoundError("Ohara", gname)

        return gindex

    def data_index(self, dname):
        if dname in self.xl_data.row_values(self.data_header, 0):
            dindex = self.xl_data.row_values(self.data_header, 0).index(dname)
        else:
            logging.info('Ohara glass data type %s not found', dname)
            raise ge.GlassDataNotFoundError("Ohara", dname)

        return dindex

    def glass_data(self, row):
        return self.xl_data.row_values(self.data_start+row, 0)

    def catalog_data(self, col):
        return self.xl_data.col_values(col, self.data_start,
                                       self.data_start+self.num_glasses)

    def glass_coefs(self, gindex):
        return (self.xl_data.row_values(self.data_start+gindex,
                                        self.coef_col_offset,
                                        self.coef_col_offset+6))

    def glass_map_data(self, wvl='d'):
        if wvl == 'd':
            nd = np.array(self.catalog_data(self.data_index('nd')))
            nF = np.array(self.catalog_data(self.data_index('nF')))
            nC = np.array(self.catalog_data(self.data_index('nC')))
            dFC = nF-nC
            vd = (nd - 1.0)/dFC
            PCd = (nd-nC)/dFC
            names = self.catalog_data(self.name_col_offset)
            return nd, vd, PCd, names
        elif wvl == 'e':
            ne = np.array(self.catalog_data(self.data_index('ne')))
            nF = np.array(self.catalog_data(self.data_index('nF')))
            nC = np.array(self.catalog_data(self.data_index('nC')))
            dFC = nF-nC
            ve = (ne - 1.0)/dFC
            PCe = (ne-nC)/dFC
            names = self.catalog_data(self.name_col_offset)
            return ne, ve, PCe, names
        else:
            return None


class OharaGlass:
    catalog = OharaCatalog()

    def __init__(self, gname, ctlg=None):
        self.gindex = self.catalog.glass_index(gname)
        self.gname = gname

    def __repr__(self):
        return 'Ohara ' + self.name() + ': ' + self.glass_code()

    def sync_to_restore(self):
        self.gindex = self.catalog.glass_index(self.gname)

    def glass_code(self):
        nd = self.glass_item('nd')
        vd = self.glass_item('νd')
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def glass_data(self):
        return self.catalog.glass_data(self.gindex)

    def name(self):
        return self.gname

    def glass_item(self, dname):
        dindex = self.catalog.data_index(dname)
        if dindex is None:
            return None
        else:
            return self.glass_data()[dindex]

    def rindex(self, wv_nm):
        wv = 0.001*wv_nm
        wv2 = wv*wv
        coefs = self.catalog.glass_coefs(self.gindex)
        n2 = 1 + coefs[0]*wv2/(wv2 - coefs[3])
        n2 += coefs[1]*wv2/(wv2 - coefs[4])
        n2 += coefs[2]*wv2/(wv2 - coefs[5])
        return sqrt(n2)
