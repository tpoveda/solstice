#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for layout files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.gui import splitters
from solstice.pipeline.tools.shotexporter import shotexporter
from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.export.layout import exportlist, propertieslist


class LayoutExporter(QWidget, object):
    def __init__(self, parent=None):
        super(LayoutExporter, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.exporter_list = exportlist.LayoutExportList()
        self.props_list = propertieslist.LayoutPropertiesWidget()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        main_splitter.addWidget(self.exporter_list)
        main_splitter.addWidget(self.props_list)

        self.main_layout.addLayout(splitters.SplitterLayout())

        self.save_btn = QPushButton('SAVE LAYOUT')
        self.save_btn.setMinimumHeight(30)
        self.save_btn.setMinimumWidth(80)
        save_layout = QHBoxLayout()
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        save_layout.addWidget(self.save_btn)
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addLayout(save_layout)

    def setup_signals(self):
        self.exporter_list.updateProperties.connect(self._on_update_properties)
        self.exporter_list.refresh.connect(self._on_clear_properties)
        self.save_btn.clicked.connect(self._on_save)

    def init_ui(self):
        self.exporter_list.init_ui()

    def refresh(self):
        self.exporter_list.refresh_exporter()

    def _on_update_properties(self, asset_widget):
        if asset_widget and sp.dcc.object_exists(asset_widget.asset.name):
            self.props_list.update_attributes(asset_widget)
        else:
            sp.logger.warning('Impossible to update properties because object {} does not exists!'.format(asset_widget.asset))
            self.props_list.clear_properties()

    def _on_clear_properties(self):
        self.props_list.clear_properties()

    def _on_save(self):
        if not sp.is_maya():
            sp.logger.warning('Shot Export only works for Maya!')
            return

        import maya.cmds as cmds

        scene_name = sp.dcc.scene_name()
        if not scene_name:
            scene_name = 'undefined'
        else:
            scene_name = os.path.basename(scene_name)

        export_path = sp.dcc.select_folder_dialog(title='Select Layout Export Path', start_directory=sp.get_solstice_project_path())
        if not export_path:
            return

        export_path = os.path.join(export_path, scene_name+'.'+sp.DataExtensions.LAYOUT)

        layout_info = dict()
        layout_info['data_version'] = sp.DataVersions.LAYOUT
        layout_info['exporter_version'] = shotexporter.ShotExporter.version
        layout_info['assets'] = dict()
        for w in self.exporter_list.all_widgets():
            asset_name = w.asset.name
            # asset_name = os.path.basename(asset_path)
            asset_uuid = cmds.ls(asset_name, uuid=True)[0]
            asset_path = os.path.relpath(w.asset.asset_path, sp.get_solstice_project_path())
            layout_info['assets'][asset_uuid] = dict()
            layout_info['assets'][asset_uuid]['name'] = asset_name
            layout_info['assets'][asset_uuid]['path'] = asset_path
            layout_info['assets'][asset_uuid]['attrs'] = dict()
            layout_info['assets'][asset_uuid]['overrides'] = list()
            for attr, flag in w.attrs.items():
                if not flag and attr not in defines.MUST_ATTRS:
                    continue
                attr_value = sp.dcc.get_attribute_value(node=asset_name, attribute_name=attr)
                layout_info['assets'][asset_uuid]['attrs'][attr] = attr_value

        try:
            with open(export_path, 'w') as f:
                json.dump(layout_info, f)
        except Exception as e:
            sp.logger.error(str(e))
