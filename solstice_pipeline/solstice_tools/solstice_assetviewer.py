#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetviewer.py
# by Tomas Poveda
# ______________________________________________________________________
# ==================================================================="""

import os
import weakref
from functools import partial

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_assetviewer, solstice_splitters, solstice_buttons, solstice_asset
from solstice_pipeline.solstice_utils import solstice_qt_utils, solstice_maya_utils
from solstice_pipeline.resources import solstice_resource

reload(solstice_asset)

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
            column_count=2,
            show_only_published_assets=True
        )

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)
        top_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(top_layout)

        refresh_btn = solstice_buttons.IconButton(icon_name='refresh', icon_hover='refresh_hover')
        top_layout.addWidget(refresh_btn)
        top_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

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
        self.rig_btn.setCheckable(True)
        self.alembic_btn.setCheckable(True)
        self._import_type_buttons.addButton(self.rig_btn)
        self._import_type_buttons.addButton(self.alembic_btn)
        import_types_layout.addWidget(self.rig_btn)
        import_types_layout.addWidget(self.alembic_btn)
        self.main_layout.addLayout(import_types_layout)
        self.alembic_btn.setChecked(True)

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
                    print(published_path)
                    if not os.path.isfile(published_path):
                        item.setEnabled(False)
                        self._create_sync_btn(item)
                else:
                    # item.setEnabled(False)
                    self._create_sync_btn(item)

    def update_asset_info(self, asset=None, check_published_info=None, check_working_info=None, check_lock_info=None):
        if self.alembic_btn.isChecked():
            asset.reference_alembic_file()
        elif self.rig_btn.isChecked():
            asset.reference_asset_file()

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)

    def _create_sync_btn(self, item):
        sync_btn = solstice_buttons.IconButton(icon_name='sync', icon_hover='sync_hover', icon_min_size=50)
        sync_btn.setIconSize(QSize(50, 50))
        sync_btn.move(item.width() * 0.5 - sync_btn.width() * 0.5, item.height() * 0.5 - sync_btn.height() * 0.5)
        sync_btn.setParent(item.containedWidget)

        not_published_pixmap = solstice_resource.pixmap('not_published', category='icons')
        print(not_published_pixmap)
        not_published_lbl = QLabel()
        not_published_lbl.move(9, 9)
        not_published_lbl.setFixedSize(65, 65)
        not_published_lbl.setPixmap(not_published_pixmap)
        not_published_lbl.setParent(item.containedWidget)

        asset = item.containedWidget
        sync_btn.clicked.connect(partial(asset.sync, 'all', 'all', True))



def run():
    solstice_qt_utils.dock_window(SolsticeAssetViewer)
