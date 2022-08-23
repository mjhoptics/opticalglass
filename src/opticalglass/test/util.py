#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2017 Michael J. Hayford
""" Utilities to support testing of Glass and Glass catalog

.. codeauthor: Michael J. Hayford
"""

spectral_lines = ['t', 's', 'r', 'C', "C'", 'D', 'd',
                  'e', 'F', "F'", 'g', 'h', 'i']


def compare_indices(tc, glass, catalog, tol=5e-6, remove_lines=None):
    """Compare calculated to measured refractive indices at spectral_lines.

    Args:
        tc: the testcase instance for this comparison
        glass: the glass instance being tested
        catalog: the catalog of the glass instance
        tol: the allowed difference between calculated and measured results
        remove_lines: a list of strings **not** to be used in the comparisons,
                      used when data isn't available for that line
    """
    slines = list(spectral_lines)
    if remove_lines is not None:
        for sl in remove_lines:
            slines.remove(sl)
    for sline in slines:
        n_calc = glass.rindex(sline)
        n_meas = glass.meas_rindex(sline)
        tc.assertAlmostEqual(n_calc, n_meas, delta=tol,
                             msg=f"spectral line '{sline:}' outside tol")
