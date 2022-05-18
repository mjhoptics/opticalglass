#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interface to the `RefractiveIndex.INFO <https://refractiveindex.info>`_ database

.. Created on Sun Nov 14 21:03:50 2021

.. codeauthor: Michael J. Hayford
"""

import requests
import urllib.parse

import numpy as np
from scipy.interpolate import interp1d

import yaml

from typing import Union
from numpy.typing import NDArray

from opticalglass.opticalmedium import OpticalMedium, InterpolatedMedium
from .spectral_lines import get_wavelength


def get_glassname_from_filestr(filestr: str):
    """ try to construct a name and catalog from the filename/url """
    # strip off `.yml` and take final partition
    full_db_path = filestr[:-4].partition('database/data/')[-1]
    name_catalog = full_db_path.split('/')
    catalog = 'rii-'
    if name_catalog[0] == 'glass' or name_catalog[0] == 'other':
        catalog += name_catalog[1]
        name_catalog = name_catalog[2:]
    else:
        catalog += name_catalog[0]
        name_catalog = name_catalog[1:]

    if len(name_catalog) == 1:
        name = name_catalog[0]
    elif len(name_catalog) == 2:
        name = f"{name_catalog[0]} [{name_catalog[1]}]"
    else:
        name = name_catalog[0]
        for subname in name_catalog[1:]:
            name += '-' + subname

    return name, catalog


def read_rii_file(filename):
    ''' given a filename of a RII file, return a yaml instance. '''
    with filename.open() as file:
        inpt = file.read()
    yaml_data = yaml.safe_load(inpt)	

    name, catalog = get_glassname_from_filestr(str(filename))

    return yaml_data, name, catalog


def read_rii_url(url):
    ''' given a url to a RII file, return a yaml instance. '''
    r = requests.get(url, allow_redirects=True)

    r.encoding = r.apparent_encoding
    inpt = r.text

    yaml_data = yaml.safe_load(inpt)

    name, catalog = get_glassname_from_filestr(urllib.parse.unquote(url))

    return yaml_data, name, catalog


def create_material(yaml_data, label, catalog):
    num_datasets = len(yaml_data["DATA"])

    material_data = yaml_data["DATA"][0]
    material_type1 = material_data["type"]

    if material_type1 in formulas:
        cndr = read_coefficients(material_data, material_type1)
        coefs, rndx_fct, data_range = cndr
        matl = RIIMedium(label, coefs, rndx_fct, data_range=data_range, 
                         cat=catalog)
    elif 'tabulated' in material_type1:
        material_type1 = material_type1.split()[1]
        ds1 = read_data_arrays(material_data, material_type1)
        if len(ds1) == 2:
            wvls, n = ds1
            wvls_nm = np.array([w*1000. for w in wvls])
            matl = InterpolatedMedium(label, wvls=wvls_nm, rndx=n, cat=catalog)
        elif len(ds1) == 3:
            wvls, n, k = ds1
            wvls_nm = np.array([w*1000. for w in wvls])
            matl = InterpolatedMedium(label, wvls=wvls_nm, rndx=n, kvals=k, 
                                      cat=catalog)
            
    # Handle second data set. This will always be a tabulated data set. In practice, if not by definition, this dataset
    #  is always a `k` list. Any rindex data returned from read_data_arrays()
    #  will be ignored.
    if num_datasets == 2:
        material_data = yaml_data["DATA"][1]
        material_type2 = material_data["type"].split()[1]
        ds2 = read_data_arrays(material_data, material_type2)
        wvls, k = ds2[0], ds2[-1]
        matl.kvals = k
        matl.kvals_wvls = np.array([w*1000. for w in wvls])

    matl.yaml_data = yaml_data

    return matl


def read_coefficients(material_data, material_type):
    rndx_fct = formulas[material_type]
    wv_rng_str = material_data["wavelength_range"].split()
    data_range = np.array([float(w) for w in wv_rng_str])
    coefs_str = material_data["coefficients"].split()
    coefs = np.array([float(c) for c in coefs_str])
    return coefs, rndx_fct, data_range


def read_data_arrays(material_data, material_type):
    wvls = []
    num_wvls = 0
	#in this type of material read data line by line
    if material_type == 'k' or material_type == 'n':
        n_or_k = []
        for line in material_data["data"].splitlines():
            values = np.array([float(v) for v in line.split()])
            if num_wvls == 0:
                wvls.append(values[0]);
                n_or_k.append(values[1])
                num_wvls += 1
            else:
                if values[0] != wvls[-1]:
                    wvls.append(values[0]);
                    n_or_k.append(values[1])
                    num_wvls += 1
        wvls = np.array(wvls)
        n_or_k = np.array(n_or_k)
        return wvls, n_or_k
    else:
        n = []
        k = []
        for line in material_data["data"].splitlines():
            values = np.array([float(v) for v in line.split()])
            if num_wvls == 0:
                wvls.append(values[0]);
                n.append(values[1])
                k.append(values[2])
                num_wvls += 1
            else:
                if values[0] != wvls[-1]:
                    wvls.append(values[0]);
                    n.append(values[1])
                    k.append(values[2])
                    num_wvls += 1
        wvls = np.array(wvls)
        n = np.array(n)
        k = np.array(k)
        return wvls, n, k

def validate_wvls(wv_um, data_range):
    def fuzzy_less_than(x, a, fuzz=1e-14):
        return x < a - fuzz
    def fuzzy_greater_than(x, a, fuzz=1e-14):
        return x > a + fuzz
    if data_range is not None:
        if isinstance(wv_um, float):
            if fuzzy_less_than(wv_um, data_range[0]) or \
               fuzzy_greater_than(wv_um, data_range[1]):
                raise Exception("OutOfBands", 
                                f"No data for this material for this {wv_um}")
        else:
            if fuzzy_less_than(min(wv_um), data_range[0]) or \
                fuzzy_greater_than(max(wv_um), data_range[1]):
                if fuzzy_less_than(min(wv_um), data_range[0]):
                    bad_wv = min(wv_um)
                else:
                    bad_wv = max(wv_um)
                raise Exception("OutOfBands", 
                                f"No data for this material for this {bad_wv}")
    return True
    

def eval_formula_1(wv_nm, coeff, data_range=None):
    """Sellmeier (preferred) """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
	
    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in reversed(range(1, np.size(coeff), 2)):
        n += ((coeff[i]*wv_um**2)/(wv_um**2 - coeff[i+1]**2))
    n += coeff[0] + 1

    return np.sqrt(n)


def eval_formula_2(wv_nm, coeff, data_range=None):
    """Sellmeier 2 """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
	
    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in reversed(range(1, np.size(coeff), 2)):
        n += ((coeff[i]*wv_um**2)/(wv_um**2 - coeff[i+1]))
    n += coeff[0] + 1

    return np.sqrt(n)


def eval_formula_3(wv_nm, coeff, data_range=None):
    """Polynomial """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)

    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in range(1, np.size(coeff), 2):
        n += coeff[i]*wv_um**coeff[i+1]

    return np.sqrt(n)


def eval_formula_4(wv_nm, coeff, data_range=None):
    """RefractiveIndex.INFO """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
    num_coefs = np.size(coeff)

    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in range(1, 9, 4):
        n += coeff[i]*wv_um**coeff[i+1]/(wv_um**2-coeff[i+2]**coeff[i+3])

    for i in range(9, num_coefs, 2):
        n += coeff[i]*wv_um**coeff[i+1]

    # n += coeff[1]*wv_um**coeff[2]/(wv_um**2-coeff[3]**coeff[4])
    # n += coeff[5]*wv_um**coeff[6]/(wv_um**2-coeff[7]**coeff[8])
    # n += coeff[9]*wv_um**coeff[10]
    # n += coeff[11]*wv_um**coeff[12]
    # n += coeff[13]*wv_um**coeff[14]
    # n += coeff[15]*wv_um**coeff[16]

    return np.sqrt(n)


def eval_formula_5(wv_nm, coeff, data_range=None):
    """Cauchy """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
	
    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in range(1, np.size(coeff), 2):
        n += coeff[i]*wv_um**coeff[i+1]

    return n
    

def eval_formula_6(wv_nm, coeff, data_range=None):
    """Gases """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
	
    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    for i in reversed(range(1, np.size(coeff), 2)):
        n += ((coeff[i])/(coeff[i+1]**2 - wv_um**-2))
    n += 1.0

    return n


def eval_formula_7(wv_nm, coeff, data_range=None):
    """Hertzberger """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)
    num_coefs = np.size(coeff)

    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    n += coeff[1]/(wv_um**2 - 0.028)
    n += coeff[2]*(1/(wv_um**2 - 0.028))**2

    exponent = 2
    for i in range(3, num_coefs, 1):
        n += coeff[i]*wv_um**(exponent)
        exponent += 2

    return n


def eval_formula_8(wv_nm, coeff, data_range=None):
    """Retro """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)

    c = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    c += coeff[1]*wv_um**2/(wv_um**2-coeff[2])
    c += coeff[3]*wv_um**2

    n = -(2*c + 1)/(c - 1)

    return np.sqrt(n)


def eval_formula_9(wv_nm, coeff, data_range=None):
    """Exotic """
    wv_um = 0.001*wv_nm

    validate_wvls(wv_um, data_range)

    n = (coeff[0] if isinstance(wv_um, float) 
         else np.full(len(wv_um), coeff[0]))

    n += coeff[1]/(wv_um**2-coeff[2])
    n += coeff[3]*(wv_um - coeff[4])/((wv_um - coeff[4])**2 + coeff[5])

    return np.sqrt(n)


formulas = {
    'formula 1': eval_formula_1,
    'formula 2': eval_formula_2,
    'formula 3': eval_formula_3,
    'formula 4': eval_formula_4,
    'formula 5': eval_formula_5,
    'formula 6': eval_formula_6,
    'formula 7': eval_formula_7,
    'formula 8': eval_formula_8,
    'formula 9': eval_formula_9,
    }


class RIIMedium(OpticalMedium):
    def __init__(self, label, coefs, rndx_fct, data_range=None, 
                 kvals_wvls=None, kvals=None, 
                 mat='', cat=''):
        """
        Parameters
        ----------
        coefs : [float, ...]
            the coefficients of the model.
        rndx_fct : callable
            a fct implementing calc_rindex, given `coefs`
        mat : str
            a string label returned from the name() fct.
        cat : str
            a string label returned from the catalog_name() fct.
        """
        self.coefs = coefs
        self.rndx_fct = rndx_fct

        self.data_range = data_range
        self.wvls = np.linspace(data_range[0]*1000., data_range[1]*1000.)
    
        if kvals is not None:
            self.kvals_wvls = self.wvls if kvals_wvls is None else kvals_wvls
            self.kvals = kvals
        self.label = label
        self._catalog_name = cat

    def __json_encode__(self):
        attrs = dict(vars(self))
        if hasattr(self, 'yaml_data'):
            del attrs['yaml_data']
        return attrs

    def name(self) -> str:
        return self.label

    def catalog_name(self) -> str:
        return self._catalog_name

    def glass_code(self) -> str:
        nd = self.rindex('d')
        nF = self.rindex('F')
        nC = self.rindex('C')
        vd = (nd - 1)/(nF - nC)
        return str(1000*round((nd - 1), 3) + round(vd/100, 3))

    def update(self) -> None:
        if self.kvals is not None:
            self.kvals_interp = interp1d(self.wvls, self.kvals, kind='cubic',
                                         assume_sorted=False)
        else:
            self.kvals_interp = None

    def rindex(self, wvl: Union[float, str]) -> float:
        """Returns the refractive index from the quadratic model at wvl."""
        return self.calc_rindex(get_wavelength(wvl))

    def calc_rindex(self, wv_nm: Union[float, NDArray]) -> Union[float, NDArray]:
        return self.rndx_fct(wv_nm, self.coefs, data_range=self.data_range)

    def meas_rindex(self, wvl: str) -> float:
        """ returns the measured refractive index at wvl

        For `InterpolatedGlass` the measured index isn't directly known. The
        calculated index is used instead. Calling `rindex` handles the spectral 
        line conversion.
        """
        return self.rindex(wvl)

    def transmission_data(self, thi=10.0):
        t = thi*1.0e3
        t_vals = np.exp(-4.0*np.pi*t*self.kvals/self.kvals_wvls)
        return self.kvals_wvls, t_vals


def summary_plots(opt_medium, opt_medium_yaml):
    """ plot refractive index and thruput data, when available. """
    import matplotlib.pyplot as plt
    print(f"{[d['type'] for d in opt_medium_yaml['DATA']]}")

    plt.plot(opt_medium.wvls, opt_medium.calc_rindex(opt_medium.wvls), label='ref index')

    if getattr(opt_medium, 'kvals', None) is not None:
        plt.plot(opt_medium.kvals_wvls, opt_medium.kvals, label='k value')
        plt.plot(*opt_medium.transmission_data(), label='T @ 10mm')

    plt.title(f"{opt_medium.catalog_name()}: {opt_medium.name()}")
    plt.xlabel('wavelength (nm)')

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))