#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shaderviewer.py
# by Tomas Poveda
# Grid widget used to show Solstice Shaders
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtWidgets import *


class ShaderViewer(QGridLayout, object):
    def __init__(self, grid_size=4, parent=None):
        super(ShaderViewer, self).__init__(parent)

        self._grid_size = grid_size
        self.setHorizontalSpacing(0)
        self.setVerticalSpacing(0)

    def add_widget(self, widget):
        row = 0
        col = 0
        while self.itemAtPosition(row, col) is not None:
            if col == self._grid_size:
                row += 1
                col = 0
            else:
                col += 1
        self.addWidget(widget, row, col)