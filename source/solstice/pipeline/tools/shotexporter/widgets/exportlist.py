#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base definition for export list widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import collections

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.gui import splitters
from solstice.pipeline.resources import resource

from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.widgets import exportreewidget

reload(defines)
reload(exportreewidget)


class BaseExportList(QWidget, object):

    ExportType = 'EXPORT'
    IconMode = 'icon'
    TableMode = 'table'

    itemClicked = Signal(object)
    itemDoubleClicked = Signal(object)
    zoomChanged = Signal(object)
    spacingChanged = Signal(object)
    updateProperties = Signal(QObject)
    refresh = Signal()

    def __init__(self, parent=None):
        super(BaseExportList, self).__init__(parent=parent)

        self._dpi = 1
        self._padding = defines.DEFAULT_EXPORT_LIST_PADDING
        w, h = defines.DEFAULT_EXPORT_LIST_ZOOM_AMOUNT, defines.DEFAULT_EXPORT_LIST_ZOOM_AMOUNT

        self._data = None

        self._icon_size = QSize(w, h)
        self._item_size_hint = QSize(w, h)
        self._zoom_amount = defines.DEFAULT_EXPORT_LIST_ZOOM_AMOUNT
        self._is_item_text_visible = True

        self._tree_widget = exportreewidget.ExportTreeWidget()

        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._tree_widget)



    #     self.widget_tree = collections.defaultdict(list)
    #     self.widgets = list()
    #
    #     self.setMouseTracking(True)
    #
    #     self.custom_ui()
    #     self.setup_signals()
    #
    # def custom_ui(self):
    #     self.main_layout = QVBoxLayout()
    #     self.main_layout.setAlignment(Qt.AlignTop)
    #     self.main_layout.setContentsMargins(2, 2, 2, 2)
    #     self.main_layout.setSpacing(2)
    #     self.setLayout(self.main_layout)
    #
    #     self.refresh_btn = QPushButton('Reload')
    #     self.refresh_btn.setIcon(resource.icon('refresh'))
    #     self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
    #     self.main_layout.addWidget(self.refresh_btn)
    #
    #     self.main_layout.addWidget(splitters.Splitter(self.ExportType))
    #
    #     self.grid_layout = QGridLayout()
    #     self.grid_layout.setSpacing(2)
    #     self.grid_layout.setContentsMargins(0, 0, 0, 0)
    #     self.main_layout.addLayout(self.grid_layout)
    #
    #     scroll_widget = QWidget()
    #     scroll_area = QScrollArea()
    #     scroll_area.setWidgetResizable(True)
    #     scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
    #     scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    #     scroll_area.setWidget(scroll_widget)
    #
    #     self.exporter_layout = QVBoxLayout()
    #     self.exporter_layout.setContentsMargins(1, 1, 1, 1)
    #     self.exporter_layout.setSpacing(0)
    #     self.exporter_layout.addStretch()
    #     scroll_widget.setLayout(self.exporter_layout)
    #     self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)
    #
    # def setup_signals(self):
    #     self.refresh_btn.clicked.connect(self._on_refresh_exporter)
    #
    # def init_ui(self):
    #     pass
    #
    # def all_widgets(self):
    #     all_widgets = list()
    #     while self.exporter_layout.count():
    #         child = self.exporter_layout.takeAt(0)
    #         if child.widget() is not None:
    #             all_widgets.append(child.widget())
    #
    #     return all_widgets
    #
    # def append_widget(self, asset):
    #     self.widgets.append(asset)
    #     self.exporter_layout.insertWidget(0, asset)
    #
    # def remove_widget(self, asset):
    #     pass
    #
    # def refresh_exporter(self):
    #     self._on_refresh_exporter()
    #
    # def clear_exporter(self):
    #     del self.widgets[:]
    #     while self.exporter_layout.count():
    #         child = self.exporter_layout.takeAt(0)
    #         if child.widget() is not None:
    #             child.widget().deleteLater()
    #
    #     self.exporter_layout.setSpacing(0)
    #     self.exporter_layout.addStretch()
    #
    # def _on_refresh_exporter(self):
    #     self.widget_tree = collections.defaultdict(list)
    #     self.clear_exporter()
    #     self.init_ui()
    #     self.refresh.emit()
