.. currentmodule:: opticalglass

=========
Changelog
=========

Version 1.0.0
=============
Replace Excel-based importing and reading of the glass manufacturers Excel data files with a pandas-based approach. Glass and Glass Catalog were completely replaced by pandas-based versions. Implementations for a particular catalog rely on specifying the spreadsheet areas for various categories of data.

An Abstract Base Class, :class:`~.opticalmedium.OpticalMedium` was defined to support access to the optical properties of a material. Two materials, :class:`~.opticalmedium.Air` and :class:`~.opticalmedium.InterpolatedMedium` were moved from the **ray-optics** package.

Finally, an interface to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database was implemented, using :class:`~.rindexinfo.RIIMedium` and :class:`~.opticalmedium.InterpolatedMedium`

Version 0.7.6
=============
Final version based on xlrd and openpyxl packages.
