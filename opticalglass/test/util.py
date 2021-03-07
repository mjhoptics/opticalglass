#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Utilities to support testing of Glass and Glass catalog

.. codeauthor: Michael J. Hayford
"""

spectral_lines = ['t', 's', 'r', 'C', "C'", 'D', 'd',
                  'e', 'F', "F'", 'g', 'h', 'i']


def compare_indices(tc, glass, catalog, tol=5e-6, slines=spectral_lines):
    """Compare calculated to measured refractive indices at spectral_lines.

    Args:
        tc: the testcase instance for this comparison
        glass: the glass instance being tested
        catalog: the catalog of the glass instance
        tol: the allowed difference between calculated and measured results
        slines: a list of strings of the spectral lines to be compared
    """
    nline = catalog.nline_str
    
    for sline in slines:
        n_calc = glass.rindex(sline)
        n_meas = glass.glass_item(nline[sline])
        tc.assertAlmostEqual(n_calc, n_meas, delta=tol,
                             msg=f'spectral line {sline:} outside tol')
