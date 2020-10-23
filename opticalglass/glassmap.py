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
from matplotlib.transforms import Bbox

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
                    cat_name = 'System'
                    catalog = GlassMapSet(arg, cat_name)
                    self.catalogs.append((catalog, cat_name))

    def get_data_at(self, i, **kwargs):
        catalog, cat_name = self.catalogs[i]
        return catalog.glass_map_data(cat_name=cat_name, **kwargs)

    def get_data_set_label_at(self, i):
        return self.catalogs[i][1]


class GlassMapSet():
    """Set of glass instances to be displayed in a GlassMapFigure. """

    def __init__(self, glass_list, cat_name):
        """The main requirement is the glass instance must respond to
        rindex() api
        """
        self.glass_list = glass_list
        self.cat_name = cat_name

    def catalog_name(self):
        return self.cat_name

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
           (255/255, 165/255, 0/255),  # orange 1
           (139/255, 139/255, 131/255),  # ivory 4
           ]
    mkr = ['^', 'x', '2', 's', 'v', '+', '*', 'D', 'o']
    home_bbox = Bbox(np.array([[95., 1.45], [20., 2.05]]))

    def __init__(self, glass_db, db_display=None, hover_glass_names=True,
                 plot_display_type="Refractive Index",
                 # width=5, height=4,
                 refresh_gui=None, **kwargs):
        # kwargs['figsize'] = (width, height)
        super().__init__(**kwargs)
        self.refresh_gui = refresh_gui
        self.glass_db = glass_db
        num_catalogs = len(glass_db.catalogs)
        self.db_display = db_display if db_display else [True]*num_catalogs
        self.plot_display_type = plot_display_type
        self.hover_glass_names = hover_glass_names
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
        """Fill in raw_data array.

        The raw_data attribute is a list over catalogs. Each catalog has an
        item consisting of the catalog name and a tuple of vectors:
            n, v, p, coefs0, coefs1, glass_names

        """
        self.rawData = []
        ctyp = ("disp_coefs"
                if self.plot_display_type == "Buchdahl Dispersion Coefficients"
                else None)
        for i, display in enumerate(self.db_display):
            gmap_data = self.glass_db.get_data_at(i, ctype=ctyp)
            n, v, p, coefs0, coefs1, glass_names = gmap_data
            catalog_name = self.glass_db.get_data_set_label_at(i)
            self.rawData.append([catalog_name,
                                 (n, v, p, coefs0, coefs1, glass_names)])
        return self

    def update_axis_limits(self, bbox):
        self.ax.set_xlim(bbox[0][0], bbox[1][0])
        self.ax.set_ylim(bbox[0][1], bbox[1][1])

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
                         # linestyle='None', markersize=7,
                         alpha=0.75, gid=i, picker=5,
                         color=self.dsc[i],
                         # marker=self.mkr[i], fillstyle='none',
                         label=self.rawData[i][0], visible=display)

        if self.plot_display_type == "Refractive Index":
            # provide a default minimum area, and update view limits accordingly
            viewLim = Bbox.union([self.home_bbox, self.ax.viewLim])
            self.update_axis_limits(viewLim.get_points())

        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_press)

        if self.hover_glass_names:
            self.canvas.mpl_connect("motion_notify_event", self.on_hover)

            self.hover_list = self.ax.annotate(
                "", xy=(0, 0), xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"))
            self.hover_list.set_visible(False)

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

    # --- interactive actions
    def find_artists_at_location(self, event):
        """Returns a list of shapes in zorder at the event location."""
        artists = []
        for artist in self.ax.get_children():
            inside, info = artist.contains(event)
            if inside:
                id = artist.get_gid()
                if id is not None:
                    artists.append((artist, info, id))

        return sorted(artists, key=lambda a: a[0].get_zorder(),
                      reverse=True)

    def on_hover(self, event):
        vis = self.hover_list.get_visible()
        artists = self.find_artists_at_location(event)
        info_text = []
        if len(artists) > 0:
            for a in artists:
                artist, info, id = a
                if self.db_display[id]:
                    ind = info['ind']
                    cat_name = self.rawData[id][0]
                    n, v, p, coef0, coef1, glass_name = self.rawData[id][1]
                    for k in ind:
                        text = glass_name[k] + ', ' + cat_name
                        info_text.append(text)
            # Update annotation with glass list
            info_text = '\n'.join(info_text)
            self.hover_list.set_text(info_text)
            pos = event.xdata, event.ydata
            self.hover_list.xy = pos
            self.hover_list.get_bbox_patch().set_alpha(0.8)
            self.hover_list.set_visible(True)
            self.canvas.draw_idle()
        else:
            if vis:
                self.hover_list.set_visible(False)
                self.canvas.draw_idle()

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
