#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Utilities including Singleton metaclass

.. Created on Wed Sep 16 21:42:49 2020

.. codeauthor: Michael J. Hayford
"""


class Counter(dict):
    """A dict that initializes a missing key's value to 0.

    Example:
        track_changes = Counter()
        track_changes['something happened'] += 1
        track_changes['something not found'] += 1
        """

    def __missing__(self, key):
        return 0


class Singleton(type):
    """A metaclass implementation for the Singleton pattern.

    Example:

        class JustOne(metaclass=Singleton):
            pass
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = (super(Singleton, cls).
                                   __call__(*args, **kwargs))
        return cls._instances[cls]


def rgb2mpl(rgb):
    """ convert 8 bit RGB data to 0 to 1 range for mpl """
    if len(rgb) == 3:
        return [rgb[0]/255., rgb[1]/255., rgb[2]/255., 1.0]
    elif len(rgb) == 4:
        return [rgb[0]/255., rgb[1]/255., rgb[2]/255., rgb[3]/255.]


def calc_glass_constants(nd, nF, nC, *partials):
    """Given central, blue and red refractive indices, calculate Vd and PFd.
    
    Args:
        nd, nF, nC: refractive indices at central, short and long wavelengths
        partials (tuple): if present, 2 ref indxs, n4 and n5, wl4 < wl5
        
    Returns:
        V-number and relative partial dispersion from F to d

    If `partials` is present, the return values include the central wavelength
    index and the relative partial dispersion between the 2 refractive indices
    provided from `partials`.
    """
    dFC = nF-nC
    vd = (nd - 1.0)/dFC
    PFd = (nF-nd)/dFC
    if len(partials) == 2:
        n4, n5 = partials
        P45 = (n4-n5)/dFC
        return nd, vd, PFd, P45
    return vd, PFd
