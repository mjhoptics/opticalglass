.. currentmodule:: opticalglass

=========
Changelog
=========

Version 2.0.0
=============
This release is a major upgrade to OpticalGlass. The :mod:`~.xls_glass` module for reading Zemax AGF files has been added and a local copy of |RII|_ can be used as a source of data. To handle this additional data, a :class:`~.glasslibs.GlassLibrary` is used to collect instances of GlassCatalogs. When :mod:`~.glassfactory` is imported, a central library |og_glass_libs| is created containing the following libraries:

	- 'user': the 'custom' GlassCatalog wraps the custom_glass_registry
	- 'xls': catalog data source is an Excel spreadsheet
	- 'agf': catalog data source is a Zemax .agf file
	- 'rii': web urls are imported into the 'rindexinfo' catalog
	- 'rii-main': 'main' "Shelf" of RII dataset
	- 'rii-organic': 'organic' "Shelf" of RII dataset
	- 'rii-glass': 'glass' "Shelf" of RII dataset
	- 'rii-other': 'other' "Shelf" of RII dataset
	- 'rii-specs': 'specs' "Shelf" of RII dataset
	- 'rii-3d': '3d' "Shelf" of RII dataset
	- 'robb': legacy dataset from the 1980s

GlassLibraries may be queried to find all occurances of glasses and catalogs.

The :mod:`~.glass` module was renamed to :mod:`~.xls_glass`.

:mod:`~.glassmapviewer` and :mod:`~.glassmap` were substantially rewritten to use |og_glass_libs| as a data source. The classes :class:`~.glassmap.GlassMapDB` and :class:`~.glassmap.GlassMapSet` were removed.

Version 1.2.0
=============
Updated the spreadsheets for the vendors to the most recent publicly available data. This includes a major update to the CDGM data, to support two different dispersion formula. The method :meth:`~opticalglass.glass.GlassPandas.transmission_data` enables different thicknesses to be queried, if the catalog data is available. Min python version is 3.12.

Version 1.1.1
=============
Add custom_glass_registry and functions to :func:`~opticalglass.glassfactory.register_glass`, :func:`~opticalglass.glassfactory.list_custom_glasses`, :func:`~opticalglass.glassfactory.save_custom_glasses` and :func:`~opticalglass.glassfactory.load_custom_glasses`. Thanks to @fujiisoup for the suggestion and implementation.
Complete the fix to RefractiveIndexInfo data hierarchy rearrangement.

Version 1.1.0
=============
Port to PySide6 for Qt app support. This gains support for Mac silicon with conda-forge availability. Move to Numpy 2.1.3 and other dependency tweaks.

Version 1.0.9
=============
Fix broken compatability with `RefractiveIndex.INFO <https://refractiveindex.info>`_ database. Extend  :func:`~opticalglass.glassfactory.create_glass` functionality to accept RefractiveIndex.Info URLs or filepaths.

Version 1.0.8
=============
Fix issue #8, add local loggers for better control of python's logging 
capability. Thanks to @dominikonysz for reporting and implementing the change.

Version 1.0.7
=============
Fix issue #7, previous version broke handling of catalog lists. Thanks to @dominikonysz for reporting and suggesting the fix.

Version 1.0.6
=============
Bullet-proof and add testcase for :func:`~opticalglass.glassfactory.create_glass`.

Version 1.0.5
=============
Enable :class:`~.rindexinfo.RIIMedium` to be saved and restored as JSON files.

Version 1.0.4
=============
Allow extrapolation for :class:`~opticalglass.opticalmedium.InterpolatedMedium` refractive index interpolation function. Cleanup help and other references to transported classes from **ray-optics**. Fix version export in build process.

Version 1.0.3
=============
Remove :meth:`~opticalglass.opticalmedium.OpticalMedium.transmission_data` from the required interfaces for :class:`~opticalglass.opticalmedium.OpticalMedium`. Add :class:`~opticalglass.opticalmedium.ConstantIndex` class for minimal material definition support. Add a new module, :mod:`~opticalglass.modelglass`, with class :class:`~opticalglass.modelglass.ModelGlass` to handle glasses specified by refractive index and v-number. Redo package layout using pyscaffold and use versioning from importlib.metadata.

Version 1.0.2
=============
Bump version of pyqt5 to 5.15.

Version 1.0.1
=============
Miscellaneous fixes and updates to the package dependencies.

Version 1.0.0
=============
Replace Excel-based importing and reading of the glass manufacturers Excel data files with a pandas-based approach. Glass and Glass Catalog were completely replaced by pandas-based versions. Implementations for a particular catalog rely on specifying the spreadsheet areas for various categories of data.

An Abstract Base Class, :class:`~opticalglass.opticalmedium.OpticalMedium` was defined to support access to the optical properties of a material. Two materials, :class:`~opticalglass.opticalmedium.Air` and :class:`~opticalglass.opticalmedium.InterpolatedMedium` were moved from the **ray-optics** package.

Finally, an interface to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database was implemented, using :class:`~opticalglass.rindexinfo.RIIMedium` and :class:`~opticalglass.opticalmedium.InterpolatedMedium`

Version 0.7.6
=============
Final version based on xlrd and openpyxl packages.
