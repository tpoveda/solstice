#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to reference/import Solstice Assets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import weakref
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.core import assetviewer
from solstice.pipeline.gui import window, buttons
from solstice.pipeline.utils import qtutils
from solstice.pipeline.resources import resource

global solstice_asset_viewer_window


class SolsticeAssetViewer(QWidget, object):

    name = 'SolsticeAssetViewer'
    title = 'Solstice Tools - Asset Viewer'
    version = '1.0'

    instances = list()

    def __init__(self, parent=None):
        if parent is None:
            parent = sys.solstice.dcc.get_main_window()
        super(SolsticeAssetViewer, self).__init__(parent=parent)

        if sp.is_maya():
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

        if sp.is_maya():
            self.parent().layout().addLayout(self.main_layout)
        else:
            self.setLayout(self.main_layout)

        self._asset_viewer = assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=self.update_asset_info,
            parent=self,
            column_count=2,
            show_only_published_assets=True
        )

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)
        top_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(top_layout)

        # refresh_btn = solstice_buttons.IconButton(icon_name='refresh', icon_hover='refresh_hover')
        # top_layout.addWidget(refresh_btn)
        # top_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

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
        top_layout.addLayout(categories_menu_layout)

        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self._asset_viewer)

        import_types_layout = QHBoxLayout()
        import_types_layout.setContentsMargins(0, 0, 0, 0)
        import_types_layout.setSpacing(0)
        import_types_layout.setAlignment(Qt.AlignTop)
        self._import_type_buttons = QButtonGroup(self)
        self._import_type_buttons.setExclusive(True)
        self.rig_btn = QPushButton('Rig')
        self.alembic_btn = QPushButton('Alembic')
        self.standin_btn = QPushButton('Standin')
        self.rig_btn.setCheckable(True)
        self.alembic_btn.setCheckable(True)
        self.standin_btn.setCheckable(True)
        self._import_type_buttons.addButton(self.rig_btn)
        self._import_type_buttons.addButton(self.alembic_btn)
        self._import_type_buttons.addButton(self.standin_btn)
        import_types_layout.addWidget(self.rig_btn)
        import_types_layout.addWidget(self.alembic_btn)
        import_types_layout.addWidget(self.standin_btn)
        self.main_layout.addLayout(import_types_layout)
        self.alembic_btn.setChecked(True)

        self._update_asset_status()

    def update_asset_info(self, asset=None, check_published_info=None, check_working_info=None, check_lock_info=None):
        if self.alembic_btn.isChecked():
            asset.reference_alembic_file()
        elif self.rig_btn.isChecked():
            asset.reference_asset_file()
        elif self.standin_btn.isChecked():
            asset.import_standin_file()

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)

    def _create_sync_btn(self, item):
        sync_btn = buttons.IconButton(icon_name='sync', icon_hover='sync_hover', icon_min_size=50)
        sync_btn.setIconSize(QSize(50, 50))
        sync_btn.move(item.width() * 0.5 - sync_btn.width() * 0.5, item.height() * 0.5 - sync_btn.height() * 0.5)
        sync_btn.setParent(item.containedWidget)

        not_published_pixmap = resource.pixmap('not_published', category='icons')
        not_published_lbl = QLabel()
        not_published_lbl.move(9, 9)
        not_published_lbl.setFixedSize(65, 65)
        not_published_lbl.setPixmap(not_published_pixmap)
        not_published_lbl.setParent(item.containedWidget)

        asset = item.containedWidget
        sync_btn.clicked.connect(partial(asset.sync, 'all', 'all', True))

    def _update_asset_status(self):
        # Store current items
        for i in range(self._asset_viewer.rowCount()):
            for j in range(self._asset_viewer.columnCount()):
                item = self._asset_viewer.cellWidget(i, j)
                if not item:
                    continue
                asset = item.containedWidget
                asset_name = asset.name + '.ma'
                local_max_versions = asset.get_max_local_versions()
                if local_max_versions['model']:
                    published_path = os.path.join(asset._asset_path, local_max_versions['model'][1], 'model', asset_name)
                    if not os.path.isfile(published_path):
                        item.setEnabled(False)
                        self._create_sync_btn(item)
                else:
                    # item.setEnabled(False)
                    self._create_sync_btn(item)


class SolsticeAssetLibraryWindow(window.Window, object):

    name = 'SolsticeAssetBuilder'
    title = 'Solstice Tools - Solstice Asset Library'
    version = '1.1'

    def __init__(self):
        super(SolsticeAssetLibraryWindow, self).__init__()

    def custom_ui(self):
        super(SolsticeAssetLibraryWindow, self).custom_ui()

        self.set_logo('solstice_assetbuilder_logo')
        self.resize(150, 800)

        self.viewer_widget = SolsticeAssetViewer()
        self.main_layout.addWidget(self.viewer_widget)


def run():
    if sp.is_maya():
        qtutils.dock_window(SolsticeAssetViewer)
    else:
        win = SolsticeAssetLibraryWindow()
        win.show()
        return win
