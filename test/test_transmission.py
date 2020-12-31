#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for GlassCatalogSpreadsheet transmission_data function

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.glassfactory as gf


class TransmissionTestCase(unittest.TestCase):

    def compare_transmission(self, glass, wl1, t1, wl2, t2, num_t, tol=5e-4):
        t_data = glass.transmission_data()
        self.assertEqual(wl1, t_data[0][0])
        self.assertAlmostEqual(t1, t_data[0][1], delta=tol)
        self.assertEqual(wl2, t_data[-1][0])
        self.assertAlmostEqual(t2, t_data[-1][1], delta=tol)
        self.assertEqual(num_t, len(t_data))

    def test_cdgm_glass_hlak50a(self):
        glass = gf.create_glass('H-LaK50A', 'CDGM')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-LaK50A')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2400.0, 0.668, 290.0, 0.028, 34)

    def test_cdgm_glass_hlak51a(self):
        glass = gf.create_glass('H-LaK51A', 'CDGM')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'H-LaK51A')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2400.0, 0.633, 290.0, 0.218, 34)

    def test_hikari_glass_jlak8(self):
        glass = gf.create_glass('J-LAK8', 'Hikari')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'J-LAK8')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 280.0, 0.01, 2400.0, 0.63, 33)

    def test_hikari_glass_jlasf010(self):
        glass = gf.create_glass('J-LASF010', 'Hikari')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'J-LASF010')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 350.0, 0.14, 2400.0, 0.72, 26)

    def test_hoya_glass_pcd51(self):
        glass = gf.create_glass('PCD51', 'Hoya')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'PCD51')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2500.0, 0.8, 280.0, 0.145, 44)

    def test_hoya_glass_fd140(self):
        glass = gf.create_glass('FD140', 'Hoya')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'FD140')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 1550.0, 0.995, 280.0, 0, 38)

    def test_ohara_glass_slah51(self):
        glass = gf.create_glass('S-LAH51', 'Ohara')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-LAH51')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 330.0, 0.01, 2400.0, 0.68, 27)

    def test_ohara_glass_slah97(self):
        glass = gf.create_glass('S-LAH97', 'Ohara')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'S-LAH97')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 280.0, 0.28, 2400.0, 0.61, 32)

    def test_schott_glass_lf5(self):
        glass = gf.create_glass('LF5', 'Schott')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'LF5')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2325.0, 0.847, 310.0, 0.04, 23)

    def test_schott_glass_nbk7(self):
        glass = gf.create_glass('N-BK7', 'Schott')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'N-BK7')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2500.0, 0.665, 290.0, 0.063, 26)

    def test_schott_glass_nfk58(self):
        glass = gf.create_glass('N-FK58', 'Schott')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'N-FK58')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 2500.0, 0.997, 250.0, 0.09, 30)

    def test_sumita_glass_ksk16(self):
        glass = gf.create_glass('K-SK16', 'Sumita')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'K-SK16')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 300.0, 0.014, 2000.0, 0.937, 24)

    def test_sumita_glass_kbk7(self):
        glass = gf.create_glass('K-BK7', 'Sumita')
        self.assertIsNotNone(glass.gindex)
        self.assertEqual(glass.name(), 'K-BK7')
        # t_data = glass.transmission_data()
        # print(glass.gname, glass.gindex, t_data[0][0], t_data[0][1],
        #       t_data[-1][0], t_data[-1][1], len(t_data))
        self.compare_transmission(glass, 270.0, 0.02, 2000.0, 0.959, 27)


if __name__ == '__main__':
    unittest.main(verbosity=2)
