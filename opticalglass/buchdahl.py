#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Buchdahl chromatic coordinate modeling and support

.. Created on Thu Aug 20 21:27:36 2020

.. codeauthor: Michael J. Hayford
"""

import numpy as np

from .spectral_lines import get_wavelength


def get_wv(wavelength):
    """Return the wavelength in micrometers."""
    return get_wavelength(wavelength)*1e-3


def omega(delta_lambda):
    """Calculate the Buchdahl chromatic coordinate."""
    return delta_lambda/(1 + 2.5*delta_lambda)


def omega2wvl(om):
    return om/(1 - 2.5*om)


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


class Buchdahl:
    """Quadratic Buchdahl refractive index model.

    .. math::

        N(\omega) = {N_0} + \\nu_1\omega + \\nu_2\omega^2

    - :math:`\omega` is the Buchdahl chromatic coordinate for the input wavelength
    - :math:`\\nu_1, \\nu_2` are the linear and quadratic coefficients of the model
    - :math:`{N_0}` is the refractive index at the central wavelength of the fit

    The Buchdahl chromatic coordinate :math:`\omega` is defined as:

    .. math::

        \omega(\lambda) = \\frac{\lambda - \lambda_0}{1 + 5/2(\lambda - \lambda_0)}

    """

    def __init__(self, wv0, rind0, coefs, mat='', cat=''):
        """
        Parameters
        ----------
        wv0 : float
            central wavelength in **micrometers**.
        rind0 : float
            refractive index at the central wavelength.
        coefs : (float, float)
            the linear and quadratic coefficients of the model.
        mat : str
            a string label returned from the name() fct.
        cat : str
            a string label returned from the catalog_name() fct.
        """
        self.wv0 = wv0
        self.rind0 = rind0
        self.coefs = coefs
        self.label = mat
        self._catalog_name = cat

    def name(self):
        return self.label

    def catalog_name(self):
        return self._catalog_name

    def glass_code(self):
        nd = self.rindex('d')
        nF = self.rindex('F')
        nC = self.rindex('C')
        vd = (nd - 1)/(nF - nC)
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def rindex(self, wvl):
        """Returns the refractive index from the quadratic model at wvl."""
        om = omega(get_wv(wvl) - self.wv0)
        return self.rind0 + self.coefs[0]*om + self.coefs[1]*om**2


class Buchdahl1(Buchdahl):
    """Quadratic refractive index model for a real glass, *medium*. """

    def __init__(self, medium, wlns=('d', 'F', 'C'), **kwargs):
        rindx = [medium.rindex(wlns[0]),
                 medium.rindex(wlns[1]),
                 medium.rindex(wlns[2])]

        wv0 = get_wv(wlns[0])
        omF = omega(get_wv(wlns[1]) - wv0)
        omC = omega(get_wv(wlns[2]) - wv0)
        self.om = omF, omC

        coefs = self.update(rindx)
        super().__init__(wv0, rindx[0], coefs, **kwargs)

    def update(self, rindx):
        omF, omC = self.om
        a = np.array([[omF, omF**2], [omC, omC**2]])
        b = np.array([rindx[1]-rindx[0], rindx[2]-rindx[0]])
        coefs = np.linalg.solve(a, b)
        return coefs


class Buchdahl2(Buchdahl):
    """Quadratic refractive index model for a 6-digit glass specification. """

    b = -0.064667
    m = -1.604048

    def __init__(self, nd, vd, model=None, wlns=('d', 'F', 'C'), **kwargs):
        if model is not None:
            self.b, self.m = model
        wv0 = get_wv(wlns[0])
        omF = omega(get_wv(wlns[1]) - wv0)
        omC = omega(get_wv(wlns[2]) - wv0)
        delta_om = omF - omC
        delta_om2 = omF**2 - omC**2
        self.om = omF, omC, delta_om, delta_om2
        rind0, coefs = self.update(nd, vd)
        super().__init__(wv0, rind0, coefs, **kwargs)

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
