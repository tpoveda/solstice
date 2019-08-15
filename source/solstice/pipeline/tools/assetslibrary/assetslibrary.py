#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow artists to interact with Artella functionality inside DCCS in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDccLib as tp

import artellapipe
from artellapipe.gui import window, button
from artellapipe.tools.assetslibrary import assetslibrary

from solstice.core import defines


class SolsticeAssetsLibraryWidget(assetslibrary.ArtellaAssetsLibraryWidget, object):

    name = 'SolsticeAssetsLibrary'
    title = 'Solstice - Assets Viewer'

    def __init__(self, project, parent=None):
        super(SolsticeAssetsLibraryWidget, self).__init__(project=project, parent=parent)

        self._update_assets_status()

    def _update_assets_status(self):
        """
        Internal function that checks asset availability an enables sync button if necessary
        """

        for i in range(self._assets_viewer.rowCount()):
            for j in range(self._assets_viewer.columnCount()):
                item = self._assets_viewer.cellWidget(i, j)
                if not item:
                    continue
                asset_widget = item.containedWidget
                rig_file_type = asset_widget.asset.get_file_type(defines.SOLSTICE_RIG_ASSET_TYPE)
                if rig_file_type:
                    published_path = rig_file_type.get_latest_local_published_path()
                    if published_path and os.path.isfile(published_path):
                        continue
                self._create_sync_button(item)

    def _create_sync_button(self, item):
        """
        Internal function that creates a sync button in the given item
        :param item: ArtellaAssetWidget
        """

        sync_icon = artellapipe.solstice.resource.icon('sync')
        sync_hover_icon = artellapipe.solstice.resource.icon('sync_hover')
        sync_btn = button.IconButton(icon=sync_icon, icon_hover=sync_hover_icon, icon_min_size=50)
        sync_btn.setIconSize(QSize(50, 50))
        sync_btn.move(item.width() * 0.5 - sync_btn.width() * 0.5, item.height() * 0.5 - sync_btn.height() * 0.5)
        sync_btn.setParent(item.containedWidget)

        not_published_pixmap = artellapipe.solstice.resource.pixmap('asset_not_published')
        not_published_lbl = QLabel()
        not_published_lbl.move(9, 9)
        not_published_lbl.setFixedSize(65, 65)
        not_published_lbl.setPixmap(not_published_pixmap)
        not_published_lbl.setParent(item.containedWidget)

        asset_widget = item.containedWidget
        sync_btn.clicked.connect(partial(asset_widget.asset.sync_latest_published_files, None, True))


class SolsticeAssetsLibrary(assetslibrary.ArtellaAssetsLibrary, object):

    LIBRARY_WIDGET = SolsticeAssetsLibraryWidget

    def __init__(self, project, parent=None):
        super(SolsticeAssetsLibrary, self).__init__(project=project, parent=parent)


def run():
    if tp.is_maya():
        win = window.dock_window(project=artellapipe.solstice, window_class=SolsticeAssetsLibraryWidget)
        return win
    else:
        win = SolsticeAssetsLibrary(project=artellapipe.solstice)
        win.show()
        return win
