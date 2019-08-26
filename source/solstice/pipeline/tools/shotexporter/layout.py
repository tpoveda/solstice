#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for layout files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import json
import traceback

from Qt.QtWidgets import *

from tpPyUtils import path as path_utils

import tpDccLib as tp

from tpQtLib.core import qtutils, image

import artellapipe
from artellapipe.core import defines as artella_defines
from artellapipe.tools.shotmanager.core import defines, assetitem, exporter, shotexporter
from artellapipe.tools.shotmanager.widgets import exportlist, exportpropertieslist

import solstice
from solstice.core import defines as solstice_defines

if tp.is_maya():
    from tpMayaLib.core import thumbnail


class LayoutExportList(exportlist.BaseExportList, object):

    SUPPORTED_TYPES = [
        solstice_defines.SOLSTICE_PROP_TAG_TYPE.strip().lower(),
        solstice_defines.SOLSTICE_BACKGROUND_ELEMENT_TAG_TYPE.strip().lower().replace(' ', '_')
    ]

    def __init__(self, project, parent=None):
        super(LayoutExportList, self).__init__(project=project, parent=parent)

    def init_ui(self):
        prop_icon = artellapipe.solstice.resource.icon('prop')
        bge_icon = artellapipe.solstice.resource.icon('backgroundelement')
        unknown_icon = artellapipe.resource.icon('question')

        assets = self._project.get_scene_assets()
        for asset_node in assets:
            tag_data_node = asset_node.get_tag_node()
            if not tag_data_node:
                continue
            tag_types = tag_data_node.get_types()
            for supported_type in self.SUPPORTED_TYPES:
                if supported_type in tag_types:
                    exporter_asset = assetitem.ExporterAssetItem(asset_node)
                    asset_item = QTreeWidgetItem(self._assets_list, [asset_node.get_short_name()])
                    asset_item.asset_item = exporter_asset
                    if supported_type == self.SUPPORTED_TYPES[0]:
                        asset_item.setIcon(0, prop_icon)
                    elif supported_type == self.SUPPORTED_TYPES[1]:
                        asset_item.setIcon(0, bge_icon)
                    else:
                        asset_item.setIcon(0, unknown_icon)
                    self._assets_list.addTopLevelItem(asset_item)
                    break


class LayoutPropertiesWidget(exportpropertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(LayoutPropertiesWidget, self).__init__(
            name='LayoutPropertiesEditor',
            label='Layout Properties',
            title='Layout Properties Editor',
            parent=parent
        )


class LayoutExporter(exporter.BaseExporter, object):

    EXPORTER_NAME = 'Layout'
    EXPORTER_ICON = solstice.resource.icon('layout')
    EXPORTER_FILE = solstice_defines.SOLSTICE_LAYOUT_SHOT_FILE_TYPE
    EXPORTER_EXTENSION = solstice_defines.SOLSTICE_LAYOUT_EXTENSION
    EXPORT_BUTTON_TEXT = 'SAVE LAYOUT'
    EXPORTER_LIST_WIDGET_CLASS = LayoutExportList
    EXPORTER_PROPERTIES_WIDGET_CLASS = LayoutPropertiesWidget

    def __init__(self, project, parent=None):
        super(LayoutExporter, self).__init__(project=project, parent=parent)

    def _on_save(self):
        if not tp.is_maya():
            artellapipe.logger.warning('Layout Export only works for Maya!')
            return

        self.show_layout_capture_dialog()

    def show_layout_capture_dialog(self):
        title = 'Create Layout Thumbnail'
        text = 'Would you like to capture Layout thumbnail?'

        res = qtutils.show_question(self, title, text)
        if res == QMessageBox.Yes:
            self._thumbnail_capture()
        else:
            self._do_save()

        return res

    def _thumbnail_capture(self):
        """
        Internal function that captures a thumbnail from viewport
        """

        try:
            path = self._project.get_temp_path('sequence', 'thumbnail.jpg')
            thumbnail.ThumbnailCaptureDialog.thumbnail_capture(path=path, clear_cache=True, step=1, captured=self._do_save)
        except Exception as e:
            artellapipe.logger.error('{} | {}'.format(e, traceback.format_exc()))
            raise

    def _do_save(self, thumb_path=None):
        if not tp.is_maya():
            artellapipe.logger.warning('Layout Export only works for Maya!')
            return

        scene_name = tp.Dcc.scene_name()
        if not scene_name:
            scene_name = 'undefined'
        else:
            scene_name = os.path.basename(scene_name)

        export_path = tp.Dcc.select_folder_dialog(title='Select Layout Export Path', start_directory=self._project.get_path())
        if not export_path:
            return

        export_path = path_utils.clean_path(os.path.join(export_path, scene_name+self.EXPORTER_EXTENSION))

        layout_info = dict()
        layout_info['data_version'] = self._project.DataVersions.LAYOUT
        layout_info['exporter_version'] = shotexporter.ShotExporter.VERSION

        if thumb_path:
            layout_info['icon'] = image.image_to_base64(thumb_path)
        layout_info['assets'] = dict()

        self._progress.set_minimum(0)
        self._progress.set_maximum(self._export_list.count())
        self._progress.setVisible(True)
        self._progress.set_text('Exporting Layout File ...')

        for i in range(self._export_list.count()):
            exporter_asset_item = self._export_list.asset_at(i)
            asset_name = exporter_asset_item.short_name
            asset_path = os.path.relpath(exporter_asset_item.path, self._project.get_path())
            self._progress.set_value(i+1)
            self._progress.set_text('Storing: {}'.format(asset_name))
            layout_info['assets'][asset_name] = dict()
            layout_info['assets'][asset_name]['path'] = asset_path
            layout_info['assets'][asset_name]['attrs'] = dict()
            layout_info['assets'][asset_name]['type'] = exporter_asset_item.asset_node.get_current_extension()
            versions = exporter_asset_item.asset_node.asset.get_latest_local_versions(
                status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS
            )
            layout_info['assets'][asset_name]['versions'] = versions

            for attr, flag in exporter_asset_item.attrs.items():
                if not flag and attr not in defines.MUST_ATTRS:
                    continue
                attr_value = tp.Dcc.get_attribute_value(node=asset_name, attribute_name=attr)
                layout_info['assets'][asset_name]['attrs'][attr] = attr_value

        self._progress.set_text('Storing Layout File ...')
        try:
            with open(export_path, 'w') as f:
                json.dump(layout_info, f)
        except Exception as e:
            artellapipe.logger.error('{} | {}'.format(e, traceback.format_exc()))

        self._progress.set_value(0)
        self._progress.set_text('')
        self._progress.setVisible(False)


shotexporter.register_exporter(LayoutExporter)
