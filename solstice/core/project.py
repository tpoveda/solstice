#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Artella project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import webbrowser
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

import os

from tpPyUtils import path as path_utils

import artellapipe
print(artellapipe.core)
print(artellapipe)
print(artellapipe.core)

from artellapipe.core import project as artella_project, defines as artella_defines

from solstice.core import defines, asset, node, shelf, tray


class Solstice(artella_project.ArtellaProject):

    TRAY_CLASS = tray.SolsticeTray
    SHELF_CLASS = shelf.SolsticeShelf
    ASSET_CLASS = asset.SolsticeAsset
    ASSET_NODE_CLASS = node.SolsticeAssetNode
    TAG_NODE_CLASS = asset.SolsticeTagNode

    class DataVersions(artella_project.ArtellaProject.DataVersions):
        LAYOUT = '0.0.1'
        ANIM = '0.0.1'
        FX = '0.0.1'
        LIGHTING = '0.0.1'

    class DataExtensions(artella_project.ArtellaProject.DataVersions):
        LAYOUT = defines.SOLSTICE_LAYOUT_EXTENSION
        ANIM = defines.SOLSTICE_ANIMATION_EXTENSION
        FX = defines.SOLSTICE_FX_EXTENSION
        LIGHTING = defines.SOLSTICE_LIGHTING_EXTENSION

    def __init__(self):

        self._project_url = None
        self._documentation_url = None

        super(Solstice, self).__init__(name='Solstice')

    def get_configurations_folder(self):
        """
       Overrides base ArtellaProject get_configuration_folder function
        Returns folder where project configuration files are loaded
        :return: str
        """

        if os.environ.get(defines.SOLSTICE_CONFIGURATION_ENV, None):
            return os.environ[defines.SOLSTICE_CONFIGURATION_ENV]
        else:
            from solstice import config
            return os.path.dirname(config.__file__)

    def get_project_path(self):
        """
        Returns path where Solstice project is located
        :return: str
        """

        return path_utils.clean_path(os.path.dirname(__file__))

    def get_project_config_path(self):
        """
        Returns path where Solstice project config is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_configurations_folder(), artella_defines.ARTELLA_PROJECT_CONFIG_FILE_NAME))

    def get_project_changelog_path(self):
        """
        Returns path where Solstice project changelog is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_configurations_folder(), artella_defines.ARTELLA_PROJECT_CHANGELOG_FILE_NAME))

    def get_project_shelf_path(self):
        """
        Returns path where Solstice project shelf file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_configurations_folder(), artella_defines.ARTELLA_PROJECT_SHELF_FILE_NAME))

    def get_project_menu_path(self):
        """
        Returns path where Solstice project menu file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_configurations_folder(), artella_defines.ARTELLA_PROJECT_SHELF_FILE_NAME))

    def get_project_version_path(self):
        """
        Returns path where version file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_configurations_folder(), artella_defines.ARTELLA_PROJECT_DEFAULT_VERSION_FILE_NAME))

    def init_config(self, project_name):
        """
       Overrides base ArtellaProject init_config function to load extra attributes from configuration file
       """

        super(Solstice, self).init_config(project_name=project_name)

        project_config_data = self.get_config_data(project_name=project_name)
        if not project_config_data:
            return False

        self._project_url = project_config_data.get('PROJECT_URL', None)
        self._documentation_url = project_config_data.get('PROJECT_DOCUMENTATION_URL', None)
        self._asset_data_filename = project_config_data.get('PROJECT_ASSET_DATA_FILENAME', None)

    @property
    def project_url(self):
        """
        Returns URL to official Plot Twist web page
        :return: str
        """

        return self._project_url

    @property
    def documentation_url(self):
        """
        Returns URL where Plot Twist documentation is stored
        :return: str
        """

        return self._documentation_url

    def open_webpage(self):
        """
        Opens Plot Twist official web page in browser
        """

        if not self._project_url:
            return

        webbrowser.open(self._project_url)

    def open_documentation(self):
        """
        Opens Plot Twist documentation web page in browser
        """

        if not self._documentation_url:
            return

        webbrowser.open(self._documentation_url)

    def get_publisher_plugin_paths(self):
        """
        Overrides base ArtellaProject get_publisher_plugin_paths function
        Function that registers all plugins available for Artella Publisher
        """

        publisher_plugin_paths = super(Solstice, self).get_publisher_plugin_paths()

        publisher_plugin_paths.append(
            path_utils.clean_path(os.path.join(self.get_project_path(), 'pipeline', 'tools', 'publisher', 'plugins'))
        )

        return publisher_plugin_paths

    def get_shaders_path(self):
        """
        Overrides base ArtellaProject get_shaders_path function
        Returns path where shareds are located in the project
        :return: str
        """

        return path_utils.clean_path(os.path.join(
            self.get_assets_path(), 'Scripts', 'PIPELINE', '__working__', 'ShadersLibrary'))

    def get_light_rigs_path(self):
        """
        Returns path where light rigs are located in the project
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_assets_path(), 'lighting', 'Light Rigs'))

    def _register_asset_classes(self):
        """
        Overrides base ArtellaProject _register_asset_classes function
        Internal function that can be override to register specific project asset classes
        """

        from solstice.pipeline.tools.assetsmanager.assets import propasset, backgroundelementasset, characterasset

        self.register_asset_class(propasset.SolsticePropAsset)
        self.register_asset_class(backgroundelementasset.SolsticeBackgroundElementAsset)
        self.register_asset_class(characterasset.SolsticeCharacterAsset)

        super(Solstice, self)._register_asset_classes()

    def _register_asset_file_types(self):
        """
        Overrides base ArtellaProject _register_asset_file_types function
        Internal function that can be override to register specific project file type classes
        """

        from solstice.core import assetfile

        self.register_asset_file_type(assetfile.TexturesAssetFile)
        self.register_asset_file_type(assetfile.ModelAssetFile)
        self.register_asset_file_type(assetfile.ShadingAssetFile)
        self.register_asset_file_type(assetfile.RigAssetFile)
        self.register_asset_file_type(assetfile.GroomAssetFile)
        self.register_asset_file_type(assetfile.AlembicAssetFile)
        self.register_asset_file_type(assetfile.StandinAssetFile)

        super(Solstice, self)._register_asset_file_types()
