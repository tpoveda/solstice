#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class for exporter widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.gui import base, splitters, menubar, search
from solstice.pipeline.tools.shotexporter import shotexporter
from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.widgets import exportlist

reload(exportlist)


class BaseExporter(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(BaseExporter, self).__init__(parent=parent)

    def get_exporter_list_widget(self):
        """
        Returns exporter list widget used by the exporter
        Override in child classes
        :return: exporter.BaseExporter
        """

        return exportlist.BaseExportList()

    def custom_ui(self):
        super(BaseExporter, self).custom_ui()

        self._search_widget = search.SearchWidget()
        self._menubar_widget = menubar.MenuBarWidget()
        self._menubar_widget.setStyleSheet('background-color: rgb(35, 35, 35);')
        self.main_layout.addWidget(self._menubar_widget)
        self._menubar_widget.addWidget(self._search_widget)

        self.export_list = self.get_exporter_list_widget()
        self.main_layout.addWidget(self.export_list)

