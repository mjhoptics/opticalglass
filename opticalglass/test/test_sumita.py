#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
""" unit test for Sumita optical glass catalog

.. Created on Wed Aug 26 14:46:13 2020

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.sumita as su

from opticalglass.test.util import compare_indices


class SumitaTestCase(unittest.TestCase):
    catalog = su.SumitaCatalog()
    # Sumita doesn't tabulate the 's' spectral line
    remove_lines = ['s']

    def test_ohara_catalog_glass_index(self):
        cafk95 = self.catalog.glass_index('K-CaFK95')  # first in list
        self.assertIsNotNone(cafk95)
        pbk40 = self.catalog.glass_index('K-PBK40')
        self.assertIsNotNone(pbk40)
        sk16 = self.catalog.glass_index('K-SK16')
        self.assertIsNotNone(sk16)
        laskn1 = self.catalog.glass_index('K-LaSKn1')
        self.assertIsNotNone(laskn1)
        fir100uv = self.catalog.glass_index('K-FIR100UV')  # last in list
        self.assertIsNotNone(fir100uv)

    # def test_sumita_catalog_data_index(self):
    #     nd = self.catalog.data_index('nd')
    #     self.assertEqual(nd, 16)
    #     vd = self.catalog.data_index('vd')
    #     self.assertEqual(vd, 4)
    #     B1 = self.catalog.data_index('A4')
    #     self.assertEqual(B1, 52)
    #     glasscode = self.catalog.data_index('GTYPE')
    #     self.assertEqual(glasscode, 2)
    #     date = self.catalog.data_index('T1_550')
    #     self.assertEqual(date, 97)

    def test_sumita_glass_pbk40(self):
        glass = su.SumitaGlass('K-PBK40')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'K-PBK40')
        compare_indices(self, glass, SumitaTestCase.catalog, tol=1.1e-5,
                        remove_lines=SumitaTestCase.remove_lines)

    def test_sumita_glass_sk16(self):
        glass = su.SumitaGlass('K-SK16')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'K-SK16')
        compare_indices(self, glass, SumitaTestCase.catalog, tol=4.5e-6,
                        remove_lines=SumitaTestCase.remove_lines)

    def test_sumita_glass_laskn1(self):
        glass = su.SumitaGlass('K-LaSKn1')
        self.assertIsNotNone(glass)
        self.assertEqual(glass.name(), 'K-LaSKn1')
        compare_indices(self, glass, SumitaTestCase.catalog, tol=7.5e-6,
                        remove_lines=SumitaTestCase.remove_lines)


if __name__ == '__main__':
    unittest.main(verbosity=2)
