#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetbrowser.py
# by Tomas Poveda
# Module that contains a QWidget to browse assets
# The browser can be based on real folder structure or JSON dict folder
# structure
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *

from resources import solstice_resource


class AssetBrowser(QWidget, object):
    def __init__(self, title='Asset Browser', parent=None):

        selection_changed = Signal()
        item_clicked = Signal()
        list_modified = Signal()

        super(AssetBrowser, self).__init__(parent=parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        asset_browser_header = solstice_resource.gui('browser_header')
        asset_browser_header.title.setText(title)
        main_layout.addWidget(asset_browser_header)
