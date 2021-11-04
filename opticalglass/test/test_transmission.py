#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for GlassCatalogSpreadsheet transmission_data function

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.glassfactory as gf


class TransmissionTestCase(unittest.TestCase):

    def compare_transmission(self, glass, wl1, t1, wl2, t2, tol=5e-4):
        t_series = glass.glass_data()['internal transmission mm, 10']
        self.assertAlmostEqual(t1, t_series[wl1], delta=tol)
        self.assertAlmostEqual(t2, t_series[wl2], delta=tol)

    def test_cdgm_glass_hlak50a(self):
        glass = gf.create_glass('H-LaK50A', 'CDGM')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-LaK50A')
        self.compare_transmission(glass, 2400.0, 0.668, 290.0, 0.028)

    def test_cdgm_glass_hlak51a(self):
        glass = gf.create_glass('H-LaK51A', 'CDGM')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'H-LaK51A')
        self.compare_transmission(glass, 2400.0, 0.633, 290.0, 0.218)

    def test_hikari_glass_jlak8(self):
        glass = gf.create_glass('J-LAK8', 'Hikari')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'J-LAK8')
        self.compare_transmission(glass, 280.0, 0.11, 2400.0, 0.63)

    def test_hikari_glass_jlasf010(self):
        glass = gf.create_glass('J-LASF010', 'Hikari')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'J-LASF010')
        self.compare_transmission(glass, 340.0, 0.03, 2400.0, 0.72)

    def test_hoya_glass_pcd51(self):
        glass = gf.create_glass('PCD51', 'Hoya')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'PCD51')
        self.compare_transmission(glass, 2500.0, 0.8, 280.0, 0.145)

    def test_hoya_glass_fd140(self):
        glass = gf.create_glass('FD140', 'Hoya')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'FD140')
        self.compare_transmission(glass, 1550.0, 0.995, 280.0, 0)

    def test_ohara_glass_slah51(self):
        glass = gf.create_glass('S-LAH51', 'Ohara')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-LAH51')
        self.compare_transmission(glass, 330.0, 0.01, 2400.0, 0.68)

    def test_ohara_glass_slah97(self):
        glass = gf.create_glass('S-LAH97', 'Ohara')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'S-LAH97')
        self.compare_transmission(glass, 280.0, 0.28, 2400.0, 0.61)

    def test_schott_glass_lf5(self):
        glass = gf.create_glass('LF5', 'Schott')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'LF5')
        self.compare_transmission(glass, 2325.0, 0.847, 310.0, 0.04)

    def test_schott_glass_nbk7(self):
        glass = gf.create_glass('N-BK7', 'Schott')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'N-BK7')
        self.compare_transmission(glass, 2500.0, 0.665, 290.0, 0.063)

    def test_schott_glass_nfk58(self):
        glass = gf.create_glass('N-FK58', 'Schott')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'N-FK58')
        self.compare_transmission(glass, 2500.0, 0.997, 250.0, 0.09)

    def test_sumita_glass_ksk16(self):
        glass = gf.create_glass('K-SK16', 'Sumita')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'K-SK16')
        self.compare_transmission(glass, 300.0, 0.014, 2000.0, 0.937)

    def test_sumita_glass_kbk7(self):
        glass = gf.create_glass('K-BK7', 'Sumita')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'K-BK7')
        self.compare_transmission(glass, 270.0, 0.02, 2000.0, 0.959)


if __name__ == '__main__':
    unittest.main(verbosity=2)
