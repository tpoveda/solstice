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
import time
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_pipeline as sp
import solstice_grid
import solstice_asset
from solstice_utils import solstice_python_utils as utils
from solstice_gui import solstice_sync_dialog


class AssetViewer(solstice_grid.GridWidget, object):
    def __init__(self, assets_path, item_prsesed_callback, simple_assets=False, checkable_assets=False, show_only_published_assets=False, parent=None):
        super(AssetViewer, self).__init__(parent=parent)

        self._assets_paths = assets_path
        self._simple_assets = simple_assets
        self._checkable_assets = checkable_assets
        self._items = dict()
        self._item_pressed_callback = item_prsesed_callback
        self._show_only_published_assets = show_only_published_assets

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

    def change_category(self, category='All'):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.cellWidget(i, j)
                if not item:
                    continue
                widget = item.containedWidget
                if category == 'All':
                    widget.setVisible(True)
                else:
                    if widget.category == category:
                        widget.setVisible(True)
                    else:
                        widget.setVisible(False)

    def update_items(self, update=True):
        """
        Updates the list of items in the Asset Viewer
        :param category: str, category of the items we want to add ('All, 'Props', 'Characters', 'BackgroundElements')
        :param update: bool, If True, we will get the info of the missing widgets from Artella
        :return:
        """

        self.clear()

        # TODO: Add list of ignored paths to avoid checking for JSON on paths that never will need JSON such as PIPELINE

        if os.path.exists(self._assets_paths):
            for root, dirs, files in os.walk(self._assets_paths):
                if dirs and '__working__' in dirs:
                    asset_path = root
                    asset_name = os.path.basename(root)
                    asset_data_file = os.path.join(asset_path, '__working__', 'data.json')
                    if not os.path.isfile(asset_data_file):
                        if update:
                            solstice_sync_dialog.SolsticeSyncFile(files=[asset_data_file]).sync()
                            if not os.path.isfile(asset_data_file):
                                sp.logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                                continue
                        else:
                            continue

                    asset_category = utils.camel_case_to_string(os.path.basename(os.path.dirname(asset_path)))
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
                        simple_mode=self._simple_assets,
                        checkable=self._checkable_assets
                    )
                    if self._show_only_published_assets:
                        if not new_asset.is_published():
                            new_asset.setVisible(False)
                    if self._item_pressed_callback:
                        new_asset._asset_btn.clicked.connect(partial(self._item_pressed_callback, new_asset))
                    self.add_asset(new_asset)
                        #
                        # if asset_category == category:


                        # if category == 'All':
                        #     asset_data = utils.read_json(asset_data_file)
                        #     new_asset = solstice_asset.AssetWidget(
                        #         name=asset_name,
                        #         path=asset_path,
                        #         category=asset_category,
                        #         icon=asset_data['asset']['icon'],
                        #         icon_format=asset_data['asset']['icon_format'],
                        #         preview=asset_data['asset']['preview'],
                        #         preview_format=asset_data['asset']['preview_format'],
                        #         description=asset_data['asset']['description'],
                        #         simple_mode=self._simple_assets,
                        #         checkable=self._checkable_assets
                        #     )
                        #     if self._show_only_published_assets:
                        #         if not new_asset.is_published():
                        #             new_asset.setVisible(False)
                        #     if self._item_pressed_callback:
                        #         new_asset._asset_btn.clicked.connect(partial(self._item_pressed_callback, new_asset))
                        #     self.add_asset(new_asset)
                        # else:


