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

from tpPyUtils import path as path_utils

import artellapipe
from artellapipe.core import artellalib, defines as artella_defines, asset as artella_asset

from solstice.core import defines


class SolsticeAsset(artella_asset.ArtellaAsset, object):
    def __init__(self, project, asset_data):
        super(SolsticeAsset, self).__init__(project=project, asset_data=asset_data)

    def get_file(self, file_type, status, extension=None):
        """
        Overrides base ArtellaAsset get_file function
        Returns file path of the given file type and status
        :param file_type: str
        :param status: str
        :param extension: str
        """

        if not extension:
            extension = artella_defines.ARTELLA_DEFAULT_ASSET_FILES_EXTENSION

        if file_type not in self.project.asset_files:
            return None
        if not artella_asset.ArtellaAssetFileStatus.is_valid(status):
            return None

        if file_type in [defines.SOLSTICE_MODEL_ASSET_TYPE, defines.SOLSTICE_TEXTURES_ASSET_TYPE]:
            file_name = self.get_short_name()
            file_name += extension
        else:
            return super(SolsticeAsset, self).get_file(file_type=file_type, status=status)

        if status == artella_asset.ArtellaAssetFileStatus.WORKING:
            if file_type == defines.SOLSTICE_TEXTURES_ASSET_TYPE:
                file_path = path_utils.clean_path(os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type))
            else:
                file_path = path_utils.clean_path(os.path.join(self.get_path(), artella_defines.ARTELLA_WORKING_FOLDER, file_type, file_name))
        else:
            raise NotImplementedError('Open Published Assets is not implemented yet!')

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
                artellapipe.solstice.logger.warning('Impossible to open "{}": {}'.format(file_type, file_path))
        else:
            super(SolsticeAsset, self).open_file(file_type=file_type, status=status)

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
        elif extension == defines.SOLSTICE_RIG_ASSET_TYPE:
            self.reference_rig_file()

    def reference_alembic_file(self, namespace=None, unresolve_path=True):
        pass

    def reference_standin_file(self):
        pass

    def reference_rig_file(self):
        pass




class SolsticeAssetWidget(artella_asset.ArtellaAssetWidget, object):
    def __init__(self, asset, parent=None):
        super(SolsticeAssetWidget, self).__init__(asset=asset, parent=parent)
