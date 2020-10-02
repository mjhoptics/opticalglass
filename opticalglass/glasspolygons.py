#!/usr/bin/env python3
# Copyright Â© 2019 Michael J. Hayford
# -*- coding: utf-8 -*-
""" create glass map glass designation polygons

.. Created on Mon Apr  1 20:05:42 2019

.. codeauthor: Michael J. Hayford
"""

from matplotlib.patches import Polygon

# The polygon corners are [10., 2.20] and [110., 1.35]
polygons = {'LAF': [[50., 1.66], [50., 2.20], [18.8, 2.20], [26., 1.81],
                    [30., 1.72], [36., 1.72]],
            'BAF': [[50., 1.54], [50., 1.66], [36., 1.72], [30., 1.72],
                    [36., 1.64], [40., 1.59]],
            'F': [[50., 1.51], [50., 1.54], [40., 1.59], [36., 1.64],
                  [30., 1.72], [26., 1.81], [18.8, 2.20], [10., 2.20],
                  [10., 2.103], [24., 1.75], [36., 1.58], [40., 1.55]],
            'F_lwr': [[50., 1.35], [50., 1.51], [40., 1.55], [36., 1.58],
                      [24., 1.75], [10., 2.103], [10., 1.35]],
            'C': [[67., 1.49], [63., 1.53], [55., 1.53], [50., 1.54],
                  [50., 1.51], [55., 1.50], [63., 1.49]],
            'C_lwr': [[67., 1.49], [63., 1.49], [55., 1.50], [50., 1.51],
                      [50., 1.35], [67., 1.35]],
            'BAC': [[63., 1.53], [63., 1.62], [55., 1.64], [50., 1.66],
                    [50., 1.54], [55., 1.53]],
            'LAC': [[110., 1.62], [110., 2.20], [50., 2.20], [50., 1.66],
                    [55., 1.64], [63., 1.62]],
            'ED': [[110., 1.35], [110., 1.62], [63., 1.62], [63., 1.53],
                   [67., 1.49], [67., 1.35]]
            }


rgb = {'LAC': [5	, 112, 176, 64],
       'BAC': [111, 170, 212, 64],
       'C': [184, 211, 230, 64],
       'C_lwr': [184, 211, 230, 64],
       'ED': [228, 237, 243, 64],
       'F': [253, 204, 138, 64],
       'F_lwr': [253, 204, 138, 64],
       'BAF': [252, 143, 89, 64],
       'LAF': [215, 77, 31, 64]
       }


def find_glass_designation(nd, vd):
    """ find the designation and rgb color for the input index and V number

    Args:
        nd: refractive index, d line
        vd: V-number, d line

    Returns:
        designation label, RGBA list
    """
    for key, poly in polygons.items():
        p = Polygon(poly, closed=True)
        if p.contains_point([vd, nd]):
            c = rgb[key]
            return key, c
    return None, None
