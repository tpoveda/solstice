#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains export list widget for layout files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.tools.shotexporter.core import assetitem
from solstice.pipeline.tools.shotexporter.widgets import exportlist

reload(exportlist)
reload(assetitem)


class LayoutExportList(exportlist.BaseExportList, object):
    ExportType = 'LAYOUT NODES'

    def __init__(self, parent=None):
        super(LayoutExportList, self).__init__(parent=parent)

    def init_ui(self):
        assets = sp.get_assets()
        for asset in assets:
            tag_data_node = asset.get_tag_data_node()
            if not tag_data_node:
                continue
            # tag_types = tag_data_node.get_types()
            exporter_asset = assetitem.ExporterAssetItem(asset)
            asset_item = QTreeWidgetItem(self.assets_list, [asset.name])
            asset_item.asset = exporter_asset
            self.assets_list.addTopLevelItem(asset_item)

