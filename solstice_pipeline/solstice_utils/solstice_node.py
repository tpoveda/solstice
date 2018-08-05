#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Module that contains Maya node definitions to work with Solstice
# ==================================================================="""

import os
import re
import ast

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella

# =================================================================================================

FULL_NAME_REGEX = re.compile(r'(?P<env>\A.+)(?P<art>_art/production/)(?P<code>.+)(?P<category>Assets/)(?P<assettype>[^/]+)/(?P<name>[^/]+)/(?P<version>[^/]+)/(?P<type>[^/]+)/(?P<filename>.+\Z)')

# =================================================================================================


class SolsticeNode(object):
    def __init__(self, node):
        super(SolsticeNode, self).__init__()

        self._node = node

        self._exists = False
        self._valid = False
        self._loaded = False
        self._filename = None
        self._filename_with_copy_number = None
        self._namespace = None
        self._parent_namespace = None
        self._nodes_list = list()

        self.update_info()

    # =================================================================================================

    def get_node(self):
        return self._node

    def get_exists(self):
        return self._exists

    def get_is_valid(self):
        return self._valid

    def get_is_loaded(self):
        return self._loaded

    def get_filename(self):
        if not os.path.isfile(self._filename):
            return None
        return self._filename

    def get_base_name(self):
        if not os.path.isfile(self._filename):
            return None
        return os.path.basename(self._filename)

    def get_dir_name(self):
        if not os.path.isfile(self._filename):
            return None
        return os.path.dirname(self._filename)

    def get_namespace(self):
        return self._namespace

    def get_parent_namespace(self):
        return self._parent_namespace

    def get_nodes_list(self):
        return self._nodes_list

    node = property(get_node)
    exists = property(get_exists)
    valid = property(get_is_valid)
    loaded = property(get_is_loaded)
    filename = property(get_filename)
    basename = property(get_base_name)
    dirname = property(get_dir_name)
    namespace = property(get_namespace)
    parent_namespace = property(get_parent_namespace)
    nodes_list = property(get_nodes_list)

    # =================================================================================================

    def update_info(self):
        """
        Updates all the info related with the given node
        """

        self._exists = cmds.objExists(self.node)
        if not self._exists:
            return False

        try:
            self._loaded = cmds.referenceQuery(self.node, isLoaded=True)
        except Exception as e:
            sp.logger.error('Cannot query this reference node: "{}"'.format(self.node))
        if self._loaded:
            try:
                self._filename = cmds.referenceQuery(self.node, filename=True, withoutCopyNumber=True)
                self._valid = True
            except Exception as e:
                self._valid = False

        try:
            self._namespace = cmds.referenceQuery(self.node, namespace=True)
        except Exception as e:
            pass

        try:
            self._parent_namespace = cmds.referenceQuery(self.node, parentNamespace=True)
        except Exception as e:
            pass

        if self._valid:
            self._filename_with_copy_number = cmds.referenceQuery(self.node, filename=True, withoutCopyNumber=False)
            self._nodes_list = cmds.referenceQuery(self.node, nodes=True)

    def change_namespace(self, new_namespace):
        """
         Updates the namespace of the reference stored node
        :param new_namespace: str
        :return: str
        """

        result = None
        try:
            result = cmds.namespace(rename=[self.namespace, new_namespace])
        except Exception as e:
            sp.logger.warning('Impossible to change namespace for reference node: "{0}" >> "{1}" to "{2}" --> {3}'.format(self.node, self.namespace, new_namespace, e))

        if result:
            sp.logger.info('Namespace for reference node: "{0}" >> "{1}" to "{2}" changed successfully!'.format(self.node, self.namespace, new_namespace))

        self.update_info()

        return result

    def change_filename(self, new_filename):
        """
        Updates the filename that the current stored reference node is pointing to
        :param new_filename: str
        :return: str
        """

        result = None
        try:
            result = cmds.file(new_filename, loadReference=self.node)
        except Exception as e:
            sp.logger.error('Impossible to change filename for reference node: "{0}" > "{1}" to "{2}" --> {3}'.format(self.node, self.filename, new_filename, e))

        self.update_info()

        return result

    def convert_reference_to_absolute_path(self):
        """
        Updates the current path the stored reference is pointing to from relative to absolute relative to
        the Solstice Artella Project path
        :return: str
        """

        solstice_project_path = os.environ.get(artella.artella_root_prefix)

        try:
            artella_absolute_path = self.filename.lower().replace('${}'.format(artella.artella_root_prefix.lower()), solstice_project_path).replace('\\', '/')
            if os.path.exists(artella_absolute_path):
                self.change_filename(artella_absolute_path)
            else:
                sp.logger.warning('Impossible to convert "{0}" to absolute path: "{1}", because new file does not exists!'.format(self.filename, artella_absolute_path))
        except Exception as e:
            sp.logger.error('Could not import object from reference node: "{}"'.format(str(e)))

        self.update_info()

    def import_objects(self, with_absolute_path=False):
        """
        Import objects pointed by the stored reference node
        :param with_absolute_path: str, Whether the imported objects should be imported using a relative or an absolute path
        :return: str
        """

        solstice_project_path = os.environ.get(artella.artella_root_prefix)
        result = None

        try:
            if with_absolute_path:
                artella_absolute_path = self.filename.lower().replace('${}'.format(artella.artella_root_prefix.lower()), solstice_project_path).replace('\\', '/')
                if os.path.exists(artella_absolute_path):
                    self.change_filename(artella_absolute_path)

            result = cmds.file(self.filename, importReference=True)
        except Exception as e:
            sp.logger.error('Impossible to import objects from reference node: "{0}" --> {1}'.format(self.node, e))

        if result:
            sp.logger.info('Imported objects from node: "{}" successfully!'.format(self.node))

        self.update_info()

        return result


class SolsticeAssetNode(SolsticeNode, object):
    def __init__(self, node):
        super(SolsticeAssetNode, self).__init__(node=node)

        self._name = None
        self._asset_type = None
        self._current_version = None
        self._latest_version = None
        self._version_folder = dict()

        self.update_info()

    # =================================================================================================

    def get_name(self):
        return self._name

    def get_asset_type(self):
        return self._asset_type

    def get_current_version(self):
        return self._current_version

    def get_latest_version(self):
        return self._latest_version

    def set_latest_version(self, version):
        self._latest_version = version

    def get_version_folder(self):
        return self._version_folder

    name = property(get_name)
    asset_type = property(get_asset_type)
    current_version = property(get_current_version)
    latest_version = property(get_latest_version, set_latest_version)
    version_folder = property(get_version_folder)

    # =================================================================================================

    def update_info(self):
        super(SolsticeAssetNode, self).update_info()

        if self.valid:
            valid_asset_name = FULL_NAME_REGEX.search(self.filename)
            if valid_asset_name:
                print('ASSET IS VALID')
            else:
                sp.logger.warning('File "{0}" does not follow a correct nomenclature!'.format(self.filename))


class SolsticeTagDataNode(object):
    def __init__(self, node):
        super(SolsticeTagDataNode, self).__init__()

        self._node = node

    def get_node(self):
        return self._node

    def get_asset(self):
        if not self._node or not cmds.objExists(self._node):
            return None
        if not cmds.attributeQuery('node', node=self._node, exists=True):
            return None

        connections = cmds.listConnections(self._node+'.node')
        if connections:
            node = connections[0]
            if cmds.objExists(node):
                return node

        return None

    def get_tag_type(self):
        if not self._node or not cmds.objExists(self._node):
            return None
        if not cmds.attributeQuery('tag_type', node=self._node, exists=True):
            return None

        return cmds.getAttr(self._node + '.tag_type')

    def get_types(self):
        if not self._node or not cmds.objExists(self._node):
            return []
        if not cmds.attributeQuery('types', node=self._node, exists=True):
            return []

        return cmds.getAttr(self._node + '.types')

    def get_proxy_group(self):
        if not self._node or not cmds.objExists(self._node):
            return None
        if not cmds.attributeQuery('proxy', node=self._node, exists=True):
            return None

        connections = cmds.listConnections(self._node + '.proxy')
        if connections:
            node = connections[0]
            if cmds.objExists(node):
                return node

        return None

    def get_hires_group(self):
        if not self._node or not cmds.objExists(self._node):
            return None
        if not cmds.attributeQuery('hires', node=self._node, exists=True):
            return None

        connections = cmds.listConnections(self._node + '.hires')
        if connections:
            node = connections[0]
            if cmds.objExists(node):
                return node

        return None

    def get_shaders(self):
        if not self._node or not cmds.objExists(self._node):
            return None
        if not cmds.attributeQuery('shaders', node=self._node, exists=True):
            return None

        shaders_attr = cmds.getAttr(self._node + '.shaders')
        shaders_attr_fixed = shaders_attr.replace("'", "\"")
        shaders_dict = ast.literal_eval(shaders_attr_fixed)
        if type(shaders_dict) != dict:
            sp.logger.error('Impossible to get dictionary from shaders attribute. Maybe shaders are not set up properly. Please contact TD!')
        else:
            return shaders_dict

        return shaders_attr
