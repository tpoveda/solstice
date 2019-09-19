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

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpPyUtils import decorators

import tpDccLib as tp

import artellapipe
from artellapipe.core import defines as artella_defines
from artellapipe.utils import tag
from artellapipe.tools.outliner.widgets import items

from solstice.core import defines

if tp.is_maya():
    from tpMayaLib.core import decorators as maya_decorators
    undo_decorator = maya_decorators.undo_chunk
else:
    undo_decorator = decorators.empty_decorator


class SolsticeOutlinerAssetItem(items.OutlinerAssetItem, object):

    replaceCompleted = Signal()

    def __init__(self, asset_node, parent=None):
        super(SolsticeOutlinerAssetItem, self).__init__(asset_node=asset_node, parent=parent)

    def _create_replace_actions(self, replace_menu):

        rig_icon = artellapipe.solstice.resource.icon('rig')
        alembic_icon = artellapipe.solstice.resource.icon('alembic')
        # standin_icon = artellapipe.solstice.resource.icon('standin')

        rig_action = QAction(rig_icon, 'Rig', replace_menu)
        alembic_action = QAction(alembic_icon, 'Alembic', replace_menu)
        # standin_action = QAction(standin_icon, 'Standin', replace_menu)

        replace_menu.addAction(rig_action)
        replace_menu.addAction(alembic_action)
        # replace_menu.addAction(standin_action)

        rig_action.triggered.connect(self._on_replace_rig)
        alembic_action.triggered.connect(self._on_replace_alembic)
        # standin_action.triggered.connect(self._on_replace_standin)

        if self._asset_node.is_rig():
            rig_action.setVisible(False)
        elif self._asset_node.is_alembic():
            alembic_action.setVisible(False)

        return True

    def _on_replace_alembic(self):

        if self._asset_node.is_alembic():
            artellapipe.solstice.logger.warning('You have already Alembic file of the asset loaded!')
            return False

        node_asset = self._asset_node.asset
        if not node_asset:
            artellapipe.solstice.logger.warning('Impossible to retrieve Asset linked to Alembic. Aborting operation ...')
            return False

        abc_file_type = node_asset.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE, defines.SOLSTICE_ALEMBIC_EXTENSION)
        if not abc_file_type:
            artellapipe.solstice.logger.warning('Alembic Asset File Type not found for Asset: {}!'.format(node_asset))
            return

        if self._asset_node.is_rig():
            n_tag = tag.get_tag_node(project=artellapipe.solstice, node=self._asset_node.node)
            if not n_tag:
                artellapipe.logger.warning('Not Tag Node found. Aborting operation ...')
                return False
            main_node = n_tag.get_asset_node()
            if not main_node:
                artellapipe.logger.warning('Tag Data node: {} is not linked to any node! Aborting operation ...'.format(n_tag.node))
                return
            node_to_retrieve_xform = main_node.node
            attrs = tp.Dcc.list_user_attributes(node=main_node.node)
            if attrs and type(attrs) == list:
                if 'root_ctrl' in attrs:
                    root_ctrl = tp.Dcc.get_attribute_value(main_node.node, attribute_name='root_ctrl')
                    if not tp.Dcc.object_exists(root_ctrl):
                        artellapipe.solstice.logger.warning('Root Control "{}" does not exists in current scene! Aborting operation ...'.format(root_ctrl))
                        return False
                    node_to_retrieve_xform = root_ctrl
                else:
                    for n in tp.Dcc.node_children(node=main_node.node, all_hierarchy=True):
                        if n.endswith('root_ctrl'):
                            node_to_retrieve_xform = n
                            break

            if not node_to_retrieve_xform or not tp.Dcc.object_exists(node_to_retrieve_xform):
                artellapipe.logger.warning('No valid node found to retrieve rig transform from. Aborting operation ...')
                return

            current_matrix = tp.Dcc.node_matrix(node_to_retrieve_xform)
            ref_nodes = abc_file_type.reference_file(status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)
            for n in ref_nodes:
                n_tag = tag.get_tag_node(project=artellapipe.solstice, node=n)
                if n_tag:
                    main_node = n_tag.get_asset_node()
                    if not main_node:
                        artellapipe.logger.warning('Tag Data node: {} is not linked to any node! Aborting operation ...'.format(n_tag.node))
                        return
                    tp.Dcc.set_node_matrix(main_node.node, current_matrix)
                    self._asset_node.remove()
                    break

            if not n_tag:
                artellapipe.logger.warning('Not Tag Node found. Aborting operation ...')
                return False

            self.replaceCompleted.emit()
            return True


        # is_referenced = tp.Dcc.node_is_referenced(self._asset_node.node)
        # if is_referenced:
        #     if self.is_rig():
        #         main_group_connections = tp.Dcc.list_source_connections(node=self._asset_node.node)
        #         for connection in main_group_connections:
        #             attrs = tp.Dcc.list_user_attributes(node=connection)
        #             if attrs and type(attrs) == list:
        #                 if 'root_ctrl' not in attrs:
        #                     artellapipe.solstice.logger.warning('Asset Rig is not ready for replace functionality yet!')
        #                     return
        #                 print('come onnnn')
        #
        #         # ref_node = sys.solstice.dcc.reference_node(self.asset.node)
        #         # if not ref_node:
        #         #     return
        #         # sys.solstice.dcc.unload_reference(ref_node)
        #     elif self.is_standin():
        #         pass
        #     else:
        #         artellapipe.solstice.logger.warning('Impossible to replace {} by Alembic!'.format(self._name))
        # else:
        #     artellapipe.solstice.logger.warning('Imported asset cannot be replaced!')

        # # if self.asset.node != hires_group:
        # #     is_referenced = cmds.referenceQuery(asset.node, isNodeReferenced=True)
        # #     if is_referenced:
        # #         namespace = cmds.referenceQuery(asset.node, namespace=True)
        # #         if not namespace or not namespace.startswith(':'):
        # #             sys.solstice.logger.error('Node {} has not a valid namespace!. Please contact TD!'.format(asset.node))
        # #             continue
        # #         else:
        # #             namespace = namespace[1:] + ':'

    def _on_replace_rig(self):
        """
        Internal callback function that is called when rig file needs to be loaded into scene
        :return: bool
        """

        if self._asset_node.is_rig():
            artellapipe.logger.warning('You have already rig file of the asset loaded!')
            return False

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
                return False

            node_asset = self._asset_node.asset
            if not node_asset:
                artellapipe.solstice.logger.warning('Impossible to retrieve Asset linked to rig. Aborting operation ...')
                return False

            current_matrix = tp.Dcc.node_matrix(self._asset_node.node)
            ref_nodes = node_asset.reference_file(file_type='rig', status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)
            n_tag = None
            for n in ref_nodes:
                n_tag = tag.get_tag_node(project=artellapipe.solstice, node=n)
                if n_tag:
                    main_node = n_tag.get_asset_node()
                    if not main_node:
                        artellapipe.logger.warning('Tag Data node: {} is not linked to any node! Aborting operation ...'.format(n_tag.node))
                        return
                    node_to_apply_xform = main_node.node
                    attrs = tp.Dcc.list_user_attributes(node=main_node.node)
                    if attrs and type(attrs) == list:
                        find_root_ctrl = False
                        if 'root_ctrl' not in attrs:
                            find_root_ctrl = True
                            break
                        else:
                            root_ctrl = tp.Dcc.get_attribute_value(main_node.node, attribute_name='root_ctrl')
                            if not tp.Dcc.object_exists(root_ctrl):
                                artellapipe.solstice.logger.warning('Root Control "{}" does not exists in current scene! Aborting operation ...'.format(root_ctrl))
                                return
                            node_to_apply_xform = root_ctrl

                    tp.Dcc.set_node_matrix(node_to_apply_xform, current_matrix)
                    self._asset_node.remove()
                    break

            if not n_tag:
                artellapipe.logger.warning('Not Tag Node found. Aborting operation ...')
                return False

            if find_root_ctrl:
                for n in ref_nodes:
                    if n.endswith('root_ctrl'):
                        tp.Dcc.set_node_matrix(n, current_matrix)
                        self._asset_node.remove()
                        self.replaceCompleted.emit()
                        return True
                artellapipe.logger.warning('No Root Control found. Impossible to place rig in proper location!')
                return False

            self.replaceCompleted.emit()
            return True

    def _on_replace_standin(self):
        pass
