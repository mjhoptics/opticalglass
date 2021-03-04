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
        nline = self.catalog.nline_str
        indxC = glass.glass_item(nline['C'])
        indxd = glass.glass_item(nline['d'])
        indxe = glass.glass_item(nline['e'])
        indxF = glass.glass_item(nline['F'])
        indxg = glass.glass_item(nline['g'])
        indxh = glass.glass_item(nline['h'])
        indxI = glass.glass_item(nline['i'])
        self.assertAlmostEqual(nC, indxC, delta=tol)
        self.assertAlmostEqual(nd, indxd, delta=tol)
        self.assertAlmostEqual(ne, indxe, delta=tol)
        self.assertAlmostEqual(nF, indxF, delta=tol)
        self.assertAlmostEqual(ng, indxg, delta=tol)
        self.assertAlmostEqual(nh, indxh, delta=tol)
        self.assertAlmostEqual(nI, indxI, delta=tol)

    def test_ohara_catalog_glass_index(self):
        sfpl51 = self.catalog.glass_index('S-FPL51')  # first in list
        self.assertEqual(sfpl51, 1)
        stim2 = self.catalog.glass_index('S-TIM 2')
        self.assertEqual(stim2, 42)
        sbsl7 = self.catalog.glass_index('S-BSL 7')
        self.assertEqual(sbsl7, 7)
        snph1 = self.catalog.glass_index('S-NPH 1')
        self.assertEqual(snph1, 127)
        snph53 = self.catalog.glass_index('S-NPH53')  # last in list
        self.assertEqual(snph53, 134)

    def test_ohara_catalog_data_index(self):
        nd = self.catalog.data_index('nd')
        self.assertEqual(nd, 17)
        vd = self.catalog.data_index('νd')
        self.assertEqual(vd, 25)
        B1 = self.catalog.data_index('B1')
        self.assertEqual(B1, 64)
        glasscode = self.catalog.data_index('Code(d)')
        self.assertEqual(glasscode, 3)
        date = self.catalog.data_index(' D0')
        self.assertEqual(date, 155)

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
