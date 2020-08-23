#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Buchdahl chromatic coordinate modeling and support

.. Created on Thu Aug 20 21:27:36 2020

.. codeauthor: Michael J. Hayford
"""

import math
import numpy as np

from rayoptics.util.spectral_lines import get_wavelength


def get_wv(wavelength):
    """Return the wavelength in micrometers."""
    return get_wavelength(wavelength)*1e-3


def omega(delta_lambda):
    """Calculate the Buchdahl chromatic coordinate."""
    return delta_lambda/(1 + 2.5*delta_lambda)


def omega2wvl(om):
    return om/(1 - 2.5*om)


class Buchdahl:
    """Quadratic Buchdahl refractive index model. """

    def __init__(self, wv0, rind0, coefs):
        self.coefs = coefs

        self.wv0 = wv0
        self.rind0 = rind0

    def rindex(self, wvl):
        om = omega(get_wv(wvl) - self.wv0)
        return self.rind0 + self.coefs[0]*om + self.coefs[1]*om**2


class Buchdahl1(Buchdahl):
    """Quadratic refractive index model for a real glass, *medium*. """

    def __init__(self, medium, wlns=('F', 'd', 'C')):
        rindx = [medium.rindex(wlns[0]),
                 medium.rindex(wlns[1]),
                 medium.rindex(wlns[2])]

        wv0 = get_wv(wlns[1])
        omC = omega(get_wv(wlns[2]) - wv0)
        omF = omega(get_wv(wlns[0]) - wv0)
        self.om = omF, omC

        coefs = self.update(rindx)
        super().__init__(wv0, rindx[1], coefs)

    def update(self, rindx):
        omF, omC = self.om
        a = np.array([[omF, omF**2], [omC, omC**2]])
        b = np.array([rindx[0]-rindx[1], rindx[2]-rindx[1]])
        coefs = np.linalg.solve(a, b)
        return coefs


class Buchdahl2(Buchdahl):
    """Quadratic refractive index model for a 6-digit glass specification. """

    b = -0.064667
    m = -1.604048

    def __init__(self, nd, vd, wlns=('F', 'd', 'C'), model=None):
        if model is not None:
            self.b, self.m = *model
        wv0 = get_wv(wlns[1])
        omC = omega(get_wv(wlns[2]) - wv0)
        omF = omega(get_wv(wlns[0]) - wv0)
        delta_om = omF - omC
        delta_om2 = omF**2 - omC**2
        self.om = omF, omC, delta_om, delta_om2
        rind0, coefs = self.update(nd, vd)
        super().__init__(wv0, rind0, coefs)

    def update(self, nd, vd):
        omF, omC, delta_om, delta_om2 = self.om
        dFC = (nd - 1.0)/vd
        v2 = (dFC - self.b*delta_om)/(self.m*delta_om - delta_om2)
        v1 = self.b + self.m*v2
        return nd, np.array([v1, v2])

    def update_model(self, nd, vd):
        rind0, coefs = self.update(nd, vd)
        self.rind0 = rind0
        self.coefs = coefs
