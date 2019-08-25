#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base asset implementatiosn for Solstice Outliner items
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

from tpPyUtils import decorators

import tpDccLib as tp

import artellapipe
from artellapipe.tools.outliner.widgets import items

if tp.is_maya():
    from tpMayaLib.core import decorators as maya_decorators
    undo_decorator = maya_decorators.undo_chunk
else:
    undo_decorator = decorators.empty_decorator


class SolsticeOutlinerAssetItem(items.OutlinerAssetItem, object):
    def __init__(self, asset_node, parent=None):
        super(SolsticeOutlinerAssetItem, self).__init__(asset_node=asset_node, parent=parent)

    def _create_replace_actions(self, replace_menu):

        rig_icon = artellapipe.solstice.resource.icon('rig')
        alembic_icon = artellapipe.solstice.resource.icon('alembic')
        standin_icon = artellapipe.solstice.resource.icon('standin')

        rig_action = QAction(rig_icon, 'Rig', replace_menu)
        alembic_action = QAction(alembic_icon, 'Alembic', replace_menu)
        standin_action = QAction(standin_icon, 'Standin', replace_menu)

        replace_menu.addAction(rig_action)
        replace_menu.addAction(alembic_action)
        replace_menu.addAction(standin_action)

        rig_action.triggered.connect(self._on_replace_rig)
        alembic_action.triggered.connect(self._on_replace_alembic)
        standin_action.triggered.connect(self._on_replace_standin)

        return True

    @undo_decorator
    def _on_replace_alembic(self):
        abc_file = self._asset_node.get_alembic_files()
        is_referenced = tp.Dcc.node_is_referenced(self._asset_node.node)
        if is_referenced:
            if self.is_rig():
                main_group_connections = tp.Dcc.list_source_connections(node=self._asset_node.node)
                for connection in main_group_connections:
                    attrs = tp.Dcc.list_user_attributes(node=connection)
                    if attrs and type(attrs) == list:
                        if 'root_ctrl' not in attrs:
                            artellapipe.solstice.logger.warning('Asset Rig is not ready for replace functionality yet!')
                            return
                        print('come onnnn')

                # ref_node = sys.solstice.dcc.reference_node(self.asset.node)
                # if not ref_node:
                #     return
                # sys.solstice.dcc.unload_reference(ref_node)
            elif self.is_standin():
                pass
            else:
                artellapipe.solstice.logger.warning('Impossible to replace {} by Alembic!'.format(self._name))
        else:
            artellapipe.solstice.logger.warning('Imported asset cannot be replaced!')

        # if self.asset.node != hires_group:
        #     is_referenced = cmds.referenceQuery(asset.node, isNodeReferenced=True)
        #     if is_referenced:
        #         namespace = cmds.referenceQuery(asset.node, namespace=True)
        #         if not namespace or not namespace.startswith(':'):
        #             sys.solstice.logger.error('Node {} has not a valid namespace!. Please contact TD!'.format(asset.node))
        #             continue
        #         else:
        #             namespace = namespace[1:] + ':'

    def _on_replace_rig(self):
        is_referenced = tp.Dcc.node_is_referenced(self._asset_node.node)
        if not is_referenced:
            valid_refs = True
            children = tp.Dcc.node_children(self._asset_node.node, all_hierarchy=False, full_path=True)
            for child in children:
                is_child_ref = tp.Dcc.node_is_referenced(child)
                if not is_child_ref:
                    valid_refs = False
                    break
            if not valid_refs:
                artellapipe.solstice.logger.warning('Impossible to replace {} by rig file ...'.format(self._asset_node.node))
                return
            rig_ref = self._asset_node.reference_asset_file('rig')
            print(rig_ref)

    def _on_replace_standin(self):
        pass
