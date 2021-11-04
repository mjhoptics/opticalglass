#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for Schott optical glass catalog

.. codeauthor: Michael J. Hayford
"""

import unittest
import opticalglass.schott as s

from opticalglass.test.util import compare_indices


class SchottTestCase(unittest.TestCase):
    catalog = s.SchottCatalog()

    def test_schott_catalog_glass_index(self):
        f2 = self.catalog.glass_index('F2')
        self.assertIsNotNone(f2)
        nbk7 = self.catalog.glass_index('N-BK7')
        self.assertIsNotNone(nbk7)
        sf6ht = self.catalog.glass_index('SF6HT')
        self.assertIsNotNone(sf6ht)

    # def test_schott_catalog_data_index(self):
    #     nd = self.catalog.data_index('nd')
    #     self.assertEqual(nd, 1)
    #     vd = self.catalog.data_index('vd')
    #     self.assertEqual(vd, 3)
    #     B1 = self.catalog.data_index('B1')
    #     self.assertEqual(B1, 6)
    #     glasscode = self.catalog.data_index('Glascode')
    #     self.assertEqual(glasscode, 158)
    #     date = self.catalog.data_index('Date')
    #     self.assertEqual(date, 160)

    def test_schott_glass_f2(self):
        f2 = s.SchottGlass('F2')
        self.assertIsNotNone(f2)
        self.assertEqual(f2.name(), 'F2')
        compare_indices(self, f2, SchottTestCase.catalog, tol=5e-6)

    def test_schott_glass_nbk7(self):
        nbk7 = s.SchottGlass('N-BK7')
        self.assertIsNotNone(nbk7)
        self.assertEqual(nbk7.name(), 'N-BK7')
        compare_indices(self, nbk7, SchottTestCase.catalog, tol=5e-6)

    def test_schott_glass_sf6ht(self):
        sf6ht = s.SchottGlass('SF6HT')
        self.assertIsNotNone(sf6ht)
        self.assertEqual(sf6ht.name(), 'SF6HT')
        compare_indices(self, sf6ht, SchottTestCase.catalog, tol=5e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
