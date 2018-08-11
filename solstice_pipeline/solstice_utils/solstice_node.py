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
import collections

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella

# =================================================================================================

FULL_NAME_REGEX = re.compile(r'(?P<env>\A.+)(?P<art>_art/production/)(?P<code>.+)(?P<category>Assets/)(?P<assettype>[^/]+)/(?P<name>[^/]+)/(?P<version>[^/]+)/(?P<type>[^/]+)/(?P<filename>.+\Z)')

# =================================================================================================


class SolsticeNode(object):
    def __init__(self, node=None):
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

        if self._node is None:
            return False

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
    def __init__(self, node=None, **kwargs):
        super(SolsticeAssetNode, self).__init__(node=node)

        if node is not None:
            self._name = node
        else:
            self._name = kwargs['name'] if 'name' in kwargs else 'New_Asset'
        self._asset_path = kwargs['path'] if 'path' in kwargs else self._get_asset_path()
        self._category = kwargs['category'] if 'category' in kwargs else None
        self._description = kwargs['description'] if 'description' in kwargs else ''

        self._current_version = None
        self._latest_version = None
        self._version_folder = dict()

        self.update_info()

    # =================================================================================================

    def get_name(self):
        return self._name

    def get_short_name(self):
        return self._name.split(':')[-1].split('|')[-1]

    def get_asset_path(self):
        return self._asset_path

    def get_category(self):
        return self._category

    def get_description(self):
        return self._description

    def get_current_version(self):
        return self._current_version

    def get_latest_version(self):
        return self._latest_version

    def set_latest_version(self, version):
        self._latest_version = version

    def get_version_folder(self):
        return self._version_folder

    name = property(get_name)
    asset_path = property(get_asset_path)
    category = property(get_category)
    description = property(get_description)
    current_version = property(get_current_version)
    latest_version = property(get_latest_version, set_latest_version)
    version_folder = property(get_version_folder)

    # =================================================================================================

    def print_asset_info(self):
        print('- {0}'.format(self._name))
        print('\t          Path: {0}'.format(self._asset_path))
        print('\t      Category: {0}'.format(self._category))
        print('\t   Description: {0}'.format(self._category))

    def update_info(self):
        super(SolsticeAssetNode, self).update_info()

        if self.valid:
            valid_asset_name = FULL_NAME_REGEX.search(self.filename)
            if valid_asset_name:
                print('ASSET IS VALID')
            else:
                sp.logger.warning('File "{0}" does not follow a correct nomenclature!'.format(self.filename))

    def get_local_versions(self, status='published', categories=None):

        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        local_folders = dict()
        for f in folders:
            local_folders[f] = dict()

        for p in os.listdir(self._asset_path):
            if status == 'working':
                if p != '__working__':
                    continue

                for f in os.listdir(os.path.join(self._asset_path, '__working__')):
                    if f in folders:
                        if f == 'textures':
                            # In textures we can have multiple textures files with different versions each one
                            txt_files = list()
                            for (dir_path, dir_names, file_names) in os.walk(os.path.join(self._asset_path, '__working__', f)):
                                txt_files.extend(file_names)
                                break

                            textures_history = dict()
                            if len(txt_files) > 0:
                                for txt in txt_files:
                                    txt_path = os.path.join(self._asset_path, '__working__', f, txt)
                                    txt_history = artella.get_asset_history(txt_path)
                                    textures_history[txt] = txt_history
                            local_folders[f] = textures_history
                        else:
                            asset_name = self._name
                            if f == 'shading':
                                asset_name = asset_name + '_SHD'
                            file_path = os.path.join(self._asset_path, '__working__', f, asset_name+'.ma')
                            history = artella.get_asset_history(file_path)
                            local_folders[f] = history
            else:
                if p == '__working__':
                    continue

                for f in folders:
                    if f in p:
                        version = sp.get_asset_version(p)[1]
                        local_folders[f][str(version)] = p

                # Sort all dictionaries by version number when we are getting published version info
                for f in folders:
                    local_folders[f] = collections.OrderedDict(sorted(local_folders[f].items()))

        return local_folders

    def get_max_local_versions(self, categories=None):

        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        max_local_versions = dict()
        for f in folders:
            max_local_versions[f] = None

        local_versions = self.get_local_versions()

        for f, versions in local_versions.items():
            if versions:
                for version, version_folder in versions.items():
                    if max_local_versions[f] is None:
                        max_local_versions[f] = [int(version), version_folder]
                    else:
                        if int(max_local_versions[f][0]) < int(version):
                            max_local_versions[f] = [int(version), version_folder]

        return max_local_versions

    def get_asset_data_path(self):
        asset_path = self.asset_path
        if asset_path is None or not os.path.exists(asset_path):
            raise RuntimeError('Asset Path {} does not exists!'.format(asset_path))

        asset_data_file = os.path.join(asset_path, '__working__', 'data.json')
        if not os.path.isfile(asset_data_file):
            # TODO: Maybe sync automatically if the data file is not already synced
            sp.logger.warning('Asset Data file {} is not sync yet! Sync it using Solstice Pipelinizer Tool plesae!'.format(asset_data_file))

        return asset_data_file

    def get_asset_file(self, file_type, status):
        """
        Returns file to an asset file
        :param file_type: str
        :param status: str
        :return: str
        """

        if file_type not in sp.valid_categories:
            return None
        if status not in sp.valid_status:
            return None

        asset_name = self.get_short_name()
        if file_type == 'shading':
            asset_name = self.get_short_name() + '_SHD'
        elif file_type == 'groom':
            asset_name = self.get_short_name() + '_GROOMING'
        asset_name = asset_name + '.ma'

        file_path = None
        if status == 'working':
            file_path = os.path.join(self._asset_path, '__working__', file_type, asset_name)
        elif status == 'published':
            local_max_versions = self.get_max_local_versions()
            if local_max_versions[file_type]:
                file_path = os.path.join(self._asset_path, local_max_versions[file_type][1], file_type, asset_name)

        return file_path

    def get_asset_files(self, status='published'):
        asset_files = dict()
        for cat in sp.valid_categories:
            asset_file = self.get_asset_file(cat, status)
            if asset_file is None or not os.path.exists(asset_file):
                continue
            asset_files[cat] = asset_file

        return asset_files

    def _get_asset_path(self):
        assets_path = sp.get_solstice_assets_path()
        if assets_path is None or not os.path.exists(assets_path):
            raise RuntimeError('Asset Path is not valid: {}'.format(assets_path))

        for root, dirs, files in os.walk(assets_path):
            asset_path = root
            asset_name = os.path.basename(root)
            if asset_name == self.get_short_name():
                return os.path.normpath(asset_path)


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
            return SolsticeAssetNode(node=node)

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
