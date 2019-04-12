#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shotassembler.py
# by Tomas Poveda
# Tool to load shot elements
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters


class ShotAssets(QWidget, object):

    ASSETS = {}

    def __init__(self, parent=None):
        super(ShotAssets, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.add_btn = QPushButton('Add Asset')
        self.main_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.assets_menu = QMenu()
        self.add_btn.setMenu(self.assets_menu)

        self.update_menu()

        list = QListWidget()
        self.main_layout.addWidget(list)

    def update_menu(self):
        for asset in ['Layout', 'Animation', 'FX']:
            self.assets_menu.addAction(asset)


class ShotHierarchy(QWidget, object):
    def __init__(self, parent=None):
        super(ShotHierarchy, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        list = QListWidget()
        self.main_layout.addWidget(list)


class AssetProperties(QWidget, object):
    def __init__(self, parent=None):
        super(AssetProperties, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        list = QListWidget()
        self.main_layout.addWidget(list)


class ShotOverrides(QWidget, object):
    def __init__(self, parent=None):
        super(ShotOverrides, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        list = QListWidget()
        self.main_layout.addWidget(list)


class ShotAssembler(solstice_windows.Window, object):
    name = 'SolsticeShotAssembler'
    title = 'Solstice Tools - Shot Assembler'
    version = '1.0'

    def __init__(self):
        super(ShotAssembler, self).__init__()

    def custom_ui(self):
        super(ShotAssembler, self).custom_ui()

        # self.set_logo('solstice_standinmanager_logo')

        self.resize(900, 850)

        self.main_layout.setAlignment(Qt.AlignTop)

        # Menu bar
        menubar_widget = QWidget()
        menubar_layout = QVBoxLayout()
        menubar_widget.setLayout(menubar_layout)
        menubar = QMenuBar()
        file_menu = menubar.addMenu('File')
        self.load_action = QAction('Load', menubar_widget)
        file_menu.addAction(self.load_action)
        menubar_layout.addWidget(menubar)
        self.main_layout.addWidget(menubar_widget)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        self.dock_window = solstice_windows.DockWindow(use_scroll=True)
        self.dock_window.centralWidget().show()
        self.main_layout.addWidget(self.dock_window)

        self.shot_hierarchy = ShotHierarchy()
        self.shot_assets = ShotAssets()
        self.asset_props = AssetProperties()
        self.shot_overrides = ShotOverrides()

        self.dock_window.main_layout.addWidget(self.shot_hierarchy)
        self.asset_props_dock = self.dock_window.add_dock(widget=self.asset_props, name='Properties', area=Qt.RightDockWidgetArea)
        self.shot_overrides_dock = self.dock_window.add_dock(widget=self.asset_props, name='Overrides', area=Qt.RightDockWidgetArea)
        self.shot_assets_dock = self.dock_window.add_dock(widget=self.shot_assets, name='Assets', tabify=False, area=Qt.LeftDockWidgetArea)

        self.generate_btn = QPushButton('GENERATE SHOT')
        self.generate_btn.setMinimumHeight(30)
        self.generate_btn.setMinimumWidth(80)
        generate_layout = QHBoxLayout()
        generate_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        generate_layout.addWidget(self.generate_btn)
        generate_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addLayout(generate_layout)





def run():
    win = ShotAssembler().show()
    return win
