#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_datamanager.py
# by Tomas Poveda
# Tool to manage Solstice Data files
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

from solstice_pipeline.solstice_gui import solstice_windows


class DataManagerTool(solstice_windows.Window, object):

    name = 'SolsticeDataManager'
    title = 'Solstice Tools - Dependencies Manager'
    version = '1.0'

    def __init__(self):
        super(DataManager, self).__init__()

    def custom_ui(self):
        super(DataManager, self).custom_ui()

        self.set_logo('solstice_dependenciesmanager_logo')

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        layout_data = LayoutDataManager()
        anim_data = AnimDataManager()
        lighting_data = LightingDataManager()

        for manager in [layout_data, anim_data, lighting_data]:
            self.tabs.addTab(manager, manager.title)


class DataManager(QWidget, object):
    def __init__(self, title='Data', parent=None):
        super(DataManager, self).__init__(parent)

        self.custom_ui()
        self.title = title

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.data_tree = QTreeView()
        self.main_layout.addWidget(self.data_tree)


class AnimDataManager(DataManager, object):
    def __init__(self, parent=None):
        super(AnimDataManager, self).__init__(title='Animation', parent=parent)


class LayoutDataManager(DataManager, object):
    def __init__(self, parent=None):
        super(LayoutDataManager, self).__init__(title='Layout', parent=parent)


class LightingDataManager(DataManager, object):
    def __init__(self, parent=None):
        super(LightingDataManager, self).__init__(title='Lighting', parent=parent)


def run():
    DataManager().show()

