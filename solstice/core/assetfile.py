#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for the different asset files supported by Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpPyUtils import path as path_utils

import tpDccLib as tp

from artellapipe.core import assetfile, artellalib, defines as artella_defines
# from artellapipe.tools.alembicmanager import alembicmanager
# from artellapipe.tools.standinmanager import standinmanager

from solstice.core import defines


class TexturesAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_TEXTURES_ASSET_TYPE
    FILE_EXTENSIONS = defines.SOLSTICE_TEXTURE_EXTENSIONS

    def __init__(self, asset):
        super(TexturesAssetFile, self).__init__(asset=asset)

    def _get_working_server_versions(self, working_path, artella_data, force_update=False):
        """
        Overrides base ArtellaAssetType _get_working_server_versions function
        Internal function that returns all the working server versions of the current file type in the wrapped asset
        :param working_path: str, working path in Artella server
        :param artella_data: ArtellaReferencesMetaData
        :param force_update: bool, Whether to update Artella data or not (this can take time)
        :return:
        """

        if not artella_data:
            return

        ref_path = os.path.join(working_path, artella_data.name)
        file_name = os.path.basename(ref_path)
        for extension in self.FILE_EXTENSIONS:
            if file_name.endswith(extension):
                if not force_update and self._working_history:
                    return self._working_history
                else:
                    return artellalib.get_asset_history(ref_path)


class ModelAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_MODEL_ASSET_TYPE
    FILE_EXTENSIONS = [defines.SOLSTICE_MODEL_EXTENSION]

    def __init__(self, asset):
        super(ModelAssetFile, self).__init__(asset=asset)


class ShadingAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_SHADING_ASSET_TYPE
    FILE_EXTENSIONS = [defines.SOLSTICE_SHADING_EXTENSION]

    def __init__(self, asset):
        super(ShadingAssetFile, self).__init__(asset=asset)

    def _get_working_path(self, asset_name, asset_path):
        """
        Overrides base ArtellaAssetType _get_working_path function
        Internal function that returns working path of the current asset file
        :param asset_name: str
        :param asset_path: str
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            asset_path,
            artella_defines.ARTELLA_WORKING_FOLDER,
            self.FILE_TYPE, asset_name + '_SHD' + self.FILE_EXTENSIONS[0]))

    def _get_published_path(self, asset_name, asset_path, version_folder):
        """
        Overrides base ArtellaAssetType _get_published_path function
        Internal function that returns published path of the current asset file
        :param asset_name: str
        :param asset_path: str
        :param version_folder: str
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            asset_path,
            version_folder,
            self.FILE_TYPE,
            asset_name + '_SHD' + self.FILE_EXTENSIONS[0]))

    def _get_working_server_versions(self, working_path, artella_data, force_update=False):
        """
        Overrides base ArtellaAssetType _get_working_server_versions function
        Internal function that returns all the working server versions of the current file type in the wrapped asset
        :param working_path: str, working path in Artella server
        :param artella_data: ArtellaReferencesMetaData
        :param force_update: bool, Whether to update Artella data or not (this can take time)
        :return:
        """

        if not artella_data:
            return

        asset_name = self._asset.get_name()
        ref_path = os.path.join(working_path, artella_data.name)
        file_name = os.path.basename(ref_path)
        for extension in self.FILE_EXTENSIONS:
            if file_name == '{}_SHD{}'.format(
                    asset_name, extension) or file_name == '{}_shd{}'.format(asset_name, extension):
                if not force_update and self._working_history:
                    return self._working_history
                else:
                    return artellalib.get_asset_history(ref_path)


class RigAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_RIG_ASSET_TYPE
    FILE_EXTENSIONS = [defines.SOLSTICE_RIG_EXTENSION]

    def __init__(self, asset):
        super(RigAssetFile, self).__init__(asset=asset)

    def _get_working_path(self, asset_name, asset_path):
        """
        Overrides base ArtellaAssetType _get_working_path function
        Internal function that returns working path of the current asset file
        :param asset_name: str
        :param asset_path: str
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            asset_path,
            artella_defines.ARTELLA_WORKING_FOLDER,
            self.FILE_TYPE, asset_name + '_RIG' + self.FILE_EXTENSIONS[0]))

    def _get_published_path(self, asset_name, asset_path, version_folder):
        """
        Overrides base ArtellaAssetType _get_published_path function
        Internal function that returns published path of the current asset file
        :param asset_name: str
        :param asset_path: str
        :param version_folder: str
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            asset_path, version_folder, self.FILE_TYPE, asset_name + '_RIG' + self.FILE_EXTENSIONS[0]))


class GroomAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_GROOM_ASSET_TYPE

    def __init__(self, asset):
        super(GroomAssetFile, self).__init__(asset=asset)


class AlembicAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_MODEL_ASSET_TYPE
    FILE_EXTENSIONS = [defines.SOLSTICE_ALEMBIC_EXTENSION]

    def _import_file(self, path, fix_path=True, *args, **kwargs):
        """
        Internal function that imports current file in DCC
        :param fix_path: bool
        :param path: str
        """

        parent = kwargs.get('parent', None)

        alembicmanager.importer.import_alembic(
            project=self.get_project(), alembic_path=path, parent=parent, fix_path=fix_path)

    def _reference_file(self, path, fix_path=True):
        """
        Internal function that references current file in DCC
        :param fix_path: bool
        :param path: str
        """

        if tp.is_houdini():
            return alembicmanager.importer.import_alembic(
                project=self.get_project(), alembic_path=path, fix_path=fix_path)
        else:
            return alembicmanager.importer.reference_alembic(
                project=self.get_project(), alembic_path=path, fix_path=fix_path)


class StandinAssetFile(assetfile.ArtellaAssetType, object):

    FILE_TYPE = defines.SOLSTICE_MODEL_ASSET_TYPE
    FILE_EXTENSIONS = [defines.SOLSTICE_STANDIN_EXTENSION]

    def _import_file(self, path, fix_path=True):
        """
        Internal function that references current file in DCC
        :param fix_path: bool
        :param path: str
        """

        standinmanager.importer.import_standin(project=self.get_project(), standin_path=path, fix_path=fix_path)

    def _reference_file(self, path, fix_path=True):
        """
        Internal function that references current file in DCC
        :param fix_path: bool
        :param path: str
        """

        self._import_file(path=path, fix_path=fix_path)
