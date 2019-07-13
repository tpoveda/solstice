#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Widgets that shows all the items of a specific directory
 """

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import grid


class AssetViewer(grid.GridWidget, object):
    def __init__(self, assets_path, item_pressed_callback, simple_assets=False, checkable_assets=False, show_only_published_assets=False, parent=None, column_count=4):
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
        self.setColumnCount(column_count)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.update_items(False)
        # self.update_items()       # Uncomment to sync on startup

    @Slot()
    def add_asset(self, asset_widget):
        if asset_widget is None:
            return

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
        assets = []

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

    def update_items(self, update=True):
        """
        Updates the list of items in the Asset Viewer
        :param update: bool, If True, we will get the info of the missing widgets from Artella
        :return:
        """

        self.clear()

        if self._assets_paths is None or not os.path.exists(self._assets_paths):
            return

        all_assets = sp.find_all_assets(
            assets_path=self._assets_paths,
            update_if_data_not_found=update,
            simple_mode=self._simple_assets,
            as_checkable=self._checkable_assets
        )

        if not all_assets:
            return

        for asset in all_assets:

            if not asset:
                continue

            # ===========================================================================================================
            # TODO: Refactor this piece of awful code
            # We connect this signal to allow Pipelinizer Tool update its asset info widget after syncronizing
            # This is a very bad way but it works for now!
            try:
                asset.syncFinished.connect(partial(self.parent().update_asset_info, asset, True, False, True))
                asset.syncFinished.connect(partial(sp.register_asset, asset.name))
            except Exception:
                pass

            # if self._show_only_published_assets:
            #     if not new_asset.is_published():
            #         continue
            #     else:
            #         sys.solstice.logger.debug('Adding asset: {}'.format(new_asset.name))

            if self._item_pressed_callback:
                asset._asset_btn.clicked.connect(partial(self._item_pressed_callback, asset))
                asset.publishFinished.connect(partial(self._item_pressed_callback, asset, True, True))
                asset.newVersionFinished.connect(partial(self._item_pressed_callback, asset, True, True))
            self.add_asset(asset)


class CategorizedAssetViewer(QWidget, object):
    def __init__(
            self,
            item_pressed_callback=None,
            simple_assets=True,
            checkable_assets=False,
            show_only_published_assets=False,
            parent=None):
        super(CategorizedAssetViewer, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        self._categories_widget.setLayout(categories_layout)

        main_categories_menu_layout = QHBoxLayout()
        main_categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        main_categories_menu_layout.setSpacing(0)
        categories_layout.addLayout(main_categories_menu_layout)

        categories_menu = QWidget()
        categories_menu_layout = QVBoxLayout()
        categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        categories_menu_layout.setSpacing(0)
        categories_menu_layout.setAlignment(Qt.AlignTop)
        categories_menu.setLayout(categories_menu_layout)
        main_categories_menu_layout.addWidget(categories_menu)

        asset_viewer_layout = QVBoxLayout()
        asset_viewer_layout.setContentsMargins(2, 2, 2, 2)
        asset_viewer_layout.setSpacing(2)
        main_categories_menu_layout.addLayout(asset_viewer_layout)

        self._asset_viewer = AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=item_pressed_callback,
            simple_assets=simple_assets,
            checkable_assets=checkable_assets,
            show_only_published_assets=show_only_published_assets,
            column_count=2
        )

        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        asset_viewer_layout.addWidget(self._asset_viewer)

        self._categories_btn_group = QButtonGroup(self)
        self._categories_btn_group.setExclusive(True)
        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            new_btn = QPushButton(category)
            new_btn.toggled.connect(partial(self._change_category, category))
            categories_buttons[category] = new_btn
            categories_buttons[category].setCheckable(True)
            categories_menu_layout.addWidget(new_btn)
            self._categories_btn_group.addButton(new_btn)
        categories_buttons['All'].setChecked(True)

        self.main_layout.addWidget(self._categories_widget)

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)
