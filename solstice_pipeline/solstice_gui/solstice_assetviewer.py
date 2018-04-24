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
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_grid
import solstice_asset
from solstice_utils import solstice_python_utils as utils
from solstice_utils import solstice_artella_utils as artella


class AssetViewer(solstice_grid.GridWidget, object):
    def __init__(self, assets_path, update_asset_info_fn, simple_assets=False, parent=None):
        super(AssetViewer, self).__init__(parent=parent)

        self._assets_paths = assets_path
        self._simple_assets = simple_assets
        self._items = dict()
        self._update_asset_info_fn = update_asset_info_fn

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
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

    def update_items(self, category='All', flag=False):
        self.clear()
        if os.path.exists(self._assets_paths):
            for root, dirs, files in os.walk(self._assets_paths):
                if dirs and '__working__' in dirs:
                    asset_path = root
                    asset_name = os.path.basename(root)
                    asset_data_file = os.path.join(asset_path, '__working__', 'data.json')
                    if os.path.isfile(asset_data_file):
                        asset_category = utils.camel_case_to_string(os.path.basename(os.path.dirname(asset_path)))
                        if category == 'All':
                            asset_data = utils.read_json(asset_data_file)
                            new_asset = solstice_asset.AssetWidget(
                                name=asset_name,
                                path=asset_path,
                                category=asset_category,
                                icon=asset_data['asset']['icon'],
                                icon_format=asset_data['asset']['icon_format'],
                                preview=asset_data['asset']['preview'],
                                preview_format=asset_data['asset']['preview_format'],
                                description=asset_data['asset']['description'],
                                simple_mode=self._simple_assets
                            )
                            if self._update_asset_info_fn:
                                new_asset._asset_btn.clicked.connect(partial(self._update_asset_info_fn, new_asset))
                            self.add_asset(new_asset)
                        else:
                            if asset_category == category:
                                asset_data = utils.read_json(asset_data_file)
                                new_asset = solstice_asset.AssetWidget(
                                    name=asset_name,
                                    path=asset_path,
                                    category=asset_category,
                                    icon=asset_data['asset']['icon'],
                                    icon_format=asset_data['asset']['icon_format'],
                                    preview=asset_data['asset']['preview'],
                                    preview_format=asset_data['asset']['preview_format'],
                                    description=asset_data['asset']['description'],
                                    simple_mode=self._simple_assets
                                )
                                if self._update_asset_info_fn:
                                    new_asset._asset_btn.clicked.connect(partial(self._update_asset_info_fn, new_asset))
                                self.add_asset(new_asset)

