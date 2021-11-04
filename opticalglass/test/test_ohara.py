#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for Ohara optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.ohara as o

from opticalglass.test.util import compare_indices


class OharaTestCase(unittest.TestCase):
    catalog = o.OharaCatalog()

    def test_ohara_catalog_glass_index(self):
        sfpl51 = self.catalog.glass_index('S-FPL51')  # first in list
        self.assertIsNotNone(sfpl51)
        stim2 = self.catalog.glass_index('S-TIM 2')
        self.assertIsNotNone(stim2)
        sbsl7 = self.catalog.glass_index('S-BSL 7')
        self.assertIsNotNone(sbsl7)
        snph1 = self.catalog.glass_index('S-NPH 1')
        self.assertIsNotNone(snph1)
        snph53 = self.catalog.glass_index('S-NPH53')  # last in list
        self.assertIsNotNone(snph53)

    # def test_ohara_catalog_data_index(self):
    #     nd = self.catalog.data_index('nd')
    #     self.assertEqual(nd, 17)
    #     vd = self.catalog.data_index('νd')
    #     self.assertEqual(vd, 25)
    #     B1 = self.catalog.data_index('B1')
    #     self.assertEqual(B1, 64)
    #     glasscode = self.catalog.data_index('Code(d)')
    #     self.assertEqual(glasscode, 3)
    #     date = self.catalog.data_index(' D0')
    #     self.assertEqual(date, 155)

    def test_ohara_glass_stim2(self):
        glass = o.OharaGlass('S-TIM 2')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-TIM 2')
        compare_indices(self, glass, OharaTestCase.catalog, tol=6e-6)

    def test_ohara_glass_sbsl7(self):
        glass = o.OharaGlass('S-BSL 7')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-BSL 7')
        compare_indices(self, glass, OharaTestCase.catalog, tol=6e-6)

    def test_ohara_glass_snbh53v(self):
        glass = o.OharaGlass('S-NBH53V')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-NBH53V')
        compare_indices(self, glass, OharaTestCase.catalog, tol=5e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
