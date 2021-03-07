#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for Hoya optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.hoya as h

from opticalglass.test.util import compare_indices


class HoyaTestCase(unittest.TestCase):
    catalog = h.HoyaCatalog()

    def test_hoya_catalog_glass_index(self):
        fc5 = self.catalog.glass_index('FC5')  # first in list
        self.assertEqual(fc5, 1)
        fcd1 = self.catalog.glass_index('FCD1')
        self.assertEqual(fcd1, 2)
        ef2 = self.catalog.glass_index('E-F2')
        self.assertEqual(ef2, 29)
        bsc7 = self.catalog.glass_index('BSC7')
        self.assertEqual(bsc7, 12)
        mctaf1 = self.catalog.glass_index('MC-TAF1')  # last in list
        self.assertEqual(mctaf1, 194)

    def test_hoya_catalog_data_index(self):
        nd = self.catalog.data_index('nd')
        self.assertEqual(nd, 5)
        vd = self.catalog.data_index('νd')
        self.assertEqual(vd, 6)
        A0 = self.catalog.data_index('A0')
        self.assertEqual(A0, 29)
        n1529 = self.catalog.data_index('n1529.6')
        self.assertEqual(n1529, 11)

    def test_hoya_glass_fcd1(self):
        fcd1 = h.HoyaGlass('FCD1')
        self.assertIsNotNone(fcd1.gindex)
        self.assertEqual(fcd1.name(), 'FCD1')
        compare_indices(self, fcd1, HoyaTestCase.catalog)

    def test_hoya_glass_ef2(self):
        ef2 = h.HoyaGlass('E-F2')
        self.assertIsNotNone(ef2.gindex)
        self.assertEqual(ef2.name(), 'E-F2')
        compare_indices(self, ef2, HoyaTestCase.catalog)

    def test_hoya_glass_bsc7(self):
        bsc7 = h.HoyaGlass('BSC7')
        self.assertIsNotNone(bsc7.gindex)
        self.assertEqual(bsc7.name(), 'BSC7')
        compare_indices(self, bsc7, HoyaTestCase.catalog)


if __name__ == '__main__':
    unittest.main(verbosity=2)
