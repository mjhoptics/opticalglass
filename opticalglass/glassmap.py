#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""

.. Created on Thu Sep 24 22:09:48 2020

.. codeauthor: Michael J. Hayford
"""
import numpy as np

from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from . import glass as cat_glass
from . import glassfactory as gf
from . import glasspolygons as gp
from . import util


class GlassMapDB():
    """ Simple model to support Model/View architecture for Glass map views """

    def __init__(self, *args):
        # if no arguments, use the default set of catalogs
        if len(args) == 0:
            args = (gf._catalog_list,)

        self.catalogs = []
        for arg in args:
            if isinstance(arg, dict):
                for cat_name, catalog in arg.items():
                    self.catalogs.append((catalog, cat_name))
            if isinstance(arg, list):
                if isinstance(arg[0], str):
                    # treat as a list of catalog names
                    for cat_name in arg:
                        catalog = gf.get_glass_catalog(cat_name)
                        self.catalogs.append((catalog, cat_name))
                else:
                    # treat as glass instances, wrap them in a GlassMapSet
                    catalog = GlassMapSet(arg)
                    self.catalogs.append((catalog, 'System'))

    def get_data_at(self, i, **kwargs):
        catalog, cat_name = self.catalogs[i]
        return catalog.glass_map_data(cat_name=cat_name, **kwargs)

    def get_data_set_label_at(self, i):
        return self.catalogs[i][1]


class GlassMapSet():
    """Set of glass instances to be displayed in a GlassMapFigure. """

    def __init__(self, glass_list):
        """The main requirement is the glass instance must respond to
        rindex() api
        """
        self.glass_list = glass_list

    def glass_map_data(self, wvl='d', **kwargs):
        return calc_glass_map_arrays(self.glass_list, wvl, 'F', 'C', **kwargs)


def calc_glass_map_arrays(glass_list, d_str, F_str, C_str, **kwargs):
    """ return index and dispersion data arrays for input spectral range

    Args:
        nd_str (str): central wavelength string
        nf_str (str): blue end wavelength string
        nc_str (str): red end wavelength string

    Returns:
        index, V-number, partial dispersion, Buchdahl coefficients, and
        glass names
    """

    nd = np.array([g.rindex(d_str) for g in glass_list])
    nF = np.array([g.rindex(F_str) for g in glass_list])
    nC = np.array([g.rindex(C_str) for g in glass_list])

    vd, PCd = cat_glass.calc_glass_constants(nd, nF, nC)

    nd, coefs = cat_glass.calc_buchdahl_coords(
        nd, nF, nC, wlns=(d_str, F_str, C_str), **kwargs)

    names = [g.name()+'/'+g.catalog_name() for g in glass_list]
    return nd, vd, PCd, coefs[0], coefs[1], names


class GlassMapFigure(Figure):
    dsc = [(56/255, 142/255, 142/255),  # sgi teal
           (133/255, 133/255, 133/255),  # grey 52
           (113/255, 113/255, 198/255),  # sgi slateblue
           (102/255, 205/255, 0),  # chartreuse 3
           (255/255, 114/255, 86/255),  # coral 1
           (255/255, 165/255, 0/255)]  # orange 1

    def __init__(self, glass_db, db_display, plot_display_type,
                 width=5, height=4, refresh_gui=None, **kwargs):
        super().__init__(figsize=(width, height), **kwargs)
        self.refresh_gui = refresh_gui
        self.glass_db = glass_db
        self.db_display = db_display
        self.plot_display_type = plot_display_type
        self.needsClear = True
        self.pick_list = []

        self.update_data()

    def get_display_label(self):
        return self.plot_display_type

    def refresh(self, **kwargs):
        """Call update_data() followed by plot(), return self.

        Args:
            kwargs: keyword arguments are passed to update_data

        Returns:
            self (class Figure) so scripting envs will auto display results
        """
        self.update_data(**kwargs)
        self.plot()
        return self

    def update_data(self, **kwargs):
        self.rawData = []
        ctyp = ("disp_coefs"
                if self.plot_display_type == "Buchdahl Dispersion Coefficients"
                else None)
        for i, display in enumerate(self.db_display):
            gmap_data = self.glass_db.get_data_at(i, ctype=ctyp)
            n, v, p, coefs0, coefs1, lbl = gmap_data
            dsLabel = self.glass_db.get_data_set_label_at(i)
            self.rawData.append([dsLabel, (n, v, p, coefs0, coefs1, lbl)])
        return self

    def draw_axes(self):
        self.ax.grid(True)
        if hasattr(self, 'header'):
            self.ax.set_title(self.header, pad=10.0, fontsize=18)
        if hasattr(self, 'x_label'):
            self.ax.set_xlabel(self.x_label)
        if hasattr(self, 'y_label'):
            self.ax.set_ylabel(self.y_label)

    def plot(self):
        try:
            self.ax.cla()
        except AttributeError:
            self.ax = self.add_subplot(1, 1, 1)

        if self.plot_display_type == "Refractive Index":
            self.x_label = r'$\mathrm{V_d}$'
            self.y_label = r'$\mathrm{n_d}$'
            xi = 1
            yi = 0
            self.draw_glass_polygons()
        elif self.plot_display_type == "Partial Dispersion":
            self.x_label = r'$\mathrm{V_d}$'
            self.y_label = r'$\mathrm{P_{C-d}}$'
            xi = 1
            yi = 2
        elif self.plot_display_type == "Buchdahl Coefficients":
            self.x_label = r'$\mathrm{\nu_2}$'
            self.y_label = r'$\mathrm{\nu_1}$'
            xi = 4
            yi = 3
        elif self.plot_display_type == "Buchdahl Dispersion Coefficients":
            self.x_label = r'$\mathrm{\eta_2}$'
            self.y_label = r'$\mathrm{\eta_1}$'
            xi = 4
            yi = 3
        self.ax.set_title(self.get_display_label())
        for i, display in enumerate(self.db_display):
            self.ax.plot(self.rawData[i][1][xi], self.rawData[i][1][yi],
                         linestyle='None', marker='o', markersize=5,
                         alpha=0.75, gid=i, picker=5,
                         # color=self.dsc[i], alpha=0.75, gid=i, picker=5,
                         label=self.rawData[i][0], visible=display)

        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_press)

        if xi == 1:
            self.ax.invert_xaxis()
        self.draw_axes()
        self.ax.legend()
        self.canvas.draw()
        return self

    def draw_glass_polygons(self):
        for glass, poly in gp.polygons.items():
            rgb = gp.rgb[glass]
            p = Polygon(poly, closed=True, fc=util.rgb2mpl(rgb), ec='black',
                        linewidth=1.0)
            self.ax.add_artist(p)

    def clear_pick_table(self):
        self.pick_list = []
        self.needsClear = False

    def on_press(self, event):
        if self.needsClear:
            # If needsClear is still set, there have been no pick events so
            #  this is a click in an empty region of the plot.
            #  Clear the pick table
            self.clear_pick_table()
        else:
            # on_press event happens after on_pick events. Set needsClear for
            #  next on_pick, i.e. a new selection, to handle
            self.needsClear = True
        if self.refresh_gui is not None:
            self.refresh_gui()

    def on_pick(self, event):
        if self.needsClear:
            self.clear_pick_table()
        line = event.artist
        id = line.get_gid()
        if self.db_display[id]:
            ind = event.ind
            dsLabel = self.rawData[id][0]
            n, v, p, coef0, coef1, lbl = self.rawData[id][1]
            for k in ind:
                glass = (dsLabel, lbl[k], n[k], v[k], p[k])
                self.pick_list.append(glass)

    def updateVisibility(self, indx, state):
        self.ax.lines[indx].set_visible(state)
        self.canvas.draw()
