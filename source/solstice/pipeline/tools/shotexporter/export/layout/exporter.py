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

import solstice.pipeline as sp
from solstice.pipeline.gui import messagebox

from solstice.pipeline.tools.shotexporter.core import defines, exporter as base_exporter
from solstice.pipeline.tools.shotexporter.export.layout import exportlist, propertieswidget

if sp.is_maya():
    import maya.cmds as cmds

reload(exportlist)
reload(messagebox)


class LayoutExporter(base_exporter.BaseExporter, object):
    def __init__(self, parent=None):
        super(LayoutExporter, self).__init__(parent=parent)

    def get_exporter_list_widget(self):
        """
        Overrides base BaseExporter get_exporter_list_widget() function
        Returns exporter list widget used by the exporter
        :return: exporter.LayoutExportList
        """

        return exportlist.LayoutExportList()

    def get_exporter_properties_widget(self):
        """
        Overrides base BaseExporter get_exporter_properties_widget() function
        Returns exporter properties widget used by the exporter
        :return: exporter.LayoutPropertiesWidget
        """

        return propertieswidget.LayoutPropertiesWidget()

    def get_export_button_text(self):
        """
        Overrides base BaseExporter get_export_button_text() function
        Returns exporter button text
        :return: str
        """

        return 'SAVE LAYOUT'

    def _on_save(self):

        from solstice.pipeline.tools.shotexporter import shotexporter

        if not sp.is_maya():
            sp.logger.warning('Shot Export only works for Maya!')
            return

        self.show_layout_capture_dialog()

        # scene_name = sp.dcc.scene_name()
        # if not scene_name:
        #     scene_name = 'undefined'
        # else:
        #     scene_name = os.path.basename(scene_name)
        #
        # export_path = sp.dcc.select_folder_dialog(title='Select Layout Export Path', start_directory=sp.get_solstice_project_path())
        # if not export_path:
        #     return
        #
        # export_path = os.path.normpath(os.path.join(export_path, scene_name+'.'+sp.DataExtensions.LAYOUT))
        #
        # layout_info = dict()
        # layout_info['data_version'] = sp.DataVersions.LAYOUT
        # layout_info['exporter_version'] = shotexporter.ShotExporter.version
        # layout_info['assets'] = dict()
        # for i in range(self.export_list.count()):
        #     asset = self.export_list.asset_at(i)
        #     asset_name = asset.name
        #     asset_uuid = cmds.ls(asset_name, uuid=True)[0]
        #     asset_path = os.path.relpath(asset.path, sp.get_solstice_project_path())
        #
        #     layout_info['assets'][asset_uuid] = dict()
        #     layout_info['assets'][asset_uuid]['name'] = asset_name
        #     layout_info['assets'][asset_uuid]['path'] = asset_path
        #     layout_info['assets'][asset_uuid]['attrs'] = dict()
        #     layout_info['assets'][asset_uuid]['overrides'] = list()
        #     for attr, flag in asset.attrs.items():
        #         if not flag and attr not in defines.MUST_ATTRS:
        #             continue
        #         attr_value = sp.dcc.get_attribute_value(node=asset_name, attribute_name=attr)
        #         layout_info['assets'][asset_uuid]['attrs'][attr] = attr_value
        #
        # try:
        #     with open(export_path, 'w') as f:
        #         json.dump(layout_info, f)
        # except Exception as e:
        #     sp.logger.error(str(e))

    def show_layout_capture_dialog(self):
        title = 'Create Layout Thumbnail'
        text = 'Would you like to capture Layout thumbnail?'
        buttons = QMessageBox.Yes | QMessageBox.Ignore | QMessageBox.Cancel

        btn = messagebox.MessageBox.question(self, title, text, buttons=buttons)

        if btn == QMessageBox.Yes:
            self.thumbnail_capture()

        return btn

    def thumbnail_capture(self):
        path = sp.temp_path('sequence', 'thumbnail.jpg')
        print(path)

