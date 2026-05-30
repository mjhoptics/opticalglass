#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Utilities including Singleton metaclass

.. Created on Wed Sep 16 21:42:49 2020

.. codeauthor: Michael J. Hayford
"""


from dataclasses import dataclass


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


def move_to(cltn: list, i: int, item: object) -> list:
    """ Move item to index i in collection cltn. """
    try:
        cltn.remove(item)
    except ValueError:
        # item not in cltn, nothing to move
        return cltn
    else:
        cltn.insert(i, item)
    return cltn


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


@dataclass(frozen=True)
class DecodedGlassName:
    prefix: str
    group: str
    num: str
    suffix: str

    @property
    def name(self) -> str:
        if self.prefix and self.suffix:
            return f"{self.prefix}-{self.group}{self.num}-{self.suffix}"
        elif self.prefix and not self.suffix:
            return f"{self.prefix}-{self.group}{self.num}"
        elif not self.prefix and self.suffix:
            return f"{self.group}{self.num}-{self.suffix}"
        else:
            return f"{self.group}{self.num}"

    @property
    def group_num(self) -> str:
        return f"{self.group}{self.num}"

    def astuple(self) -> tuple[str, str, str, str]:
        return (self.prefix, self.group, self.num, self.suffix)


def decode_glass_name(glass_name: str) -> DecodedGlassName:
    """Split glass_name into prefix, group, num, suffix.

    Manufacturers glass names follow a common pattern. At the simplest, it is
    a short character string, typically used to identify a particular glass
    composition, with a numeric qualifier. The composition group and product
    serial number are combined to form the basic product id, the group_num:

        - F2
        - SF56

    Manufacturers will often use a single character prefix to indicate
    different categories of glasses, e.g. moldable or "New":

        - N-BK7
        - P-LASF50

    Similarly, a suffix with one or more characters is often used to
    differentiate between different variations of the same base material.

        - N-SF57
        - N-SF57HT
        - N-SF57HTultra

    This function takes an input glass name and returns a tuple of strings. A
    valid glass_name should always have a non-null group_num; prefixes and
    suffixes are optional and used differently by different manufacturers.

        * group_num, prefix, suffix
        * group, num = group_num

    Args:
        glass_name (str): a glass manufacturer's glass name

    Returns: group_num, prefix, suffix, where group_num = group, num

    Returned strings are uppercase.

    """
    gn = glass_name.upper().split('-')
    suffix = ''
    if len(gn) == 1:
        prefix = ''
        gn2 = gn[0]
    elif len(gn) == 3:
        prefix = gn[0]
        suffix = gn[2]
        gn2 = gn[1]
    elif len(gn) == 2:
        if len(gn[0]) < 3:
            prefix = gn[0]
            gn2 = gn[1]
        else:
            prefix = ''
            gn2 = gn[0]
            suffix = gn[1]

    group = gn2
    num = ''
    for i, char in enumerate(gn2):
        if char.isdigit():
            start = i
            while i < len(gn2) and gn2[i].isdigit():
                i += 1
            group = gn2[:start].rstrip()
            num = gn2[start:i]
            break
    suffix = gn2[i:] if suffix == '' else suffix

    return DecodedGlassName(prefix, group, num, suffix)

