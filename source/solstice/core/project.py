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

from artellapipe.core import project as artella_project

import solstice
from solstice.launcher import tray
from solstice.core import asset, node, shelf


class Solstice(artella_project.ArtellaProject):

    PROJECT_PATH = solstice.get_project_path()
    TRAY_CLASS = tray.SolsticeTray
    SHELF_CLASS = shelf.SolsticeShelf
    ASSET_CLASS = asset.SolsticeAsset
    ASSET_NODE_CLASS = node.SolsticeAssetNode
    TAG_NODE_CLASS = asset.SolsticeTagNode
    PROJECT_CONFIG_PATH = solstice.get_project_config_path()
    PROJECT_CHANGELOG_PATH = solstice.get_project_changelog_path()
    PROJECT_SHELF_FILE_PATH = solstice.get_project_shelf_path()
    PROJECT_MENU_FILE_PATH = solstice.get_project_menu_path()

    def __init__(self, resource, naming_file):

        self._project_url = None
        self._documentation_url = None

        super(Solstice, self).__init__(resource=resource, naming_file=naming_file)

    def init_config(self):
        """
       Overrides base ArtellaProject init_config function to load extra attributes from configuration file
       """

        super(Solstice, self).init_config()

        project_config_data = self.get_config_data()
        if not project_config_data:
            return

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
            path_utils.clean_path(os.path.join(solstice.get_project_path(), 'pipeline', 'tools', 'publisher', 'plugins'))
        )

        return publisher_plugin_paths

    def get_shaders_path(self):
        """
        Overrides base ArtellaProject get_shaders_path function
        Returns path where shareds are located in the project
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_assets_path(), 'Scripts', 'PIPELINE', '__working__', 'ShadersLibrary'))

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
