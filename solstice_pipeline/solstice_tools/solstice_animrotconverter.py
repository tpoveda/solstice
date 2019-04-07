
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_animrotconverter.py
# by Tomas Poveda
# Tool to change rotation order of objects while preserving animation
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows
from solstice_pipeline.solstice_utils import solstice_maya_utils

from solstice_pipeline.externals.ml_tools import ml_convertRotationOrder


class SolsticeRotOrder(solstice_windows.Window, object):

    name = 'SolsticeRotOrder'
    title = 'Solstice Tools - Solstice Rotation Order Converter'
    version = '1.0'

    def __init__(self):
        super(SolsticeRotOrder, self).__init__()

        ml_convertRotationOrder.ui()

        maya_main_window = solstice_maya_utils.get_maya_window()
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