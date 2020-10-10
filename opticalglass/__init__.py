""" package supplying optical glass data from vendor supplied data

    The :mod:`opticalglass` package currently supports the following vendors:

        - CDGM
        - Hikari
        - Hoya
        - Ohara
        - Schott
        - Sumita

    The spreadsheets from the vendors are in the ``data`` directory.

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
