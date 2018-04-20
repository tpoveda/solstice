#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_asset.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *


class ArtellaAsset(object):
    def __init__(self):
        pass

class AssetWidget(QWidget, object):
    def __init__(self, asset_name='New_Asset', asset_image=None, parent=None):
        super(AssetWidget, self).__init__(parent=parent)

        self._name = asset_name

        if asset_image == '' or asset_image is None:
            self._image = None
        else:
            self._image = asset_image.encode('utf-8')

        self.setMaximumWidth(160)
        self.setMaximumHeight(200)

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
        for widget in [self._asset_btn, self._asset_label]:
            main_layout.addWidget(widget)