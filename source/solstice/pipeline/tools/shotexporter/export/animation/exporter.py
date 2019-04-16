#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for animation files
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
from solstice.pipeline.tools.shotexporter.export.animation import exportlist, propertieslist


class AnimationExporter(QWidget, object):
    def __init__(self, parent=None):
        super(AnimationExporter, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.exporter_list = exportlist.AnimationExportList()
        self.anims_list = propertieslist.AnimationPropertiesWidget()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        main_splitter.addWidget(self.exporter_list)
        main_splitter.addWidget(self.anims_list)

        self.main_layout.addLayout(splitters.SplitterLayout())

        self.save_btn = QPushButton('SAVE ANIMATIONS')
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
            self.anims_list.update_attributes(asset_widget)
        else:
            sp.logger.warning('Impossible to update properties because object {} does not exists!'.format(asset_widget.asset))
            self.anims_list.clear_properties()

    def _on_clear_properties(self):
        self.anims_list.clear_properties()

    def _on_save(self):
        if not sp.is_maya():
            sp.logger.warning('Shot Export only works for Maya!')
            return

        import maya.cmds as cmds

        anim_file = sp.dcc.save_file_dialog(title='Animation File', start_directory=sp.get_solstice_project_path(), pattern='Animation Files (*.anim)')
        print(anim_file)
        if not anim_file:
            return

        anim_info = dict()
        anim_info['data_version'] = sp.DataVersions.ANIM
        anim_info['exporter_version'] = shotexporter.ShotExporter.version
        anim_info['anims'] = dict()
        for w in self.exporter_list.all_widgets():
            abc_files = w.asset.get_alembic_files()
            if not abc_files:
                sp.logger.warning('Skipping {} because Alembic File does not exists!'.format(w.asset.name))
                continue
            abc_file = sp.dcc.get_attribute_value(node=w.abc_node, attribute_name='abc_File')
            if not os.path.isfile(abc_file):
                sp.logger.warning('Skipping {} because Alembic File {} does not exists!'.format(w.asset.name))
                continue
            abc_file = os.path.relpath(abc_file, sp.get_solstice_project_path())
            if not abc_file:
                sp.logger.warning('Skipping {} because Alembic File {} is not located in Soltice Project path!'.format(w.asset.name))
                continue
            anim_name = w.asset.name
            anim_uuid = cmds.ls(anim_name, uuid=True)[0]
            anim_info['anims'][anim_uuid] = dict()
            anim_info['anims'][anim_uuid]['name'] = anim_name
            anim_info['anims'][anim_uuid]['path'] = abc_file
            anim_info['anims'][anim_uuid]['attrs'] = dict()
            anim_info['anims'][anim_uuid]['abc_attrs'] = dict()
            anim_info['anims'][anim_uuid]['overrides'] = dict()
            for attr, flag in w.attrs.items():
                if not flag and attr not in defines.MUST_ATTRS:
                    continue
                attr_value = sp.dcc.get_attribute_value(node=anim_name, attribute_name=attr)
                anim_info['anims'][anim_uuid]['attrs'][attr] = attr_value
            for attr, flag in w.abc_attrs.items():
                if not flag and attr not in defines.ABC_ATTRS:
                    continue
                attr_value = sp.dcc.get_attribute_value(node=w.abc_node, attribute_name=attr)
                anim_info['anims'][anim_uuid]['abc_attrs'][attr] = attr_value

        try:
            with open(anim_file, 'w') as f:
                json.dump(anim_info, f)
        except Exception as e:
            sp.logger.error(str(e))
