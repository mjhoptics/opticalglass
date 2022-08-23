#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
""" unit test for Hikari glass catalog

.. Created on Wed Aug 26 15:12:40 2020

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.hikari as hi

from opticalglass.test.util import compare_indices


class HikariTestCase(unittest.TestCase):
    catalog = hi.HikariCatalog()

    def test_hikari_catalog_glass_index(self):
        fk5 = self.catalog.glass_index('J-FK5')  # first in list
        self.assertIsNotNone(fk5)
        bk7a = self.catalog.glass_index('J-BK7A')
        self.assertIsNotNone(bk7a)
        sk16 = self.catalog.glass_index('J-SK16')
        self.assertIsNotNone(sk16)
        lasf02 = self.catalog.glass_index('J-LASF02')
        self.assertIsNotNone(lasf02)
        lasfh24hs = self.catalog.glass_index('J-LASFH24HS')  # last in list
        self.assertIsNotNone(lasfh24hs)

    # def test_hikari_catalog_data_index(self):
    #     nd = self.catalog.data_index(self.catalog.nline_str['d'])
    #     self.assertEqual(nd, 17)
    #     vd = self.catalog.data_index('νd')
    #     self.assertEqual(vd, 25)
    #     A5 = self.catalog.data_index('A5/λ^6')
    #     self.assertEqual(A5, 61)
    #     glasscode = self.catalog.data_index('コードCode(d)')
    #     self.assertEqual(glasscode, 2)
    #     date = self.catalog.data_index('550nm')
    #     self.assertEqual(date, 121)

    def test_hikari_glass_bk7(self):
        glass = hi.HikariGlass('J-BK7A')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'J-BK7A')
        compare_indices(self, glass, HikariTestCase.catalog, tol=4e-6)

    def test_hikari_glass_sk16(self):
        glass = hi.HikariGlass('J-SK16')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'J-SK16')
        compare_indices(self, glass, HikariTestCase.catalog, tol=4.5e-6)

    def test_hikari_glass_lasf02(self):
        glass = hi.HikariGlass('J-LASF02')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'J-LASF02')
        compare_indices(self, glass, HikariTestCase.catalog, tol=2.25e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)



