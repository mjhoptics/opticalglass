#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for og.glassfactory.create_glass()

.. codeauthor: Michael J. Hayford
"""

import unittest
from opticalglass.glassfactory import create_glass
from opticalglass import glasserror as ge
from opticalglass import opticalmedium


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

        nbk7 = create_glass('N-BK7','Schott ')
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass(' N-BK7',' Schott')
        self.assertIsNotNone(nbk7)

    def test_create_glass_cat_list(self):
        """ test 2 arg form vs whitespace """
        nbk7 = create_glass('N-BK7',['Schott', 'Hoya', 'Ohara'])
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass('N-BK7',[' Schott', ' Hoya', ' Ohara'])
        self.assertIsNotNone(nbk7)

        nbk7 = create_glass(' N-BK7',['Schott ', 'Hoya ', 'Ohara '])
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

    def test_register_glass(self):
        """ test registering a glass """
        from opticalglass.glassfactory import register_glass
        from opticalglass import glasserror as ge

        # register a glass
        register_glass(opticalmedium.InterpolatedMedium(
            'myglass', [(600, 1.5), (610, 1.6), (620, 1.61), (630, 1.62)], cat='mycatalog')
        )
        medium = create_glass('myglass', 'mycatalog')
        self.assertIsInstance(medium, opticalmedium.OpticalMedium)


if __name__ == '__main__':
    unittest.main(verbosity=2)
