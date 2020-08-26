#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
""" unit test for Hikari glass catalog

.. Created on Wed Aug 26 15:12:40 2020

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.hikari as hi


class HikariTestCase(unittest.TestCase):
    catalog = hi.HikariCatalog()

    def compare_indices(self, glass, tol=5e-6):
        nC = glass.rindex(656.27)
        nd = glass.rindex(587.56)
        ne = glass.rindex(546.07)
        nF = glass.rindex(486.13)
        ng = glass.rindex(435.84)
        nh = glass.rindex(404.66)
        nI = glass.rindex(365.01)
        nline = self.catalog.nline_str
        indxC = glass.glass_data()[self.catalog.data_index(nline['nC'])]
        indxd = glass.glass_data()[self.catalog.data_index(nline['nd'])]
        indxe = glass.glass_data()[self.catalog.data_index(nline['ne'])]
        indxF = glass.glass_data()[self.catalog.data_index(nline['nF'])]
        indxg = glass.glass_data()[self.catalog.data_index(nline['ng'])]
        indxh = glass.glass_data()[self.catalog.data_index(nline['nh'])]
        indxI = glass.glass_data()[self.catalog.data_index(nline['ni'])]
        self.assertAlmostEqual(nC, indxC, delta=tol)
        self.assertAlmostEqual(nd, indxd, delta=tol)
        self.assertAlmostEqual(ne, indxe, delta=tol)
        self.assertAlmostEqual(nF, indxF, delta=tol)
        self.assertAlmostEqual(ng, indxg, delta=tol)
        self.assertAlmostEqual(nh, indxh, delta=tol)
        self.assertAlmostEqual(nI, indxI, delta=tol)

    def test_hikari_catalog_glass_index(self):
        fk5 = self.catalog.glass_index('J-FK5')  # first in list
        self.assertEqual(fk5, 0)
        bk7a = self.catalog.glass_index('J-BK7A')
        self.assertEqual(bk7a, 9)
        sk16 = self.catalog.glass_index('J-SK16')
        self.assertEqual(sk16, 39)
        lasf02 = self.catalog.glass_index('J-LASF02')
        self.assertEqual(lasf02, 104)
        lasfh24hs = self.catalog.glass_index('J-LASFH24HS')  # last in list
        self.assertEqual(lasfh24hs, 131)

    def test_hikari_catalog_data_index(self):
        nd = self.catalog.data_index(self.catalog.nline_str['nd'])
        self.assertEqual(nd, 16)
        vd = self.catalog.data_index('νd')
        self.assertEqual(vd, 24)
        A5 = self.catalog.data_index('A5/λ^6')
        self.assertEqual(A5, 60)
        glasscode = self.catalog.data_index('Code(d)')
        self.assertEqual(glasscode, 1)
        date = self.catalog.data_index('550nm')
        self.assertEqual(date, 115)

    def test_hikari_glass_bk7(self):
        glass = hi.HikariGlass('J-BK7A')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'J-BK7A')
        self.compare_indices(glass, tol=1e-6)

    def test_hikari_glass_sk16(self):
        glass = hi.HikariGlass('J-SK16')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'J-SK16')
        self.compare_indices(glass, tol=1.05e-6)

    def test_hikari_glass_lasf02(self):
        glass = hi.HikariGlass('J-LASF02')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'J-LASF02')
        self.compare_indices(glass, tol=2.25e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)



