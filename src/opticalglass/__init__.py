""" 
    Common interface for sources of optical material data

    OpticalGlass provides a common API to a number of different optical material data sources. These include

    - interfaces to vendor supplied Excel spreadsheets with glass data.
    - ability to import material files in the Zemax .agf data format.
    - ability to import material data from the |RII|_ database.

    These and other sources of data are organized into libraries. Each library contains one or more catalogs, and each catalog contains one or more glasses. The glass catalog of particular vendors (e.g. Hoya, Ohara, Schott) will be found in multiple libraries. The user can control the order in which the libraries are searched, as well as the order of the catalogs available from each library.

    The global variable |og_glass_libs| is an instance of the :class:`~.glassfactory.CentralGlassLibrary` class that contains the various libraries and catalogs. 

    OpticalGlass currently supports glass spreadsheets fromthe following vendors:

        - CDGM
        - Hikari
        - Hoya
        - Ohara
        - Schott
        - Sumita

    The spreadsheets from the vendors are in the ``data`` directory. They are
    imported using :mod:`pandas` into |DataFrame| instances, one per catalog.
    The data in the catalog |DataFrame| is used unchanged from the import; only
    the data headers are modified for consistency across catalogs. The 
    :func:`~.glassfactory.create_glass` function returns a |OpticalMedium| 
    object, given the glass and catalog names.

    An interface to the |RII|_ database is provided by the :mod:`~.rindexinfo` 
    module. 

    A set of legacy catalogs, circa 1980, is available via the
    :class:`~glass.Robb1983Catalog` class. The data used by this class is from
    the 1983 paper by Paul N. Robb and R. I. Mercado, `Calculation of
    refractive indices using Buchdahl’s chromatic coordinate
    <https://doi.org/10.1364/AO.22.001198>`_ . The catalogs include:

        - Hoya
        - Ohara
        - Schott
        - Chance
        - Corning-France

    The authors fitted a Buchdahl quadratic model to the glass data that has a
    standard deviation of 0.00002 and a maximum absolute error of 0.0001 in the
    visible spectral region.

    Fitting and modeling glass data using the Buchdahl chromatic coordinate is
    supported in the :mod:`~.buchdahl` module.
"""
from importlib.metadata import version

try:
    __version__ = version(__name__)
except:
    __version__ = 'unknown'
finally:
    del version
