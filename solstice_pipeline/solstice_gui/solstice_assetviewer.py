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
from Qt.QtGui import *

import solstice_pipeline as sp
import solstice_grid
import solstice_asset
from solstice_utils import solstice_python_utils as utils
from solstice_gui import solstice_sync_dialog


class AssetViewer(solstice_grid.GridWidget, object):

    IGNORED_PATHS = ['PIPELINE', 'lighting', 'Light Rigs', 'S_CH_02_summer_scripts']

    def __init__(self, assets_path, item_pressed_callback, simple_assets=False, checkable_assets=False, show_only_published_assets=False, parent=None):
        super(AssetViewer, self).__init__(parent=parent)


        self._assets_paths = assets_path
        self._simple_assets = simple_assets
        self._checkable_assets = checkable_assets
        self._items = dict()
        self._item_pressed_callback = item_pressed_callback
        self._show_only_published_assets = show_only_published_assets

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setColumnCount(4)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.update_items(False)
        # self.update_items()       # Uncomment later

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

        # First we store all the current assets
        assets = []
        # for i in range(self.rowCount()):
        #     assets.append(list())
        #     for j in range(self.columnCount()):
        #         item = self.cellWidget(i, j)
        #         if not item:
        #             continue
        #         assets[i].append(item)

        # Store current items
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.cellWidget(i, j)
                if not item:
                    continue
                assets.append(item.containedWidget)
        self.clear()

        new_assets = list()
        for asset in reversed(assets):
            if category == 'All':
                asset.setVisible(True)
                new_assets.insert(0, asset)
            else:
                if asset.category == category:
                    asset.setVisible(True)
                    new_assets.insert(0, asset)
                else:
                    asset.setVisible(False)
                    new_assets.append(asset)

        for asset in new_assets:
            self.add_asset(asset)


        # self.clear()
        #
        # for



        # for i in range(self.rowCount()):
        #     for j in range(self.columnCount()):
        #         item = self.cellWidget(i, j)
        #         if not item:
        #             continue
        #         widget = item.containedWidget
        #         if category == 'All':
        #             widget.setVisible(True)
        #         else:
        #             if widget.category == category:
        #                 widget.setVisible(True)
        #             else:
        #                 widget.setVisible(False)

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
                    is_ignored = False
                    for ignored in self.IGNORED_PATHS:
                        if ignored in asset_data_file:
                            is_ignored = True
                            break

                    if not is_ignored:
                        if not os.path.isfile(asset_data_file):
                            if update:
                                solstice_sync_dialog.SolsticeSyncFile(files=[asset_data_file]).sync()
                                if not os.path.isfile(asset_data_file):
                                    sp.logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                                    continue
                            else:
                                if not os.path.isfile(asset_data_file):
                                    sp.logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                                continue

                        asset_category = utils.camel_case_to_string(os.path.basename(os.path.dirname(asset_path)))
                        asset_data = utils.read_json(asset_data_file)

                        new_asset = solstice_asset.generate_asset_widget_by_category(
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

                        # We connect this signal to allow Pipelinizer Tool update its asset info widget after syncronizing
                        # This is a very bad way but it works for now!
                        try:
                            new_asset.sync_finished.connect(partial(self.parent().update_asset_info, new_asset, True))
                            new_asset.sync_finished.connect(partial(sp.register_asset, new_asset.name))
                        except Exception:
                            pass

                        if not new_asset:
                            sp.logger.debug('Asset Widget for "{0}" was not generated!'.format(asset_name))
                            continue

                        if self._show_only_published_assets:
                            if not new_asset.is_published():
                                new_asset.setVisible(False)
                        if self._item_pressed_callback:
                            new_asset._asset_btn.clicked.connect(partial(self._item_pressed_callback, new_asset))
                        self.add_asset(new_asset)

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


