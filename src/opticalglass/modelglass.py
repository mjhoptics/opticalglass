#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2022 Michael J. Hayford
""" Module for optical glass models based on index/v-number

.. Created on Tue Aug 23 22:41:03 2022

.. codeauthor: Michael J. Hayford
"""

from opticalglass.opticalmedium import OpticalMedium, glass_encode
from opticalglass.buchdahl import Buchdahl1, Buchdahl2


def model_from_glasses(gla1, gla2):
    """Create a model from the slope between two glasses."""
    bhdl_gla1 = Buchdahl1(gla1)
    bhdl_gla2 = Buchdahl1(gla2)
    # get the Buchdahl quadratic coefficients for the 2 input glasses
    v1_gla1, v2_gla1 = bhdl_gla1.coefs[0], bhdl_gla1.coefs[1]
    v1_gla2, v2_gla2 = bhdl_gla2.coefs[0], bhdl_gla2.coefs[1]
    # calculate the slope and v1 intercept of the line between the 2 glasses
    m = (v1_gla1 - v1_gla2)/(v2_gla1 - v2_gla2)
    b = v1_gla1 - m*v2_gla1
    return b, m


class ModelGlass(OpticalMedium):
    """ Optical medium defined by a glass code, i.e. index - V number pair """

    def __init__(self, nd: float, vd: float, mat: str, cat: str='user'):
        self.label = mat
        self._catalog_name = cat
        self.n = nd
        self.v = vd
        self.bdhl_model = Buchdahl2(self.n, self.v)

    def __str__(self):
        return 'ModelGlass ' + self.label + ': ' + glass_encode(self.n, self.v)

    def __repr__(self):
        return ('ModelGlass(nd=' + str(self.n) +
                ', vd=' + str(self.v) +
                ', mat=' + f"'{self.label}'" +
                ', cat=' + f"'{self._catalog_name}'" + ')')

    def sync_to_restore(self):
        if not hasattr(self, 'bdhl_model'):
            self.bdhl_model = Buchdahl2(self.n, self.v)

    def glass_code(self):
        return glass_encode(self.n, self.v)

    def name(self):
        if self.label == '':
            return glass_encode(self.n, self.v)
        else:
            return self.label

    def catalog_name(self):
        return self._catalog_name

    def calc_rindex(self, wv_nm):
        return self.bdhl_model.calc_rindex(wv_nm)

    def meas_rindex(self, wvl):
        return self.rindex(wvl)

    def update(self, nd, vd):
        self.n = nd
        self.v = vd
        self.bdhl_model.update_model(nd, vd)
