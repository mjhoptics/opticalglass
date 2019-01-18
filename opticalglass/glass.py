#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Michael J. Hayford
""" Support for Glass catalogs and instances

.. codeauthor: Michael J. Hayford
"""
import logging
from pathlib import Path

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


class GlassCatalog:
    """ base glass catalog

    Args:
        name: name of the glass catalog
        fname: excel filename, located in ``data`` directory
        glass_str: the header string for the Glass column in fname
        coef_str: the header string for the first refractive index coefficient
                  column in fname
        rindex_str: the header string for the first refractive index value
                    column in fname

    Attributes:
        num_glasses: number of glasses in the catalog
        data_header: the row containing the data header labels
        data_start: first row in the spreadsheet contain glass data
        name_col_offset = the column offset for glass_str
        coef_col_offset: the column offset for coef_str
        index_col_offset: the column offset for rindex_str
        data_header_offset: the row offset of the data headers from the
                            glass_str row
    """

    def __init__(self, name, fname, glass_str, coef_str, rindex_str,
                 data_header_offset=0):
        # Open the workbook
        xl_workbook = xlrd.open_workbook(get_filepath(fname))
        self.xl_data = xl_workbook.sheet_by_index(0)

        for i in range(0, self.xl_data.nrows):
            try:
                self.name_col_offset = (self.xl_data.row_values(i, 0)
                                        .index(glass_str))
                glass_header = i
                self.data_header = i
                # the data headers may be offset from the Glass header row
                self.data_header += data_header_offset
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
        self.coef_col_offset = colnames.index(coef_str)
        self.index_col_offset = colnames.index(rindex_str)

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
            logging.info('%s glass %s not found', self.name, gname)
            raise ge.GlassNotFoundError(self.name, gname)

        return gindex

    def data_index(self, dname):
        if dname in self.xl_data.row_values(self.data_header, 0):
            dindex = self.xl_data.row_values(self.data_header, 0).index(dname)
        else:
            logging.info('%s glass data type %s not found', self.name, dname)
            raise ge.GlassDataNotFoundError(self.name, dname)

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

    def glass_map_data(self, nd_str, nf_str, nc_str):
        nd = np.array(self.catalog_data(self.data_index(nd_str)))
        nF = np.array(self.catalog_data(self.data_index(nf_str)))
        nC = np.array(self.catalog_data(self.data_index(nc_str)))
        dFC = nF-nC
        vd = (nd - 1.0)/dFC
        PCd = (nd-nC)/dFC
        names = self.catalog_data(self.name_col_offset)
        return nd, vd, PCd, names


class Glass:
    """ base optical glass

    Attributes:
        gname: the glass name
        gindex: the index into the glass list
        catalog: the GlassCatalog this glass is associated with. Must be
                 provided by the derived class
    """
    def __init__(self, gname):
        self.gindex = self.catalog.glass_index(gname)
        self.gname = gname

    def __repr__(self):
        return self.catalog.name + ' ' + self.name() + ': ' + self.glass_code()

    def sync_to_restore(self):
        self.gindex = self.catalog.glass_index(self.gname)

    def glass_code(self, nd_str, vd_str):
        nd = self.glass_item(nd_str)
        vd = self.glass_item(vd_str)
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
        """ returns the interpolated refractive index at wv_nm

        Args:
            wv_nm (float): wavelength in nm for the refractive index query

        Returns:
            float: the refractive index at wv_nm
        """
        pass
