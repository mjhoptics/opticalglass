.. currentmodule:: opticalglass

##############################
RefractiveIndex.Info interface
##############################

Access to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database is provided by the :mod:`~.rindexinfo` module. A major function of this module is to create glass instances (:class:`~.rindexinfo.RIIMedium` or :class:`~.opticalmedium.InterpolatedMedium`) for use in optical models.



.. code:: ipython3

    from opticalglass.glassfactory import create_glass
    from opticalglass.rindexinfo import summary_plots

Typical use scenario - Polycarbonate
====================================

Ofttimes, a Google search of a "refractive index for Polycarbonate" will include a RefractiveIndex.Info link in the query. 
Follow the link to the page on `RefractiveIndex.INFO <https://refractiveindex.info>`_ for Polycarbonate.

.. image:: RII_page_top.png
   :align: center

----

The data is below this on the web page.

.. image:: RII_page_rindexdata.png
   :align: center

----

To get a link to the data for this material, scroll further down the webpage to the Data section:

.. image:: RII_page_data_links.png
   :align: center

----

Right mouse click on the ``Full database record`` link and choose the ``Copy Link Address`` menu item:

.. image:: RII_page_copy_data_link.png
   :align: center

----

We can now define a variable for the polycarbonate data url and paste the link we obtained above into the right hand side of the definition.

.. code:: ipython3

    polycarb_url = 'https://refractiveindex.info/database/data/organic/(C16H14O3)n%20-%20polycarbonate/nk/Zhang.yml'

The function :func:`~.glassfactory.create_glass` takes the URL of the material in the and the names and returns a glass instance.

.. code:: ipython3

    polycarb = create_glass(polycarb_url, "rindexinfo")

The :func:`~.rindexinfo.summary_plots` function can be used in a scripting environment to plot the (complex) refractive index data of a material.

.. code:: ipython3

    summary_plots(polycarb)


.. parsed-literal::

    ['tabulated nk']



.. image:: output_7_1.png


There is additional information available for each database entry, beyond refractive index and absorption. It is easiest to work directly with the imported yaml data. The `rindexinfo` materials returned from create_glass() all have a `yaml_data` attribute, i.e. the complete database record.

.. code:: ipython3

    polycarb.yaml_data.keys()




.. parsed-literal::

    dict_keys(['REFERENCES', 'COMMENTS', 'DATA'])



The 'DATA' key contains the raw index data. The 'REFERENCES' key is always present and documents the source of the data.

.. code:: ipython3

    polycarb.yaml_data['REFERENCES']




.. parsed-literal::

    '1) X. Zhang, J. Qiu, X. Li, J. Zhao, L. Liu.\nComplex refractive indices measurements of polymers in visible and near-infrared bands.\n<a href="https://doi.org/10.1364/AO.383831"><i>Appl. Opt.</i> <b>59</b>, 2337-2344 (2020)</a>\n(0.4-2 µm)<br>\n2) X. Zhang, J. Qiu, J. Zhao, X. Li, L. Liu.\nComplex refractive indices measurements of polymers in infrared bands.\n<a href="https://doi.org/10.1016/j.jqsrt.2020.107063"><i>J. Quant. Spectrosc. Radiat. Transf.</i> <b>252</b>, 107063 (2020)</a>\n(2-20 µm)\n'



The 'COMMENTS' key is often present with additional information. Other common keys include 'CONDITIONS' and 'PROPERTIES'.

.. code:: ipython3

    polycarb.yaml_data['COMMENTS']




.. parsed-literal::

    'Normal temperature and pressure. Manufacturer: Dedicated Plastic, China.\n'



Material file examples
======================

Below are a sampling of different material files of common interest.

SiO2
----

.. code:: ipython3

    sio2_url = 'https://refractiveindex.info/database/data/main/SiO2/nk/Malitson.yml'
    sio2 = create_glass(sio2_url, "rindexinfo")
    summary_plots(sio2)


.. parsed-literal::

    ['formula 1']



.. image:: output_16_1.png


CaF2
----

.. code:: ipython3

    caf2_url = 'https://refractiveindex.info/database/data/main/CaF2/nk/Daimon-20.yml'
    caf2 = create_glass(caf2_url, "rindexinfo")
    summary_plots(caf2)


.. parsed-literal::

    ['formula 2']



.. image:: output_18_1.png


Germanium
---------

.. code:: ipython3

    ge_url = 'https://refractiveindex.info/database/data/main/Ge/nk/Amotchkina.yml'
    ge = create_glass(ge_url, "rindexinfo")
    summary_plots(ge)


.. parsed-literal::

    ['tabulated nk']



.. image:: output_20_1.png


PEDOT
-----

.. code:: ipython3

    pedot_url = 'https://refractiveindex.info/database/data/other/mixed%20organic/PEDOT-PSS/nk/Chen.yml'
    pedot = create_glass(pedot_url, "rindexinfo")
    summary_plots(pedot)


.. parsed-literal::

    ['tabulated n', 'tabulated k']



.. image:: output_22_1.png


F1 LZOS
-------

.. code:: ipython3

    url = 'https://refractiveindex.info/database/data/specs/lzos/optical/F1.yml'
    F1 = create_glass(url, "rindexinfo")
    summary_plots(F1)


.. parsed-literal::

    ['tabulated n']



.. image:: output_24_1.png


MgF2
----

.. code:: ipython3

    url_root = 'https://refractiveindex.info/database/data/'

.. code:: ipython3

    url = url_root + 'main/MgF2/nk/Li-e.yml'

.. code:: ipython3

    MgF2 = create_glass(url, "rindexinfo")
    summary_plots(MgF2)


.. parsed-literal::

    ['formula 1']



.. image:: output_28_1.png


KNbO3
-----

.. code:: ipython3

    url = url_root + 'main/KNbO3/nk/Umemura-alpha.yml'

.. code:: ipython3

    KNbO3 = create_glass(url, "rindexinfo")
    summary_plots(KNbO3)


.. parsed-literal::

    ['formula 4']



.. image:: output_31_1.png


.. code:: ipython3

    KNbO3.data_range




.. parsed-literal::

    array([0.4, 5.3])



.. code:: ipython3

    KNbO3.yaml_data




.. parsed-literal::

    {'REFERENCES': 'N. Umemura, K. Yoshida, and K. Kato. Phase-matching properties of KNbO<sub>3</sub> in the mid-infrared, <a href="    https://doi.org/10.1364/AO.38.000991"><i>Appl Opt.</i> <b>38</b>, 991-994 (1999)</a>\n',
     'COMMENTS': 'n<sub>α</sub>; 22 °C.\n',
     'DATA': [{'type': 'formula 4',
       'wavelength_range': '0.40 5.3',
       'coefficients': '4.4222 0.09972 0 0.05496 1 0 0 0 1 -0.01976 2'}]}



.. code:: ipython3

    KNbO3.coefs




.. parsed-literal::

    array([ 4.4222 ,  0.09972,  0.     ,  0.05496,  1.     ,  0.     ,
            1.     ,  0.     ,  1.     , -0.01976,  2.     ])



.. code:: ipython3

    len(KNbO3.coefs)




.. parsed-literal::

    11



