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
        pandas_offset = 1
        fc5 = self.catalog.glass_index('FC5') + pandas_offset  # first in list
        self.assertIsNotNone(fc5)
        fcd1 = self.catalog.glass_index('FCD1') + pandas_offset
        self.assertIsNotNone(fcd1)
        ef2 = self.catalog.glass_index('E-F2') + pandas_offset
        self.assertIsNotNone(ef2)
        bsc7 = self.catalog.glass_index('BSC7') + pandas_offset
        self.assertIsNotNone(bsc7)
        mctaf1 = self.catalog.glass_index('MC-TAF1') + pandas_offset  # last in list
        self.assertIsNotNone(mctaf1)

    # def test_hoya_catalog_data_index(self):
    #     pandas_offset = 3
    #     nd = self.catalog.data_index('nd') + pandas_offset
    #     self.assertEqual(nd, 5)
    #     vd = self.catalog.data_index('νd') + pandas_offset
    #     self.assertEqual(vd, 6)
    #     A0 = self.catalog.data_index('A0') + pandas_offset
    #     self.assertEqual(A0, 29)
    #     n1529 = self.catalog.data_index('n1529.6') + pandas_offset
    #     self.assertEqual(n1529, 11)

    def test_hoya_glass_fcd1(self):
        fcd1 = h.HoyaGlass('FCD1')
        self.assertIsNotNone(fcd1)
        self.assertEqual(fcd1.name(), 'FCD1')
        compare_indices(self, fcd1, HoyaTestCase.catalog)

    def test_hoya_glass_ef2(self):
        ef2 = h.HoyaGlass('E-F2')
        self.assertIsNotNone(ef2)
        self.assertEqual(ef2.name(), 'E-F2')
        compare_indices(self, ef2, HoyaTestCase.catalog)

    def test_hoya_glass_bsc7(self):
        bsc7 = h.HoyaGlass('BSC7')
        self.assertIsNotNone(bsc7)
        self.assertEqual(bsc7.name(), 'BSC7')
        compare_indices(self, bsc7, HoyaTestCase.catalog)


if __name__ == '__main__':
    unittest.main(verbosity=2)
