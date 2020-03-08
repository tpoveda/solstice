#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for DCC nodes in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import tpDcc as tp

import artellapipe

from solstice.core import utils

LOGGER = logging.getLogger()


class SolsticeAssetNode(artellapipe.AssetNode, object):
    def __init__(self, project, asset, node=None, **kwargs):
        super(SolsticeAssetNode, self).__init__(project=project, asset=asset, node=node, **kwargs)

    # def get_current_extension(self):
    #     """
    #     Overrides base ArtellaAsset get_current_extension function
    #     Returns the extension of the current asset file loaded
    #     :return: str
    #     """
    #
    #     if self.is_rig():
    #         return defines.SOLSTICE_RIG_EXTENSION
    #     elif self.is_alembic():
    #         return defines.SOLSTICE_ALEMBIC_EXTENSION
    #     else:
    #         return defines.SOLSTICE_STANDIN_EXTENSION
    #
    # def get_current_extension_icon(self):
    #     """
    #     Returns icon of the current asset extension
    #     :return: QIcon
    #     """
    #
    #     current_extension = self.get_current_extension()
    #     if current_extension == defines.SOLSTICE_RIG_EXTENSION:
    #         return resource.ResourceManager().icon('rig')
    #     elif current_extension == defines.SOLSTICE_ALEMBIC_EXTENSION:
    #         return resource.ResourceManager().icon('alembic')
    #     else:
    #         return resource.ResourceManager().icon('standin')

    def switch_to_proxy(self):
        if self.is_rig():
            if not tp.Dcc.attribute_exists(self._node, 'type'):
                LOGGER.warning('Rig for "{}" is not ready to switch between proxy/high models'.format(self.id))
                return
            tp.Dcc.set_integer_attribute_value(self._node, 'type', 0)
        elif self.is_gpu_cache():
            asset_shape_operator = self.get_shape_operator()
            if not asset_shape_operator:
                asset_shape_operator = self.create_shape_operator()
            if not asset_shape_operator:
                LOGGER.warning('Impossible to switch proxy for GPU Cache "{}"'.format(self.id))
                return
            self.remove_shape_operator_assignment('subdiv_type')
            self.remove_shape_operator_assignment('subdiv_iterations')

    def switch_to_hires(self):
        if self.is_rig():
            if not tp.Dcc.attribute_exists(self._node, 'type'):
                LOGGER.warning('Rig for "{}" is not ready to switch between proxy/high models'.format(self.id))
                return
            tp.Dcc.set_integer_attribute_value(self._node, 'type', 1)
        elif self.is_gpu_cache():
            asset_shape_operator = self.get_shape_operator()
            if not asset_shape_operator:
                asset_shape_operator = self.create_shape_operator()
            if not asset_shape_operator:
                LOGGER.warning('Impossible to switch proxy for GPU Cache "{}"'.format(self.id))
                return
            self.add_shape_operator_assignment("subdiv_type = 'catclark'")
            self.add_shape_operator_assignment('subdiv_iterations = 2')

    def is_rig(self):
        """
        Returns whether current asset is a rig or not
        :return: bool
        """

        tag_node = self.get_tag_node()
        if not tag_node:
            return False

        return True

    def is_gpu_cache(self):
        """
        Returns whether current asset is a GPU alembic or not
        :return: bool
        """

        shapes = tp.Dcc.list_shapes(self._node)
        if not shapes:
            return False

        for shape in shapes:
            shape_type = tp.Dcc.node_type(shape)
            if shape_type == 'gpuCache':
                return True

        return False

    def is_standin(self):
        """
        Returns whether current asset is a Standin or not
        :return: bool
        """

        shapes = tp.Dcc.list_shapes(self._node)
        if not shapes:
            return False

        for shape in shapes:
            shape_type = tp.Dcc.node_type(shape)
            if shape_type == 'aiStandIn':
                return True

        return False

    def get_control(self, rig_control):
        """
        Returns main control of the current asset
        :return: str
        """

        if not rig_control:
            rig_control = 'root_ctrl'

        tag_node = artellapipe.TagsMgr().get_tag_node(project=self._project, node=self.node)
        if not tag_node:
            LOGGER.warning('No Tag Node found! Aborting operation ...')
            return None
        asset_node = tag_node.get_asset_node()
        if not asset_node:
            LOGGER.warning('Tag Data node: {} is not linked to any asset! Aborting operation ...'.format(tag_node))
            return
        node_to_apply_xform = asset_node.node
        attrs = tp.Dcc.list_user_attributes(node_to_apply_xform)
        if attrs and type(attrs) == list:
            if rig_control not in attrs:
                all_children = tp.Dcc.list_children(self.node)
                for child in all_children:
                    if child.endswith(rig_control):
                        return child
            else:
                root_ctrl = tp.Dcc.get_attribute_value(node_to_apply_xform, attribute_name=rig_control)
                if not tp.Dcc.object_exists(root_ctrl):
                    LOGGER.warning(
                        '"{}" does not exists in current scene! Aborting operation...'.format(
                            root_ctrl))
                    return None
                return root_ctrl

        return None

    def replace_by_rig(self, rig_control=None):
        """
        Replaces current asset by its rig file
        :param rig_control: str
        :return:
        """

        if not rig_control:
            rig_control = 'root_ctrl'

        if self.is_rig():
            return

        rig_file_class = artellapipe.FilesMgr().get_file_class('rig')
        if not rig_file_class:
            LOGGER.warning('Impossible to reference rig file because Rig File Class (rig) was not found!')
            return

        node_namespace = tp.Dcc.node_namespace(self.node, clean=True)
        current_matrix = tp.Dcc.node_matrix(self.node)
        parent_node = tp.Dcc.node_parent(self.node)

        self.remove()

        rig_file = rig_file_class(self.asset)
        ref_nodes = rig_file.import_file(reference=True, namespace=node_namespace, unique_namespace=False)
        if not ref_nodes:
            LOGGER.warning('No nodes imported into current scene for rig file!')
            return None

        root_ctrl = None
        for node in ref_nodes:
            root_ctrl = utils.get_control(node=node, rig_control=rig_control)
            if root_ctrl:
                break
        if not root_ctrl:
            return False

        tp.Dcc.set_node_matrix(root_ctrl, current_matrix)
        if parent_node and tp.Dcc.object_exists(parent_node):
            asset_node = artellapipe.AssetsMgr().get_asset_node_in_scene(root_ctrl)
            if not asset_node:
                return
            tp.Dcc.set_parent(asset_node.node, parent_node)

        return True

    def replace_by_gpu_cache(self, rig_control=None):
        """
        Replaces current asset by its gpu cache file
        :param rig_control: str
        :return:
        """

        if not rig_control:
            rig_control = 'root_ctrl'

        if self.is_gpu_cache():
            return

        if self.is_rig():
            main_ctrl = self.get_control(rig_control)
            if not main_ctrl:
                LOGGER.warning('No Main Control found for Asset Node: {}'.format(self.node))
                return False
            node_namespace = tp.Dcc.node_namespace(main_ctrl, clean=True)
            main_world_translate = tp.Dcc.node_world_space_translation(main_ctrl)
            main_world_rotation = tp.Dcc.node_world_space_rotation(main_ctrl)
            main_world_scale = tp.Dcc.node_world_space_scale(main_ctrl)
            parent_node = tp.Dcc.node_parent(self.node)
        else:
            node_namespace = tp.Dcc.node_namespace(self.node, clean=True)
            main_world_translate = tp.Dcc.node_world_space_translation(self.node)
            main_world_rotation = tp.Dcc.node_world_space_rotation(self.node)
            main_world_scale = tp.Dcc.node_world_space_scale(self.node)
            parent_node = tp.Dcc.node_parent(self.node)

        gpu_cache_file_class = artellapipe.FilesMgr().get_file_class('gpualembic')
        if not gpu_cache_file_class:
            LOGGER.warning(
                'Impossible to import gpu cache file because GpuAlembic File Class (gpualembic) was not found!')
            return False

        self.remove()

        gpu_cache_file = gpu_cache_file_class(self.asset)
        ref_nodes = gpu_cache_file.import_file(namespace=node_namespace, unique_namespace=False)
        if not ref_nodes:
            LOGGER.warning('No nodes imported into current scene for gpu cache file!')
            return False

        if isinstance(ref_nodes, (list, tuple)):
            gpu_cache_node = ref_nodes[0]
        else:
            gpu_cache_node = ref_nodes

        tp.Dcc.translate_node_in_world_space(gpu_cache_node, main_world_translate)
        tp.Dcc.rotate_node_in_world_space(gpu_cache_node, main_world_rotation)
        tp.Dcc.scale_node_in_world_space(gpu_cache_node, main_world_scale)
        if parent_node and tp.Dcc.object_exists(parent_node):
            tp.Dcc.set_parent(gpu_cache_node, parent_node)

        return True

    def replace_by_standin(self, rig_control=None):
        """
        Replaces current asset by its standin file
        :param rig_control: str
        :return:
        """

        if not rig_control:
            rig_control = 'root_ctrl'

        if self.is_standin():
            return

        if self.is_rig():
            main_ctrl = self.get_control(rig_control)
            if not main_ctrl:
                LOGGER.warning('No Main Control found for Asset Node: {}'.format(self.node))
                return False
            node_namespace = tp.Dcc.node_namespace(main_ctrl, clean=True)
            main_world_translate = tp.Dcc.node_world_space_translation(main_ctrl)
            main_world_rotation = tp.Dcc.node_world_space_rotation(main_ctrl)
            main_world_scale = tp.Dcc.node_world_space_scale(main_ctrl)
            parent_node = tp.Dcc.node_parent(self.node)
        else:
            node_namespace = tp.Dcc.node_namespace(self.node, clean=True)
            main_world_translate = tp.Dcc.node_world_space_translation(self.node)
            main_world_rotation = tp.Dcc.node_world_space_rotation(self.node)
            main_world_scale = tp.Dcc.node_world_space_scale(self.node)
            parent_node = tp.Dcc.node_parent(self.node)

        standin_file_class = artellapipe.FilesMgr().get_file_class('standin')
        if not standin_file_class:
            LOGGER.warning('Impossible to import standin file because Standin File Class (standin) was not found!')
            return False

        self.remove()

        standin_file = standin_file_class(self.asset)
        ref_nodes = standin_file.import_file(namespace=node_namespace, unique_namespace=False)
        if not ref_nodes:
            LOGGER.warning('No nodes imported into current scene for standin file!')
            return False

        if isinstance(ref_nodes, (list, tuple)):
            gpu_cache_node = ref_nodes[0]
        else:
            gpu_cache_node = ref_nodes

        tp.Dcc.translate_node_in_world_space(gpu_cache_node, main_world_translate)
        tp.Dcc.rotate_node_in_world_space(gpu_cache_node, main_world_rotation)
        tp.Dcc.scale_node_in_world_space(gpu_cache_node, main_world_scale)
        if parent_node and tp.Dcc.object_exists(parent_node):
            tp.Dcc.set_parent(gpu_cache_node, parent_node)

        return True


artellapipe.register.register_class('AssetNode', SolsticeAssetNode)
