#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for og.glassfactory.create_glass()

.. codeauthor: Michael J. Hayford
"""

import unittest
from opticalglass.glassfactory import create_glass, register_glass, save_custom_glasses, load_custom_glasses
from opticalglass import glasserror as ge
import opticalglass.opticalmedium as om
from opticalglass import modelglass

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

        # register a glass
        register_glass(om.InterpolatedMedium(
            'myglass', [(600, 1.5), (610, 1.6), (620, 1.61), (630, 1.62)], cat='mycatalog')
        )
        medium = create_glass('myglass', 'mycatalog')
        self.assertIsInstance(medium, om.OpticalMedium)

    def test_save_load_custom_glass(self):
        """ test registering a glass """
        import opticalglass.glassfactory

        # register a glass
        register_glass(om.InterpolatedMedium(
            'myglass', [(600, 1.5), (610, 1.6), (620, 1.61), (630, 1.62)], cat='mycatalog')
        )
        # test modelglass as well
        register_glass(modelglass.ModelGlass(
            nd=1.61, vd=50, mat='anotherglass', cat='mycatalog')
        )
        # temporarily save the glass to a file
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as dirname:
            save_custom_glasses(dirname)

            # check that the glass is saved
            self.assertTrue(os.path.exists(os.path.join(dirname, 'mycatalog/myglass.json')))

            # Force to forget the registered glass
            opticalglass.glassfactory._custom_glass_registry = {}
            load_custom_glasses(dirname)
            medium = create_glass('myglass', 'mycatalog')
            self.assertIsInstance(medium, om.OpticalMedium)
            medium = create_glass('anotherglass', 'mycatalog')
            self.assertIsInstance(medium, om.OpticalMedium)


if __name__ == '__main__':
    unittest.main(verbosity=2)
