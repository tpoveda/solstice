#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetviewer.py
# by Tomas Poveda
# ______________________________________________________________________
# ==================================================================="""

import weakref
from functools import partial

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_assetviewer
from solstice_pipeline.solstice_utils import solstice_qt_utils, solstice_maya_utils

reload(solstice_assetviewer)


global solstice_asset_viewer_window


class SolsticeAssetViewer(QWidget, object):

    name = 'SolsticeAssetViewer'
    title = 'Solstice Tools - Asset Viewer'
    version = '1.0'

    instances = list()

    def __init__(self, parent=solstice_maya_utils.get_maya_window()):
        super(SolsticeAssetViewer, self).__init__(parent=parent)

        SolsticeAssetViewer._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))

        self.custom_ui()
        self.resize(150, 800)

        global solstice_asset_viewer_window
        solstice_asset_viewer_window = self

    @staticmethod
    def _delete_instances():
        for ins in SolsticeAssetViewer.instances:
            try:
                ins.remove_callbacks()
                ins.setParent(None)
                ins.deleteLater()
            except Exception:
                pass

            SolsticeAssetViewer.instances.remove(ins)
            del ins

    def custom_ui(self):

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.parent().layout().addLayout(self.main_layout)

        self._asset_viewer = solstice_assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=self.update_asset_info,
            parent=self,
            column_count=1,
            show_only_published_assets=True
        )

        categories_menu_layout = QHBoxLayout()
        categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        categories_menu_layout.setSpacing(0)
        categories_menu_layout.setAlignment(Qt.AlignTop)
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
        self.main_layout.addLayout(categories_menu_layout)

        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self._asset_viewer)

    def update_asset_info(self, asset=None, check_published_info=None, check_working_info=None, check_lock_info=None):
        asset.reference_asset_file()

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)


def run():
    solstice_qt_utils.dock_window(SolsticeAssetViewer)
