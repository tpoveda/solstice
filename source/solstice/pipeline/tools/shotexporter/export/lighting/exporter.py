#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for lighting files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.gui import splitters


class LightingExporter(QWidget, object):
    def __init__(self, parent=None):
        super(LightingExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.reload_btn = QPushButton('RELOAD')
        self.main_layout.addWidget(self.reload_btn)
        self.main_layout.addLayout(splitters.SplitterLayout())

    def refresh(self):
        pass
