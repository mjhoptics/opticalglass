.. currentmodule:: opticalglass

=========
Changelog
=========

Version 1.1.0
=============
Port to PySide6 for Qt app support. This gains support for Mac silicon with conda-forge availability. Move to Numpy 2.1.3 and other dependency tweaks.

Version 1.0.9
=============
Fix broken compatability with `RefractiveIndex.INFO <https://refractiveindex.info>`_ database. Extend  :func:`~.glassfactory.create_glass` functionality to accept RefractiveIndex.Info URLs or filepaths.

Version 1.0.8
=============
Fix issue #8, add local loggers for better control of python's logging 
capability. Thanks to @dominikonysz for reporting and implementing the change.

Version 1.0.7
=============
Fix issue #7, previous version broke handling of catalog lists. Thanks to @dominikonysz for reporting and suggesting the fix.

Version 1.0.6
=============
Bullet-proof and add testcase for :func:`~.glassfactory.create_glass`.

Version 1.0.5
=============
Enable :class:`~.rindexinfo.RIIMedium` to be saved and restored as JSON files.

Version 1.0.4
=============
Allow extrapolation for :class:`~.opticalmedium.InterpolatedMedium` refractive index interpolation function. Cleanup help and other references to transported classes from **ray-optics**. Fix version export in build process.

Version 1.0.3
=============
Remove :meth:`~.opticalmedium.OpticalMedium.transmission_data` from the required interfaces for :class:`~.opticalmedium.OpticalMedium`. Add :class:`~.opticalmedium.ConstantIndex` class for minimal material definition support. Add a new module, :mod:`~.modelglass`, with class :class:`~.modelglass.ModelGlass` to handle glasses specified by refractive index and v-number. Redo package layout using pyscaffold and use versioning from importlib.metadata.

Version 1.0.2
=============
Bump version of pyqt5 to 5.15.

Version 1.0.1
=============
Miscellaneous fixes and updates to the package dependencies.

Version 1.0.0
=============
Replace Excel-based importing and reading of the glass manufacturers Excel data files with a pandas-based approach. Glass and Glass Catalog were completely replaced by pandas-based versions. Implementations for a particular catalog rely on specifying the spreadsheet areas for various categories of data.

An Abstract Base Class, :class:`~.opticalmedium.OpticalMedium` was defined to support access to the optical properties of a material. Two materials, :class:`~.opticalmedium.Air` and :class:`~.opticalmedium.InterpolatedMedium` were moved from the **ray-optics** package.

Finally, an interface to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database was implemented, using :class:`~.rindexinfo.RIIMedium` and :class:`~.opticalmedium.InterpolatedMedium`

Version 0.7.6
=============
Final version based on xlrd and openpyxl packages.
