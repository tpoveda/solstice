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

import solstice.pipeline as sp
from solstice.pipeline.tools.shotexporter.widgets import exportlist
from solstice.pipeline.tools.shotexporter.export.animation import exportanimitem


class AnimationExportList(exportlist.AbstractExportList, object):

    EXPORT_TYPE = 'ANIMATION NODES'

    def __init__(self, parent=None):
        super(AnimationExportList, self).__init__(parent=parent)

    def init_ui(self):
        alembics = sp.get_alembics()

        for asset in alembics:
            asset_widget = exportanimitem.AnimationAssetItem(asset[0], alembic_node=asset[1])
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()
            asset_widget.clicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, widget, event):
        if widget is None:
            self.updateProperties.emit(None)
            return

        if sp.dcc.object_exists(widget.asset.name):
            for asset_widget, file_items in self.widget_tree.items():
                if asset_widget != widget:
                    asset_widget.deselect()
                else:
                    asset_widget.select()
            self.updateProperties.emit(widget)
            # widget.set_select(item_state)
        else:
            self._on_refresh_exporter()
            self.updateProperties.emit(None)