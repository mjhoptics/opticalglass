#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for CDGM optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.cdgm as c

from opticalglass.test.util import compare_indices


class CDGMTestCase(unittest.TestCase):
    catalog = c.CDGMCatalog()

    def test_cdgm_catalog_glass_index(self):
        g1 = self.catalog.glass_index('H-FK55')  # first in list
        self.assertIsNotNone(g1)
        g2 = self.catalog.glass_index('H-QK3L')
        self.assertIsNotNone(g2)
        g3 = self.catalog.glass_index('H-K5')  # schott
        self.assertIsNotNone(g3)
        g4 = self.catalog.glass_index('H-F4')  # sellmeier
        self.assertIsNotNone(g4)
        g4a = self.catalog.glass_index('F4')   # schott
        self.assertIsNotNone(g4a)
        g5 = self.catalog.glass_index('H-K9L')
        self.assertIsNotNone(g5)
        g6 = self.catalog.glass_index('D-LaF50')
        self.assertIsNotNone(g6)
        g7 = self.catalog.glass_index('D-ZLaF85LS-25')  # last in list
        self.assertIsNotNone(g7)

    # def test_cdgm_catalog_data_index(self):
    #     nd = self.catalog.data_index('nd')
    #     self.assertEqual(nd, 9)
    #     vd = self.catalog.data_index('υd')
    #     self.assertEqual(vd, 17)
    #     A0 = self.catalog.data_index('A0')
    #     self.assertEqual(A0, 21)
    #     nt = self.catalog.data_index('nt')
    #     self.assertEqual(nt, 2)

    def test_cdgm_glass_hfk61(self):
        glass = c.CDGMGlass('H-FK55')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-FK55')
        compare_indices(self, glass, CDGMTestCase.catalog, tol=6e-6)

    def test_cdgm_glass_hf4(self):
        # uses sellmeier interpolation function
        glass = c.CDGMGlass('H-F4')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-F4')
        compare_indices(self, glass, CDGMTestCase.catalog, tol=1.1e-5)

    def test_cdgm_glass_f4(self):
        # uses schott interpolation function
        glass = c.CDGMGlass('F4')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'F4')
        compare_indices(self, glass, CDGMTestCase.catalog, tol=1.1e-5)

    def test_cdgm_glass_hk9l(self):
        glass = c.CDGMGlass('H-K9L')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-K9L')
        compare_indices(self, glass, CDGMTestCase.catalog, tol=8e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
