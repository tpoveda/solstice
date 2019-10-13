#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for asset in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import ast
import logging

from tpPyUtils import python, path as path_utils

import tpDccLib as tp

from artellapipe.core import artellalib, defines as artella_defines, asset as artella_asset

from solstice.core import defines

LOGGER = logging.getLogger()


class SolsticeAsset(artella_asset.ArtellaAsset, object):
    def __init__(self, project, asset_data, node=None):
        super(SolsticeAsset, self).__init__(project=project, asset_data=asset_data, node=node)

    def get_file(self, file_type, status, extension=None, fix_path=False):
        """
        Overrides base ArtellaAsset get_file function
        Returns file path of the given file type and status
        :param file_type: str
        :param status: str
        :param extension: str
        :param fix_path: bool
        """

        if not extension:
            extension = artella_defines.ARTELLA_DEFAULT_ASSET_FILES_EXTENSION

        if hasattr(file_type, 'FILE_TYPE'):
            file_type = file_type.FILE_TYPE

        if file_type not in self.project.asset_files:
            return None
        if not artella_asset.ArtellaAssetFileStatus.is_valid(status):
            return None

        if file_type in [defines.SOLSTICE_MODEL_ASSET_TYPE, defines.SOLSTICE_TEXTURES_ASSET_TYPE]:
            file_name = self.get_name()
            file_name += extension
        else:
            return super(SolsticeAsset, self).get_file(file_type=file_type, status=status)

        if status == artella_asset.ArtellaAssetFileStatus.WORKING:
            if file_type == defines.SOLSTICE_TEXTURES_ASSET_TYPE:
                file_path = path_utils.clean_path(
                    os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type))
            else:
                file_path = path_utils.clean_path(
                    os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type, file_name))
        else:
            raise NotImplementedError('Open Published Assets is not implemented yet!')

        if fix_path:
            file_path = self._project.fix_path(file_path)

        return file_path

    def open_file(self, file_type, status):
        """
        Overrides base ArtellaAsset open_file function
        Opens asset file with the given type and status (if exists)
        :param file_type: str
        :param status: str
        """

        if file_type == defines.SOLSTICE_TEXTURES_ASSET_TYPE:
            file_path = self.get_file(file_type=file_type, status=status)
            if os.path.isdir(file_path):
                artellalib.explore_file(file_path)
            else:
                LOGGER.warning('Impossible to open "{}": {}'.format(file_type, file_path))
        else:
            super(SolsticeAsset, self).open_file(file_type=file_type, status=status)

    def import_file_by_extension(self, extension=None):
        """
        Implements base AbstractAsset reference_file_by_extension function
        References asset file with the given extension
        :param extension: str
        """

        if extension == defines.SOLSTICE_ALEMBIC_EXTENSION:
            self.import_alembic_file()
        elif extension == defines.SOLSTICE_STANDIN_EXTENSION:
            self.import_standin_file()
        elif extension == defines.SOLSTICE_RIG_EXTENSION:
            self.import_rig_file()
        else:
            self._project.logger.error(
                'Extension "{}" is not supported in {}!'.format(extension, self._project.name.title()))

    def get_shading_type(self):
        """
        Implements base ArtellaAsset get_shading_type function
        Returns the asset file type of the shading file for the project
        :return: str
        """

        return defines.SOLSTICE_SHADING_ASSET_TYPE

    def reference_file_by_extension(self, extension=None):
        """
        Implements base AbstractAsset reference_file_by_extension function
        References asset file with the given extension
        :param extension: str
        """

        if extension == defines.SOLSTICE_ALEMBIC_EXTENSION:
            self.reference_alembic_file()
        elif extension == defines.SOLSTICE_STANDIN_EXTENSION:
            self.reference_standin_file()
        elif extension == defines.SOLSTICE_RIG_EXTENSION:
            self.reference_rig_file()
        else:
            self._project.logger.error(
                'Extension "{}" is not supported in {}!'.format(extension, self._project.name.title()))

    def import_rig_file(self):
        """
        Imports rig file of the current asset
        """

        self.import_file(
            file_type=defines.SOLSTICE_RIG_ASSET_TYPE, status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)

    def reference_rig_file(self):
        """
        References rig file of the current asset
        """

        self.reference_file(
            file_type=defines.SOLSTICE_RIG_ASSET_TYPE, status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)

    def import_standin_file(self):
        """
        Imports Standin file of the current asset
        :return: str
        """

        model_file_type = self.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE)
        latest_published_local_versions = model_file_type.get_latest_local_published_version()
        if not latest_published_local_versions:
            LOGGER.warning('Asset {} has not model files synced!'.format(self.get_name()))
            return

        standin_file_type = self.get_file_type(
            defines.SOLSTICE_MODEL_ASSET_TYPE, extension=defines.SOLSTICE_STANDIN_EXTENSION)
        if not standin_file_type:
            LOGGER.warning('Asset {} has not Alembic File published!')
            return

        standin_file_type.import_file(artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)

    def reference_standin_file(self):
        """
        References Standin file of the current asset
        :return: str
        """

        self.import_standin_file()

    def import_alembic_file(self, parent_name=None, fix_path=True):
        """
        Imports Alembic file of the current asset
        :param parent_name: str
        :param fix_path: bool
        """

        model_file_type = self.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE)
        latest_published_local_versions = model_file_type.get_latest_local_published_version()
        if not latest_published_local_versions:
            LOGGER.warning('Asset {} has not model files synced!'.format(self.get_name()))
            return

        alembic_file_type = self.get_file_type(
            defines.SOLSTICE_MODEL_ASSET_TYPE, extension=defines.SOLSTICE_ALEMBIC_EXTENSION)
        if not alembic_file_type:
            LOGGER.warning('Asset {} has not Alembic File published!')
            return

        alembic_file_type.import_file(artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS, parent=parent_name)

    def reference_alembic_file(self, namespace=None, fix_path=True):
        """
        References Alembic file of the current asset
        :param namespace: str
        :param fix_path: bool
        """

        model_file_type = self.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE)
        latest_published_local_versions = model_file_type.get_latest_local_published_version()
        if not latest_published_local_versions:
            LOGGER.warning('Asset {} has not model files synced!'.format(self.get_name()))
            return

        alembic_file_type = self.get_file_type(
            defines.SOLSTICE_MODEL_ASSET_TYPE, extension=defines.SOLSTICE_ALEMBIC_EXTENSION)
        if not alembic_file_type:
            LOGGER.warning('Asset {} has not Alembic File published!')
            return

        alembic_file_type.reference_file(artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)


class SolsticeAssetWidget(artella_asset.ArtellaAssetWidget, object):
    def __init__(self, asset, parent=None):
        super(SolsticeAssetWidget, self).__init__(asset=asset, parent=parent)


class SolsticeTagNode(artella_asset.ArtellaTagNode, object):
    def __init__(self, project, node, tag_info=None):
        super(SolsticeTagNode, self).__init__(project=project, node=node, tag_info=tag_info)

    def get_types(self):
        """
        Returns a list of types for the current asset
        :return: list(str)
        """

        return python.force_list(self._get_attribute('types'))

    def get_proxy_group(self):
        """
        Returns proxy group linked to tag node
        :return: str
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            return self._node
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='proxy'):
                return None

            connections = tp.Dcc.list_connections(node=self._node, attribute_name='proxy')
            if connections:
                node = connections[0]
                if tp.Dcc.object_exists(node):
                    return node

        return None

    def get_hires_group(self):
        """
        Returns hires group linked to tag node
        :return: str
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            return self._node
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='hires'):
                return None

            connections = tp.Dcc.list_connections(node=self._node, attribute_name='hires')
            if connections:
                node = connections[0]
                if tp.Dcc.object_exists(node):
                    return node

        return None

    def get_shaders(self):
        """
        Returns shaders info linked to this node
        :return: dict
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            shaders_info = self._tag_info_dict.get('shaders', None)
            if not shaders_info:
                LOGGER.warning('Impossible retrieve shaders info of node: {}'.format(self._node))
                return
            shaders_info_fixed = shaders_info.replace("'", "\"")
            shaders_dict = ast.literal_eval(shaders_info_fixed)
            if type(shaders_dict) != dict:
                LOGGER.error(
                    'Impossible to get dictionary from shaders info. Maybe shaders are not set up properly. '
                    'Please contact TD!')
            else:
                return shaders_dict
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='shaders'):
                return None

            shaders_attr = tp.Dcc.get_attribute_value(node=self._node, attribute_name='shaders')
            shaders_attr_fixed = shaders_attr.replace("'", "\"")
            shaders_dict = ast.literal_eval(shaders_attr_fixed)
            if type(shaders_dict) != dict:
                LOGGER.error(
                    'Impossible to get dictionary from shaders attribute. Maybe shaders are not set up properly. '
                    'Please contact TD!')
            else:
                return shaders_dict

            return shaders_attr

        return None
