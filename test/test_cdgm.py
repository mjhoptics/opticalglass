#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for CDGM optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.cdgm as c


class CDGMTestCase(unittest.TestCase):
    catalog = c.CDGMCatalog()

    def compare_indices(self, glass, tol=5e-6):
        nC = glass.rindex(656.27)
        nd = glass.rindex(587.56)
        ne = glass.rindex(546.07)
        nF = glass.rindex(486.13)
        ng = glass.rindex(435.84)
        nh = glass.rindex(404.66)
        nI = glass.rindex(365.01)
        indxC = glass.glass_data()[self.catalog.data_index('nc')]
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

    def test_cdgm_catalog_glass_index(self):
        g1 = self.catalog.glass_index('H-FK61')  # first in list
        self.assertEqual(g1, 0)
        g2 = self.catalog.glass_index('H-QK3L')
        self.assertEqual(g2, 4)
        g3 = self.catalog.glass_index('F4')
        self.assertEqual(g3, 97)
        g4 = self.catalog.glass_index('H-K9L')
        self.assertEqual(g4, 13)
        g5 = self.catalog.glass_index('D-LaF50')
        self.assertEqual(g5, 229)
        g6 = self.catalog.glass_index('D-ZLaF85L')  # last in list
        self.assertEqual(g6, 239)

    def test_cdgm_catalog_data_index(self):
        nd = self.catalog.data_index('nd')
        self.assertEqual(nd, 9)
        vd = self.catalog.data_index('υd')
        self.assertEqual(vd, 17)
        A0 = self.catalog.data_index('A0')
        self.assertEqual(A0, 21)
        nt = self.catalog.data_index('nt')
        self.assertEqual(nt, 2)

    def test_cdgm_glass_hfk61(self):
        glass = c.CDGMGlass('H-FK61')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-FK61')
        self.compare_indices(glass, tol=6e-6)

    def test_cdgm_glass_f4(self):
        glass = c.CDGMGlass('F4')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'F4')
        self.compare_indices(glass, tol=1e-5)

    def test_cdgm_glass_hk9l(self):
        glass = c.CDGMGlass('H-K9L')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-K9L')
        self.compare_indices(glass)


if __name__ == '__main__':
    unittest.main(verbosity=2)
