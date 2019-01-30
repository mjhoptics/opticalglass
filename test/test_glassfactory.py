#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for GlassFactory create_glass function

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.glassfactory as gf


class GlassFactoryTestCase(unittest.TestCase):

    def compare_indices(self, glass, tol=5e-6):
        nC = glass.rindex(656.27)
        nd = glass.rindex(587.56)
        ne = glass.rindex(546.07)
        nF = glass.rindex(486.13)
        ng = glass.rindex(435.84)
        nh = glass.rindex(404.66)
        nI = glass.rindex(365.01)
        indxC = glass.glass_item(glass.catalog.nline_str['nC'])
        indxd = glass.glass_item(glass.catalog.nline_str['nd'])
        indxe = glass.glass_item(glass.catalog.nline_str['ne'])
        indxF = glass.glass_item(glass.catalog.nline_str['nF'])
        indxg = glass.glass_item(glass.catalog.nline_str['ng'])
        indxh = glass.glass_item(glass.catalog.nline_str['nh'])
        indxI = glass.glass_item(glass.catalog.nline_str['ni'])
        self.assertAlmostEqual(nC, indxC, delta=tol)
        self.assertAlmostEqual(nd, indxd, delta=tol)
        self.assertAlmostEqual(ne, indxe, delta=tol)
        self.assertAlmostEqual(nF, indxF, delta=tol)
        self.assertAlmostEqual(ng, indxg, delta=tol)
        self.assertAlmostEqual(nh, indxh, delta=tol)
        self.assertAlmostEqual(nI, indxI, delta=tol)

    def test_cdgm_glass_hfk61(self):
        glass = gf.create_glass('H-FK61', 'CDGM')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-FK61')
        self.compare_indices(glass, tol=6e-6)

    def test_cdgm_glass_f4(self):
        glass = gf.create_glass('F4', 'CDGM')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'F4')
        self.compare_indices(glass, tol=1e-5)

    def test_cdgm_glass_hk9l(self):
        glass = gf.create_glass('H-K9L', 'CDGM')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-K9L')
        self.compare_indices(glass)

    def test_hoya_glass_fcd1(self):
        fcd1 = gf.create_glass('FCD1', 'Hoya')
        self.assertIsNotNone(fcd1.gindex)
        self.assertEqual(fcd1.name(), 'FCD1')
        self.compare_indices(fcd1)

    def test_hoya_glass_ef2(self):
        ef2 = gf.create_glass('E-F2', 'Hoya')
        self.assertIsNotNone(ef2.gindex)
        self.assertEqual(ef2.name(), 'E-F2')
        self.compare_indices(ef2)

    def test_hoya_glass_bsc7(self):
        bsc7 = gf.create_glass('BSC7', 'Hoya')
        self.assertIsNotNone(bsc7.gindex)
        self.assertEqual(bsc7.name(), 'BSC7')
        self.compare_indices(bsc7)

    def test_ohara_glass_stim2(self):
        stim2 = gf.create_glass('S-TIM 2', 'Ohara')
        self.assertIsNotNone(stim2.gindex)
        self.assertEqual(stim2.name(), 'S-TIM 2')
        self.compare_indices(stim2, tol=6e-6)

    def test_ohara_glass_sbsl7(self):
        sbsl7 = gf.create_glass('S-BSL 7', 'Ohara')
        self.assertIsNotNone(sbsl7.gindex)
        self.assertEqual(sbsl7.name(), 'S-BSL 7')
        self.compare_indices(sbsl7, tol=6e-6)

    def test_ohara_glass_snbh53v(self):
        glass = gf.create_glass('S-NBH53V', 'Ohara')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-NBH53V')
        self.compare_indices(glass)

    def test_schott_glass_f2(self):
        f2 = gf.create_glass('F2', 'Schott')
        self.assertIsNotNone(f2.gindex)
        self.assertEqual(f2.name(), 'F2')
        self.compare_indices(f2)

    def test_schott_glass_nbk7(self):
        nbk7 = gf.create_glass('N-BK7', 'Schott')
        self.assertIsNotNone(nbk7.gindex)
        self.assertEqual(nbk7.name(), 'N-BK7')
        self.compare_indices(nbk7)

    def test_schott_glass_sf6ht(self):
        sf6ht = gf.create_glass('SF6HT', 'Schott')
        self.assertIsNotNone(sf6ht.gindex)
        self.assertEqual(sf6ht.name(), 'SF6HT')
        self.compare_indices(sf6ht)


if __name__ == '__main__':
    unittest.main(verbosity=2)
