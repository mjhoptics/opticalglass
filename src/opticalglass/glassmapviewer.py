#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2018 Michael J. Hayford
""" desktop application for viewing glass catalog data

.. Created on Wed Jan  3 12:50:03 2018

.. codeauthor: Michael J. Hayford
"""
import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QMimeData, Slot
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QGridLayout, QSizePolicy, QGroupBox,
                               QCheckBox, QRadioButton, QTableView, QTabWidget, 
                               QLabel, QTextEdit, QItemDelegate)

from matplotlib.backends.backend_qtagg \
     import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt \
     import NavigationToolbar2QT as NavigationToolbar

from opticalglass.glassmap import GlassMapFigure
from opticalglass import glassfactory as gfact

logger = logging.getLogger(__name__)

def init_glass_libs(og_glass_libs):
    og_priority_order = [
        'xls',
        'agf',
        'rii-specs',
        'rii-organic',
        'rii-other',
        'rii-3d',
        ]
    og_glass_libs.search_order = og_priority_order

    xls_priority_order = ['Hoya', 'Ohara', 'Schott', 'CDGM', 'Hikari', 'Sumita']
    og_glass_libs['xls'].search_order = xls_priority_order

    agf_priority_order = [
    'hoya',
    'ohara',
    'schott',
    'misc',
    'cdgm',
    'hikari',
    'nikon',
    'sumita',
    'lzos',
    'lightpath',
    'corning',
    ]
    og_glass_libs['agf'].search_order = agf_priority_order

    rii_specs_priority_order = [
    'SCHOTT-optical',
    'OHARA-optical',
    'HIKARI-optical',
    'CDGM-optical',
    'HOYA-optical',
    'SUMITA-optical',
    'LZOS-optical',
    ]
    og_glass_libs['rii-specs'].search_order = rii_specs_priority_order


def init_UI(gui_parent, fig):
    main_widget = QWidget()
    layout = QHBoxLayout(main_widget)

    # leftBar = QVBoxLayout()
    # layout.addLayout(leftBar)

    gm = PlotCanvas(gui_parent, fig)
    layout.addWidget(gm)

    gui_parent.addToolBar(Qt.ToolBarArea.BottomToolBarArea,
                          NavigationToolbar(gm, gui_parent))

    rightBar = QVBoxLayout()
    layout.addLayout(rightBar)

    plotPartialsBar = QHBoxLayout()
    plotTypeGroup = createPlotTypeBox(gui_parent, fig)
    plotPartialsBar.addWidget(plotTypeGroup)

    partialsGroup = createPartialsBox(gui_parent, fig)
    plotPartialsBar.addWidget(partialsGroup)
    rightBar.addLayout(plotPartialsBar)

    # test_group = createTestWidgetBox(gui_parent=gui_parent, fig=fig)
    # rightBar.addWidget(test_group)

    libsGroup = createLibraryGroupBox(gui_parent, fig)
    rightBar.addWidget(libsGroup)

    pick_model = PickModel(fig)
    gmt = PickTable(gui_parent, pick_model)
    rightBar.addWidget(gmt)

    return main_widget, pick_model


def createTestWidgetBox(gui_parent, fig):
    groupBox = QGroupBox("Test Widget Area", gui_parent)
    groupBox.setMaximumWidth(sum(_pt_col_widths) + 20)

    test_md_str = "H<sub>2</sub>O:C<sub>3</sub>H<sub>5</sub>(OH)<sub>3</sub>"
    label = QLabel(test_md_str)
    textedit = QTextEdit()
    textedit.setMarkdown(test_md_str)

    vbox = QVBoxLayout()
    vbox.addWidget(label)
    vbox.addWidget(textedit)

    groupBox.setLayout(vbox)

    return groupBox

def createPlotTypeBox(gui_parent, fig):
    groupBox = QGroupBox("Plot Type", gui_parent)
    groupBox.setMaximumWidth(190)

    index_btn = QRadioButton("Refractive Index")
    index_btn.setChecked(True)
    index_btn.toggled.connect(lambda:
                              on_plot_type_toggled(fig, index_btn))
    partial_btn = QRadioButton("Partial Dispersion")
    partial_btn.toggled.connect(lambda:
                                on_plot_type_toggled(fig, partial_btn))
    buchdahl_btn = QRadioButton("Buchdahl Coefficients")
    buchdahl_btn.toggled.connect(lambda:
                                 on_plot_type_toggled(fig, buchdahl_btn))
    buchdahl_disp_btn = QRadioButton("Buchdahl Dispersion\nCoefficients")
    buchdahl_disp_btn.toggled.connect(
        lambda: on_plot_type_toggled(fig, buchdahl_disp_btn))

    vbox = QVBoxLayout()
    vbox.addWidget(index_btn)
    vbox.addWidget(partial_btn)
    vbox.addWidget(buchdahl_btn)
    vbox.addWidget(buchdahl_disp_btn)

    groupBox.setLayout(vbox)

    return groupBox


def createPartialsBox(gui_parent, fig):
    def on_ui_changed(fig, button):
        is_changed = False
        if button.text() == "Default range":
            if button.isChecked() is True:
                short = short_wl_default.text()
                long = long_wl_default.text()
                is_changed = True
        elif button.text() == "Blue range":
            if button.isChecked() is True:
                short = short_wl_blue.text()
                long = long_wl_blue.text()
                is_changed = True
        elif button.text() == "Red range":
            if button.isChecked() is True:
                short = short_wl_red.text()
                long = long_wl_red.text()
                is_changed = True
        if is_changed:
            fig.partials = (short, long)
            fig.refresh()

    groupBox = QGroupBox("Partial Dispersion", gui_parent)
    groupBox.setMaximumWidth(190)

    F_d_btn = QRadioButton("Default range")
    F_d_btn.setChecked(True)
    F_d_btn.toggled.connect(lambda:
                            on_ui_changed(fig, F_d_btn))
    short_wl_default = QLabel()
    short_wl_default.setText('F')

    long_wl_default = QLabel()
    long_wl_default.setText('d')

    blue_btn = QRadioButton("Blue range")
    blue_btn.toggled.connect(lambda:
                             on_ui_changed(fig, blue_btn))
    short_wl_blue = QLabel()
    short_wl_blue.setText('g')

    long_wl_blue = QLabel()
    long_wl_blue.setText('F')

    red_btn = QRadioButton("Red range")
    red_btn.toggled.connect(lambda:
                            on_ui_changed(fig, red_btn))
    short_wl_red = QLabel()
    short_wl_red.setText('d')

    long_wl_red = QLabel()
    long_wl_red.setText('C')

    layout = QGridLayout()
    groupBox.setLayout(layout)
    layout.addWidget(F_d_btn, 0, 0)
    layout.addWidget(short_wl_default, 0, 1)
    layout.addWidget(long_wl_default, 0, 2)
    layout.addWidget(blue_btn, 1, 0)
    layout.addWidget(short_wl_blue, 1, 1)
    layout.addWidget(long_wl_blue, 1, 2)
    layout.addWidget(red_btn, 2, 0)
    layout.addWidget(short_wl_red, 2, 1)
    layout.addWidget(long_wl_red, 2, 2)

    return groupBox


def on_plot_type_toggled(fig, button):
    plot_display_type = fig.plot_display_type
    if button.text() == "Refractive Index":
        if button.isChecked() is True:
            plot_display_type = "Refractive Index"
    elif button.text() == "Partial Dispersion":
        if button.isChecked() is True:
            plot_display_type = "Partial Dispersion"
    elif button.text() == "Buchdahl Coefficients":
        if button.isChecked() is True:
            plot_display_type = "Buchdahl Coefficients"
    elif button.text() == "Buchdahl Dispersion\nCoefficients":
        if button.isChecked() is True:
            plot_display_type = "Buchdahl Dispersion Coefficients"

    fig.plot_display_type = plot_display_type
    fig.refresh()


def createLibraryGroupBox(gui_parent, fig):
    tab = QTabWidget()
    tab.setMaximumWidth(sum(_pt_col_widths) + 20)

    for lib_name in fig.glass_libs:
        cat_pg = createCatalogGroupBox(gui_parent, fig, lib_name)
        tab.addTab(cat_pg, lib_name)

    return tab

def createCatalogGroupBox(gui_parent, fig, lib: str):
    groupBox = QGroupBox("Glass Catalogs", gui_parent)

    check_box_list = []

    for i, cat_name in enumerate(fig.glass_libs[lib]):
        checkBox = QCheckBox(cat_name)
        checkBox.setChecked(True)
        checkBox.stateChanged.connect(
            create_handle_lib_cat_checkbox(fig, i, lib, cat_name))
        check_box_list.append(checkBox)

    checkBox = QCheckBox("Select All")
    checkBox.setChecked(True)
    checkBox.stateChanged.connect(
        create_select_all_lib_cat_checkbox(fig, lib, check_box_list))
    check_box_list.insert(0, checkBox)

    vbox = QVBoxLayout()
    for cb in check_box_list:
        vbox.addWidget(cb)

    groupBox.setLayout(vbox)

    return groupBox


def create_select_all_lib_cat_checkbox(fig, lib, check_box_list):
    def select_all_checkbox(state):
        fig_delay_refresh = fig._delay_refresh
        fig._delay_refresh = True
        state = Qt.CheckState(state)
        checked = state == Qt.CheckState.Checked
        for checkBox in check_box_list:
            checkBox.setChecked(checked)
        fig._delay_refresh = False
        fig.refresh()
        fig._delay_refresh = fig_delay_refresh
    return select_all_checkbox


def create_handle_lib_cat_checkbox(fig, cb_number, lib, cat_name):
    def handle_checkbox(state):
        state = Qt.CheckState(state)
        checked = state == Qt.CheckState.Checked
        fig.glass_libs[lib].active_state[cat_name] = checked
        fig.updateVisibility(cb_number, checked)
        fig.refresh()
    return handle_checkbox


class GlassMapViewer(QMainWindow):
    def __init__(self, glass_libs, window_size=(1650, 1100)):
        super().__init__()

        self.title = 'Glass Map Viewer'
        self.setWindowTitle(self.title)

        self.left = 50
        self.top = 150
        self.width = window_size[0]
        self.height = window_size[1]
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.glass_libs = glass_libs

        self.plot_display_type = "Refractive Index"
        self.fig = GlassMapFigure(self.glass_libs,
                                  plot_display_type=self.plot_display_type,
                                  refresh_gui=self.refresh_gui,
                                  )
        self._main, self.pick_model = init_UI(self, self.fig)
        self.setCentralWidget(self._main)

        self.fig.plot()

    def refresh_gui(self, **kwargs):
        self.pick_model.fill_table(self.fig.pick_list)


_pt_header = ["Library", "Catalog", "Glass", "Nd", "Vd", "P F,d"]
_pt_format = ["{:s}", "{:s}", "{:s}", "{:7.5f}", "{:5.2f}", "{:6.4f}"]
_pt_col_widths = [65, 115, 100, 63, 52, 60]


class PickTable(QTableView):
    def __init__(self, gui_parent, pick_model):
        super().__init__(gui_parent)
        self.setModel(pick_model)
        self.setAlternatingRowColors(True)
        self.setMinimumWidth(285)
        self.setMaximumWidth(sum(_pt_col_widths) + 20)
        self.setDragEnabled(True)
        self.pickRow = 0
        for i, w in enumerate(_pt_col_widths):
            self.setColumnWidth(i, w)
        self.setItemDelegate(LabelDelegate(self))

    def mousePressEvent(self, event):
        """Initiate glass drag and drop operation from here. """
        super().mousePressEvent(event)
        if (
                event.button() == Qt.MouseButton.LeftButton and
                self.model().rowCount(0) > 0):
            drag = QDrag(self)
            mimeData = QMimeData()
            si = self.indexAt(event.pos())
            pick_row = si.row()
            pick = self.model().pick_table[pick_row]
            # comma separated list: glass_name,catalog_name,library_name
            mimeData.setText(pick[2] + ',' + pick[1] + ',' + pick[0])
            drag.setMimeData(mimeData)

            drag.exec_(Qt.DropAction.CopyAction)


class PickModel(QAbstractTableModel):
    def __init__(self, fig):
        super().__init__()
        self.fig = fig
        self.num_rows = 0
        self.pick_table = []
        self.pt_header = _pt_header

    def rowCount(self, index):
        return self.num_rows

    def columnCount(self, index):
        return len(self.pt_header)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section == 5:  # index of P F,d column
                    self.pt_header[section] = "P %s-%s" % self.fig.partials
                return self.pt_header[section]
            elif orientation == Qt.Orientation.Vertical:
                return None
        else:
            return None

    def data(self, index, role):
        if (role == Qt.ItemDataRole.DisplayRole or 
            role == Qt.ItemDataRole.EditRole):
            r = index.row()
            c = index.column()
            return self.pick_table[r][c]
        else:
            return None

    def fill_table(self, pick_list):
        self.pickRow = 0
        pick_table = []
        for item in pick_list:
            pick_table.append([f.format(v) for f, v in zip(_pt_format, item)])
        self.pick_table = pick_table

        if self.num_rows > 0:
            self.beginRemoveRows(QModelIndex(), 0, self.num_rows-1)
            self.removeRows(0, self.num_rows)
            self.endRemoveRows()

        self.num_rows = len(pick_table)
        if self.num_rows > 0:
            self.beginInsertRows(QModelIndex(), 0, self.num_rows-1)
            self.insertRows(0, self.num_rows)
            self.endInsertRows()


class LabelDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def get_label(self, option, index):
        value = index.data(Qt.ItemDataRole.DisplayRole)
        label = QLabel(value)
        label.resize(option.rect.size())
        return label

    def paint(self, painter, option, index):
        label = self.get_label(option, index)
        painter.save()
        pixmap = QPixmap(option.rect.size())
        label.render(pixmap)
        painter.drawPixmap(option.rect, pixmap)
        painter.restore()

    def sizeHint(self, option, index):
        label = self.get_label(option, index)
        return label.sizeHint()
    

class PlotCanvas(FigureCanvas):
    def __init__(self, gui_parent, fig):
        super().__init__(fig)
        self.setParent(gui_parent)
        logger.debug("Canvas dpi: {}".format(fig.dpi))

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        fig.plot()


def main():
    logging.basicConfig(filename='opticalglass.log',
                        filemode='w',
                        format='%(asctime)s: %(message)s',
                        level=logging.INFO)
    logger.info("opticalglass started")
    qtapp = QApplication(sys.argv)
    init_glass_libs(gfact.og_glass_libs)
    qtwnd = GlassMapViewer(gfact.og_glass_libs)
    qtwnd.show()
    return qtapp.exec()


if __name__ == '__main__':
    sys.exit(main())
