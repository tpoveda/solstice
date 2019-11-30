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

import logging

import artellapipe.register
from artellapipe.core import defines, asset as artella_asset

LOGGER = logging.getLogger()


class SolsticeAsset(artella_asset.ArtellaAsset, object):
    def __init__(self, project, asset_data, node=None):
        super(SolsticeAsset, self).__init__(project=project, asset_data=asset_data, node=node)

    # def get_file(self, file_type, status, extension=None, fix_path=False):
    #     """
    #     Overrides base ArtellaAsset get_file function
    #     Returns file path of the given file type and status
    #     :param file_type: str
    #     :param status: str
    #     :param extension: str
    #     :param fix_path: bool
    #     """
    #
    #     if not extension:
    #         extension = artella_defines.ARTELLA_DEFAULT_ASSET_FILES_EXTENSION
    #
    #     if hasattr(file_type, 'FILE_TYPE'):
    #         file_type = file_type.FILE_TYPE
    #
    #     if file_type not in self.project.asset_files:
    #         return None
    #     if not artella_asset.ArtellaAssetFileStatus.is_valid(status):
    #         return None
    #
    #     if file_type in [defines.SOLSTICE_MODEL_ASSET_TYPE, defines.SOLSTICE_TEXTURES_ASSET_TYPE]:
    #         file_name = self.get_name()
    #         file_name += extension
    #     else:
    #         return super(SolsticeAsset, self).get_file(file_type=file_type, status=status)
    #
    #     if status == artella_asset.ArtellaAssetFileStatus.WORKING:
    #         if file_type == defines.SOLSTICE_TEXTURES_ASSET_TYPE:
    #             file_path = path_utils.clean_path(
    #                 os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type))
    #         else:
    #             file_path = path_utils.clean_path(
    #                 os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type, file_name))
    #     else:
    #         raise NotImplementedError('Open Published Assets is not implemented yet!')
    #
    #     if fix_path:
    #         file_path = self._project.fix_path(file_path)
    #
    #     return file_path
    #
    # def open_file(self, file_type, status):
    #     """
    #     Overrides base ArtellaAsset open_file function
    #     Opens asset file with the given type and status (if exists)
    #     :param file_type: str
    #     :param status: str
    #     """
    #
    #     if file_type == defines.SOLSTICE_TEXTURES_ASSET_TYPE:
    #         file_path = self.get_file(file_type=file_type, status=status)
    #         if os.path.isdir(file_path):
    #             artellalib.explore_file(file_path)
    #         else:
    #             LOGGER.warning('Impossible to open "{}": {}'.format(file_type, file_path))
    #     else:
    #         super(SolsticeAsset, self).open_file(file_type=file_type, status=status)
    #
    # def import_file_by_extension(self, extension=None):
    #     """
    #     Implements base AbstractAsset reference_file_by_extension function
    #     References asset file with the given extension
    #     :param extension: str
    #     """
    #
    #     if extension == defines.SOLSTICE_ALEMBIC_EXTENSION:
    #         self.import_alembic_file()
    #     elif extension == defines.SOLSTICE_STANDIN_EXTENSION:
    #         self.import_standin_file()
    #     elif extension == defines.SOLSTICE_RIG_EXTENSION:
    #         self.import_rig_file()
    #     else:
    #         self._project.logger.error(
    #             'Extension "{}" is not supported in {}!'.format(extension, self._project.name.title()))
    #
    # def get_shading_type(self):
    #     """
    #     Implements base ArtellaAsset get_shading_type function
    #     Returns the asset file type of the shading file for the project
    #     :return: str
    #     """
    #
    #     return defines.SOLSTICE_SHADING_ASSET_TYPE

    # def import_rig_file(self):
    #     """
    #     Imports rig file of the current asset
    #     """
    #
    #     self.import_file(
    #         file_type=defines.SOLSTICE_RIG_ASSET_TYPE, status=artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)

    def reference_rig_file(self, file_type, sync=False):
        """
        References rig file of the current asset
        """

        return self.reference_file(
            file_type=file_type, namespace=self.get_id(),
            status=defines.ArtellaFileStatus.PUBLISHED, sync=sync)

    # def import_standin_file(self):
    #     """
    #     Imports Standin file of the current asset
    #     :return: str
    #     """
    #
    #     model_file_type = self.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE)
    #     latest_published_local_versions = model_file_type.get_latest_local_published_version()
    #     if not latest_published_local_versions:
    #         LOGGER.warning('Asset {} has not model files synced!'.format(self.get_name()))
    #         return
    #
    #     standin_file_type = self.get_file_type(
    #         defines.SOLSTICE_MODEL_ASSET_TYPE, extension=defines.SOLSTICE_STANDIN_EXTENSION)
    #     if not standin_file_type:
    #         LOGGER.warning('Asset {} has not Alembic File published!')
    #         return
    #
    #     standin_file_type.import_file(artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS)
    #
    # def reference_standin_file(self):
    #     """
    #     References Standin file of the current asset
    #     :return: str
    #     """
    #
    #     self.import_standin_file()
    #
    # def import_alembic_file(self, parent_name=None, fix_path=True):
    #     """
    #     Imports Alembic file of the current asset
    #     :param parent_name: str
    #     :param fix_path: bool
    #     """
    #
    #     model_file_type = self.get_file_type(defines.SOLSTICE_MODEL_ASSET_TYPE)
    #     latest_published_local_versions = model_file_type.get_latest_local_published_version()
    #     if not latest_published_local_versions:
    #         LOGGER.warning('Asset {} has not model files synced!'.format(self.get_name()))
    #         return
    #
    #     alembic_file_type = self.get_file_type(
    #         defines.SOLSTICE_MODEL_ASSET_TYPE, extension=defines.SOLSTICE_ALEMBIC_EXTENSION)
    #     if not alembic_file_type:
    #         LOGGER.warning('Asset {} has not Alembic File published!')
    #         return
    #
    #     alembic_file_type.import_file(artella_defines.ARTELLA_SYNC_PUBLISHED_ASSET_STATUS, parent=parent_name)

    def reference_alembic_file(self, file_type, model_type, sync=False):
        """
        References Alembic file of the current asset
        :param namespace: str
        :param fix_path: bool
        """

        model_file_type = self.get_file_type(model_type)
        latest_published_local_versions = model_file_type.get_latest_local_published_version()
        if not latest_published_local_versions:
            LOGGER.warning('Asset {} has not model publsihed files synced!'.format(self.get_name()))
            return None

        file_type_extensions = artellapipe.AssetsMgr().get_file_type_extensions(file_type)
        if not file_type_extensions:
            LOGGER.warning('Impossible to retrieve registered extensions from file type: "{}"'.format(file_type))
            return None
        abc_extension = file_type_extensions[0]

        alembic_file_type = self.get_file_type(model_type, abc_extension)
        if not alembic_file_type:
            LOGGER.warning('Asset {} has not Alembic File published!')
            return None

        self.reference_file(
            file_type=model_type, namespace=self.get_id(), extension=abc_extension,
            status=defines.ArtellaFileStatus.PUBLISHED, sync=sync)

        # alembic_file_type.reference_file(
        #     namespace=self.get_id(), status=artella_asset.ArtellaAssetFileStatus.PUBLISHED, sync=sync)


# class SolsticeAssetWidget(artella_asset.ArtellaAssetWidget, object):
#     def __init__(self, asset, parent=None):
#         super(SolsticeAssetWidget, self).__init__(asset=asset, parent=parent)


artellapipe.register.register_class('Asset', SolsticeAsset)
