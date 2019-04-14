#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to change rotation order of objects while preserving animation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.ml_tools import ml_convertRotationOrder

from solstice.pipeline.gui import window
from solstice.pipeline.utils import mayautils


class SolsticeRotOrder(window.Window, object):

    name = 'SolsticeRotOrder'
    title = 'Solstice Tools - Solstice Rotation Order Converter'
    version = '1.0'

    def __init__(self):
        super(SolsticeRotOrder, self).__init__()

        ml_convertRotationOrder.ui()

        maya_main_window = mayautils.get_maya_window()
        for child in maya_main_window.children():
            if child.objectName() == 'ml_convertRotationOrder':
                child.setWindowFlags(child.windowFlags() ^ Qt.FramelessWindowHint)
                self.main_layout.addWidget(child)
                return

        self.statusBar().setSizeGripEnabled(False)

    def custom_ui(self):
        super(SolsticeRotOrder, self).custom_ui()


def run():
    win = SolsticeRotOrder().show()
