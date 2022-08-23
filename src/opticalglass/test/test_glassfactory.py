#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for GlassFactory create_glass function

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.glassfactory as gf
from opticalglass.test.util import compare_indices


class GlassFactoryTestCase(unittest.TestCase):

    def test_cdgm_glass_hfk61(self):
        glass = gf.create_glass('H-FK61', 'CDGM')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-FK61')
        compare_indices(self, glass, glass.catalog, tol=6e-6)

    def test_cdgm_glass_f4(self):
        glass = gf.create_glass('F4', 'CDGM')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'F4')
        compare_indices(self, glass, glass.catalog, tol=1.05e-5)

    def test_cdgm_glass_hk9l(self):
        glass = gf.create_glass('H-K9L', 'CDGM')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-K9L')
        compare_indices(self, glass, glass.catalog, tol=8e-6)

    def test_hoya_glass_fcd1(self):
        fcd1 = gf.create_glass('FCD1', 'Hoya')
        self.assertIsNotNone(fcd1)
        self.assertEqual(fcd1.name(), 'FCD1')
        compare_indices(self, fcd1, fcd1.catalog)

    def test_hoya_glass_ef2(self):
        ef2 = gf.create_glass('E-F2', 'Hoya')
        self.assertIsNotNone(ef2)
        self.assertEqual(ef2.name(), 'E-F2')
        compare_indices(self, ef2, ef2.catalog)

    def test_hoya_glass_bsc7(self):
        bsc7 = gf.create_glass('BSC7', 'Hoya')
        self.assertIsNotNone(bsc7)
        self.assertEqual(bsc7.name(), 'BSC7')
        compare_indices(self, bsc7, bsc7.catalog)

    def test_ohara_glass_stim2(self):
        stim2 = gf.create_glass('S-TIM 2', 'Ohara')
        self.assertIsNotNone(stim2)
        self.assertEqual(stim2.name(), 'S-TIM 2')
        compare_indices(self, stim2, stim2.catalog, tol=6e-6)

    def test_ohara_glass_sbsl7(self):
        sbsl7 = gf.create_glass('S-BSL 7', 'Ohara')
        self.assertIsNotNone(sbsl7)
        self.assertEqual(sbsl7.name(), 'S-BSL 7')
        compare_indices(self, sbsl7, sbsl7.catalog, tol=6e-6)

    def test_ohara_glass_snbh53v(self):
        glass = gf.create_glass('S-NBH53V', 'Ohara')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-NBH53V')
        compare_indices(self, glass, glass.catalog)

    def test_schott_glass_f2(self):
        f2 = gf.create_glass('F2', 'Schott')
        self.assertIsNotNone(f2)
        self.assertEqual(f2.name(), 'F2')
        compare_indices(self, f2, f2.catalog)

    def test_schott_glass_nbk7(self):
        nbk7 = gf.create_glass('N-BK7', 'Schott')
        self.assertIsNotNone(nbk7)
        self.assertEqual(nbk7.name(), 'N-BK7')
        compare_indices(self, nbk7, nbk7.catalog)

    def test_schott_glass_sf6ht(self):
        sf6ht = gf.create_glass('SF6HT', 'Schott')
        self.assertIsNotNone(sf6ht)
        self.assertEqual(sf6ht.name(), 'SF6HT')
        compare_indices(self, sf6ht, sf6ht.catalog)


if __name__ == '__main__':
    unittest.main(verbosity=2)
