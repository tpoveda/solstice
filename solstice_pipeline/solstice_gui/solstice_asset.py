#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_asset.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

import os

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *


class ArtellaAsset(object):
    def __init__(self):
        pass


class AssetWidget(QWidget, object):
    def __init__(self, asset_name='New_Asset', asset_path=None, asset_image=None, asset_category=None, parent=None):
        super(AssetWidget, self).__init__(parent=parent)

        self._name = asset_name
        self._asset_path = asset_path
        self._category = asset_category

        if asset_image == '' or asset_image is None:
            self._image = None
        else:
            self._image = asset_image.encode('utf-8')
        if self._image is None:
            self._image = QImage(os.path.join(asset_path, 'icon.png'))

        self.setMaximumWidth(160)
        self.setMaximumHeight(200)

        print(asset_path)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)
        self.setLayout(main_layout)

        self._asset_btn = QPushButton('', self)
        if self._image:
            self._asset_btn.setIcon(QPixmap.fromImage(self._image))
            self._asset_btn.setIconSize(QSize(150, 150))
        self._asset_label = QLabel(self._name)
        self._asset_label.setAlignment(Qt.AlignCenter)
        asset_menu_layout = QHBoxLayout()
        asset_menu_layout.setContentsMargins(2, 2, 2, 2)
        asset_menu_layout.setSpacing(2)
        self._asset_menu_widget = QWidget()
        self._asset_menu_widget.setLayout(asset_menu_layout)
        for widget in [self._asset_btn, self._asset_menu_widget, self._asset_label]:
            main_layout.addWidget(widget)

        instance_btn = QPushButton('I')
        asset_menu_layout.addWidget(instance_btn)

        self._asset_btn.clicked.connect(self.toggle_asset_menu)

        self._asset_menu_widget.setVisible(False)

    def toggle_asset_menu(self):
        self._asset_menu_widget.setVisible(not self._asset_menu_widget.isVisible())