User's Guide
============

Optical glass manufacturers provide detailed technical data for optical glasses via Excel spreadsheets. The ``opticalglass`` package provides uniform access to data from different vendors.

.. note::

   The spreadsheets containing the glass data are from the vendor websites. The vendors retain all ownership and copyrights to that data.

Installation
------------

To install ``opticalglass`` using pip, use

.. code::

   > pip install opticalglass

Glass Map Application
---------------------

A desktop application is installed as part of ``opticalglass``. It is invoked by running ``glassmap`` at the command line.

.. code::

   > glassmap

On a Windows machine, the ``glassmap`` command will be located in a Scripts directory underneath the install directory. For example, if using a virtual environment named ``optgla``, the command would be

.. code::

   > \optgla\Scripts\glassmap

Clicking on a glass or glasses in the map will list the glasses and their catalog plus index, V-number and partial dispersion in the table at the right.

.. image:: _images/RefractiveIndex.png

Partial dispersion data can be displayed by clicking on the plot type in the upper right hand panel.

.. image:: _images/PartialDispersion.png

Display of different catalogs can be controlled by selecting or unselecting checkboxs in the Glass Catalogs panel on the right.

.. image:: _images/CatalogSelection.png

Command Line Quick Start
------------------------

Two families of objects are provided to manage access to glass data. The :class:`~opticalglass.glass.GlassCatalog` base class manages the generic operations on the catalog. Subclasses of :class:`~opticalglass.glass.GlassCatalog` provide specific mapping information for the vendor spreadsheet format. The :class:`~opticalglass.glass.Glass` base class manages the generic operations on the individual glass instances, principally the index interpolation function :func:`~opticalglass.glass.Glass.calc_rindex`.

A factory interface to ``Glass`` creation is the function :func:`~opticalglass.glassfactory.create_glass` that returns a ``Glass`` instance of the appropriate catalog type, given the glass and catalog names.

The following is an example of using ``opticalglass`` interactively.

.. code:: python

   In [1]: import numpy as np

   In [2]: import matplotlib.pyplot as plt

   In [3]: import opticalglass as og

   In [4]: from opticalglass.glassfactory import create_glass

   In [5]: bk7=create_glass('N-BK7', 'Schott')

   In [6]: bk7
   Out[6]: SchottGlass('N-BK7')

   In [7]: str(bk7)
   Out[7]: 'Schott N-BK7: 517.642'

   In [8]: bk7.glass_code()
   Out[8]: '517.642'

   In [9]: nd = bk7.rindex('d')
	  ...: nF = bk7.rindex('F')
	  ...: nC = bk7.rindex('C')
	  ...: nC, nd, nF
   Out[9]: (1.5143223472613747, 1.5168000345005885, 1.5223762897312285)

   In [10]: dFC = nF-nC
	   ...: vd = (nd - 1.0)/dFC
	   ...: PCd = (nd-nC)/dFC
	   ...: print(nd, vd, PCd)
   1.5168000345005885 64.1673362374998 0.30763657034898056

   In [11]: bk7.rindex(555.0)
   Out[11]: 1.5182740250316704

   In [12]: wl=[]
	   ...: rn=[]
	   ...: for i in np.linspace(365., 700., num=75):
	   ...:     wl.append(i)
	   ...:     rn.append(bk7.rindex(i))
	   ...: plt.plot(wl,rn)
   Out[12]: [<matplotlib.lines.Line2D at 0x120f95860>]

.. image:: _images/Index_vs_wvl.png
