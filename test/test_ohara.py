#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for Ohara optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.ohara as o


class OharaTestCase(unittest.TestCase):
    catalog = o.OharaCatalog()

    def compare_indices(self, glass, tol=5e-6):
        nC = glass.rindex(656.27)
        nd = glass.rindex(587.56)
        ne = glass.rindex(546.07)
        nF = glass.rindex(486.13)
        ng = glass.rindex(435.84)
        nh = glass.rindex(404.66)
        nI = glass.rindex(365.01)
        indxC = glass.glass_data()[self.catalog.data_index('nC')]
        indxd = glass.glass_data()[self.catalog.data_index('nd')]
        indxe = glass.glass_data()[self.catalog.data_index('ne')]
        indxF = glass.glass_data()[self.catalog.data_index('nF')]
        indxg = glass.glass_data()[self.catalog.data_index('ng')]
        indxh = glass.glass_data()[self.catalog.data_index('nh')]
        indxI = glass.glass_data()[self.catalog.data_index('ni')]
        self.assertAlmostEqual(nC, indxC, delta=tol)
        self.assertAlmostEqual(nd, indxd, delta=tol)
        self.assertAlmostEqual(ne, indxe, delta=tol)
        self.assertAlmostEqual(nF, indxF, delta=tol)
        self.assertAlmostEqual(ng, indxg, delta=tol)
        self.assertAlmostEqual(nh, indxh, delta=tol)
        self.assertAlmostEqual(nI, indxI, delta=tol)

    def test_ohara_catalog_glass_index(self):
        sfpl51 = self.catalog.glass_index('S-FPL51')  # first in list
        self.assertEqual(sfpl51, 0)
        stim2 = self.catalog.glass_index('S-TIM 2')
        self.assertEqual(stim2, 41)
        sbsl7 = self.catalog.glass_index('S-BSL 7')
        self.assertEqual(sbsl7, 6)
        snph1 = self.catalog.glass_index('S-NPH 1')
        self.assertEqual(snph1, 126)
        snph53 = self.catalog.glass_index('S-NPH53')  # last in list
        self.assertEqual(snph53, 133)

    def test_ohara_catalog_data_index(self):
        nd = self.catalog.data_index('nd')
        self.assertEqual(nd, 16)
        vd = self.catalog.data_index('νd')
        self.assertEqual(vd, 24)
        B1 = self.catalog.data_index('B1')
        self.assertEqual(B1, 63)
        glasscode = self.catalog.data_index('Code(d)')
        self.assertEqual(glasscode, 2)
        date = self.catalog.data_index(' D0')
        self.assertEqual(date, 154)

    def test_ohara_glass_stim2(self):
        glass = o.OharaGlass('S-TIM 2')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-TIM 2')
        self.compare_indices(glass, tol=6e-6)

    def test_ohara_glass_sbsl7(self):
        glass = o.OharaGlass('S-BSL 7')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-BSL 7')
        self.compare_indices(glass, tol=6e-6)

    def test_ohara_glass_snbh53v(self):
        glass = o.OharaGlass('S-NBH53V')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-NBH53V')
        self.compare_indices(glass)


if __name__ == '__main__':
    unittest.main(verbosity=2)
