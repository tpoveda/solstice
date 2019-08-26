#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains different outliners for Solstice Outliner
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDccLib as tp

from artellapipe.tools.outliner.widgets import baseoutliner

from solstice.pipeline.tools.outliner.items import base


class SolsticeBaseOutliner(baseoutliner.BaseOutliner, object):

    OUTLINER_ITEM = base.SolsticeOutlinerAssetItem

    def __init__(self, project, parent=None):
        super(SolsticeBaseOutliner, self).__init__(project=project, parent=parent)

    def _on_toggle_proxy_hires(self, widget, item_index):
        node_name = widget.parent.asset_node.node
        if tp.Dcc.object_exists(node_name):
            if tp.Dcc.attribute_exists(node=node_name, attribute_name='type'):
                widget.parent.block_callbacks = True
                try:
                    tp.Dcc.set_integer_attribute_value(node=node_name, attribute_name='type', attribute_value=item_index)
                except Exception:
                    widget.parent.block_callbacks = False
                widget.parent.block_callbacks = False






