""" package supplying optical glass data from vendor supplied data

    The :mod:`opticalglass` package currently supports the following vendors:

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
    :func:`~.glassfactory.create_glass` function returns a glass object, given 
    the glass and catalog names.

    An interface to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ 
    database is provided by the :mod:`~.rindexinfo` module. :func:`~.rindexinfo.read_rii_file`
    and :func:`~.rindexinfo.read_rii_url` return the native yaml representation
    used by RefractiveIndex.INFO. The :func:`~.rindexinfo.create_material` 
    function returns an object depending on the yaml database specification. If 
    the material is specified by an interpolating polynomial, a :class:`~.rindexinfo.RIIMedium`
    instance is returned. If the material is specified by a set of data points, 
    an :class:`~.opticalmedium.InterpolatedMedium` instance is returned.

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
