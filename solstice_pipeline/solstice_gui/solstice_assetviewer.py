#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetviewer.py
# by Tomas Poveda
# Widgets that shows all the items of a specific directory
# ______________________________________________________________________
# ==================================================================="""

import os

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_grid
import solstice_asset
from solstice_utils import solstice_python_utils as utils


class AssetViewer(solstice_grid.GridWidget, object):
    def __init__(self, assets_path, parent=None):
        super(AssetViewer, self).__init__(parent=parent)

        self._assets_paths = assets_path

        self._items = dict()

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setShowGrid(False)
        self.setColumnCount(4)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        self.update_items()

    @Slot()
    def add_asset(self, asset_widget):
        row, col = self.first_empty_cell()
        self.addWidget(row, col, asset_widget)
        self.resizeRowsToContents()

    @property
    def assets_path(self):
        return self._assets_paths

    @assets_path.setter
    def assets_path(self, assets_path):
        if os.path.exists(assets_path):
            self._assets_paths = assets_path
            self.update_items()

    def update_items(self):
        if os.path.exists(self._assets_paths):
            for root, dirs, files in os.walk(self._assets_paths):
                for f in files:
                    if f.endswith('.ma'):
                        print('holaaa')
                        print(root)
                        new_asset_path = os.path.join(root, f)
                        asset_folders_path = utils.get_folders_from_path(new_asset_path)
                        for category in ['All', 'BackgroundElements', 'Characters', 'Props', 'Sets']:
                            if category in asset_folders_path:
                                new_asset = solstice_asset.AssetWidget(
                                    asset_name=os.path.splitext(f)[0],
                                    asset_path=new_asset_path,
                                    asset_category=category
                                )
                                self.add_asset(new_asset)