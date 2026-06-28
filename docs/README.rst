
.. image:: https://app.readthedocs.org/projects/opticalglass/badge/?version=latest
    :alt: ReadTheDocs
    :target: https://opticalglass.readthedocs.io/en/stable/
.. image:: https://img.shields.io/pypi/v/opticalglass.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/opticalglass/
.. image:: https://img.shields.io/conda/vn/conda-forge/opticalglass.svg
    :alt: Conda-Forge

OpticalGlass
============

Tools for reading optical material catalogs and libraries
---------------------------------------------------------

Common interface for sources of optical material data
-----------------------------------------------------

OpticalGlass provides a common API for querying refractive index data and other properties to a number of different optical material data sources. These include:

    * Excel spreadsheets published by optical glass manufacturers
    * Zemax ANSI Glass Format (.agf) files
    * The `RefractiveIndex.INFO <https://refractiveindex.info>`_ database

The global function `create_glass <https://opticalglass.readthedocs.io/en/latest/opticalglass.html#opticalglass.glassfactory.create_glass>`_ returns a `glass object <https://opticalglass.readthedocs.io/en/stable/opticalglass.html#opticalglass.opticalmedium.OpticalMedium>`_ given a glass name and, optionally, a catalog name. This glass instance can be queried for refractive index and transmittance values.

Interface to optical glass manufacturer glass data spreadsheets
---------------------------------------------------------------

The excel spreadsheets published by optical glass manufacturers are imported using `pandas`. The imported data is read into a dataframe and then mapped to the final glass catalog dataframe, with a common set of headings for different data categories.

The package currently supports the following manufacturers:

    * CDGM
    * Hikari
    * Hoya
    * Ohara
    * Schott
    * Sumita

.. note::

   All rights and ownership of the data is retained by the original owners, i.e the respective manufacturers.

Interface to .AGF files
-----------------------

OpticalGlass provides a wrapper around the .agf file importer in the ZemaxGlass package. Each .agf file is mapped to a Glass Catalog.


Interface to RefractiveIndex.INFO database
------------------------------------------

An interface to the RefractiveIndex.INFO database, using both the InterpolatedMedium and RIIMedium classes, is available.

Glass Map Application
---------------------

A desktop application is installed as part of OpticalGlass. It is invoked by running ``glassmap`` at the command line.

Documentation
-------------

The documentation for OpticalGlass is hosted at `Read the Docs <https://opticalglass.readthedocs.io>`_
