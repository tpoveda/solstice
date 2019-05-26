#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used to synchronize all assets to its latest available versions
ç"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from collections import defaultdict

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.gui import window


class AssetOutlinerItem(QWidget, object):
    clicked = Signal(QObject, QEvent)

    def __init__(self, asset, parent=None):
        super(AssetOutlinerItem, self).__init__(parent)

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.asset = asset
        self.parent = parent
        self.name = asset.get_short_name()
        self.block_callbacks = False

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.item_widget = QFrame()
        self.item_layout = QGridLayout()
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_widget.setLayout(self.item_layout)
        self.main_layout.addWidget(self.item_widget)

        self.asset_lbl = QLabel(self.name)
        self.item_layout.addWidget(self.asset_lbl, 0, 3, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

    def setup_signals(self):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self, event)


class AssetOutliner(QWidget, object):
    def __init__(self, parent=None):
        super(AssetOutliner, self).__init__(parent=parent)

        self.widget_tree = defaultdict(list)
        self.widgets = list()
        self.setMouseTracking(True)
        self.custom_ui()
        self.update_ui()

    def custom_ui(self):
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.outliner_layout = QVBoxLayout()
        self.outliner_layout.setContentsMargins(1, 1, 1, 1)
        self.outliner_layout.setSpacing(0)
        self.outliner_layout.addStretch()
        scroll_widget.setLayout(self.outliner_layout)
        self.main_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def update_ui(self):
        assets = sp.get_assets()
        for asset in assets:
            asset_widget = AssetOutlinerItem(asset)
            self.append_widget(asset_widget)

    def append_widget(self, asset):
        self.widgets.append(asset)
        self.outliner_layout.insertWidget(0, asset)


class AssetSyncer(window.Window, object):

    name = 'SolsticeShaderLibrary'
    title = 'Solstice Tools - Asset Syncer'
    version = '1.0'

    def __init__(self):
        super(AssetSyncer, self).__init__()

    def custom_ui(self):
        super(AssetSyncer, self).custom_ui()

        self.set_logo('solstice_shaderlibrary_logo')

        self.resize(400, 600)

        self.outliner = AssetOutliner(self)
        self.main_layout.addWidget(self.outliner)

def run():
    AssetSyncer().show()