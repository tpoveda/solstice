#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that implements mixin for Export List Tree Widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.tools.shotexporter.widgets import exportlistviewmixin


class ExportListTreeWidget(exportlistviewmixin.ExporterItemViewMixin, QTreeWidget):
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        exportlistviewmixin.ExporterItemViewMixin.__init__(self)

        self._header_labels = list()
        self._hidden_columns = dict()

        self.setAutoScroll(False)
        self.setMouseTracking(True)
        self.setSortingEnabled(False)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        header = self.header()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_show_header_menu)

    def _on_show_header_menu(self):
        pass