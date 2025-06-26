#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" unit test for og.glassfactory.create_glass()

.. codeauthor: Michael J. Hayford
"""

import unittest
from opticalglass.glassfactory import (
    create_glass, register_glass, save_custom_glasses, load_custom_glasses,
    get_glass_catalog
)
from opticalglass import glasserror as ge
from opticalglass import opticalmedium as om
from opticalglass import modelglass as mg
from opticalglass import glass as cat_glass

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

        # register a glass
        register_glass(om.InterpolatedMedium(
            'myglass', [(600, 1.5), (610, 1.6), (620, 1.61), (630, 1.62)], cat='mycatalog')
        )
        medium = create_glass('myglass', 'mycatalog')
        self.assertIsInstance(medium, om.OpticalMedium)

        # make sure get_glass_catalog returns the catalog
        cat = get_glass_catalog('mycatalog')
        found = False
        for g in cat.glass_list:
            if g[1] == 'myglass':
                found = True
                # mimic zmxread by accessing glass[0][0] and glass[0][1]
                gn_decode, gn, gc = g
                # just make sure gn_decode has 3 elements
                self.assertTrue(len(gn_decode) == 3) 
                    
        self.assertTrue(found)

    def test_save_load_custom_glass(self):
        """ test registering a glass """
        import opticalglass.glassfactory as gfact

        # register a glass
        register_glass(om.InterpolatedMedium(
            'myglass', [(600, 1.5), (610, 1.6), (620, 1.61), (630, 1.62)], cat='mycatalog')
        )
        # test modelglass as well
        register_glass(mg.ModelGlass(
            nd=1.61, vd=50, mat='anotherglass', cat='mycatalog')
        )
        # temporarily save the glass to a file
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as dirname:
            dirpath = Path(dirname)
            save_custom_glasses(dirpath)

            filename = dirpath / 'custom_glasses.json'
            # check that the glass is saved
            self.assertTrue(filename.exists())

            # Force to forget the registered glass
            gfact._custom_glass_registry = {}
            load_custom_glasses(dirpath)
            anotherglass = create_glass('anotherglass', 'mycatalog')
            self.assertIsInstance(anotherglass, om.OpticalMedium)
            myglass = create_glass('myglass', 'mycatalog')
            self.assertIsInstance(myglass, om.OpticalMedium)
            # make sure medium can give refractive index
            self.assertAlmostEqual(myglass.rindex(610), 1.6, places=2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
