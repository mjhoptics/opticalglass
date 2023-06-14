#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for og.glassfactory.create_glass()

.. codeauthor: Michael J. Hayford
"""

import unittest
from opticalglass.glassfactory import create_glass
from opticalglass import glasserror as ge


class CreateGlassTestCase(unittest.TestCase):

    def test_create_glass_1_arg(self):
        """ test 1 arg form vs case and whitespace """
        nbk7 = create_glass('N-BK7,Schott')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass('N-BK7,schott')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass('N-BK7,SCHOTT')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass('N-BK7, Schott')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass(' N-BK7, Schott')
        self.assertIsNotNone(nbk7)

    def test_create_glass_2_arg(self):
        """ test 2 arg form vs whitespace """
        nbk7 = create_glass('N-BK7','Schott')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass('N-BK7','Schott')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass(' N-BK7',' Schott')
        self.assertIsNotNone(nbk7)

    def test_create_glass_exceptions(self):
        """ test exceptions for glass and catalog not found """
        self.assertRaises(ge.GlassNotFoundError, 
                          create_glass, 'NBK7, Schott')
        self.assertRaises(ge.GlassNotFoundError, 
                          create_glass, 'NBK7', 'Schott')

        self.assertRaises(ge.GlassCatalogNotFoundError, 
                          create_glass, 'N-BK7, xSchott')
        self.assertRaises(ge.GlassCatalogNotFoundError, 
                          create_glass, 'N-BK7','xSchott')


if __name__ == '__main__':
    unittest.main(verbosity=2)
