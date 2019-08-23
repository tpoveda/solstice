#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains shot file for layout files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import string
from collections import OrderedDict

import tpDccLib as tp

import artellapipe
from artellapipe.tools.shotmanager.core import assetitem, shotassembler, shotexporter

from solstice.core import defines as solstice_defines, node

if tp.is_maya():
    from tpMayaLib.core import scene as maya_scene


class NodeAsset(assetitem.ShotAssetItem, object):

    def __init__(self, asset, name, path, params, layout_file, parent=None):
        self._asset = asset
        self._name = name
        self._params = params
        self._layout_file = layout_file

        self._node = None
        if path:
            self._node = node.SolsticeAssetNode(project=artellapipe.solstice, name=os.path.basename(path))

        super(NodeAsset, self).__init__(name, parent)

        self.set_icon(artellapipe.resource.icon('teapot'))

    def load(self):
        """
        Overrides base ShotAssetItem laod function
        Function that loads item into current DCC scene
        """

        if not tp.is_maya():
            artellapipe.solstice.logger.warning('NodeAsset only can be loaded in Maya!')
            return

        track = maya_scene.TrackNodes(full_path=True)
        track.load()
        namespace = os.path.basename(self.layout_file).split('.')[0]
        self.import_alembic(namespace=namespace)
        res = track.get_delta()

        return res

    @property
    def asset(self):
        """
        Returns asset linked to this node
        :return:
        """

        return self._asset

    @property
    def node(self):
        """
        Returns the DCC node wrapped by this node
        :return:
        """

        return self._node

    @property
    def layout_file(self):
        """
        Returns path where layout file is located
        :return: str
        """

        return self._layout_file

    def get_asset_path(self):
        """
        Returns path where asset is located
        :return: str
        """

        if not self.node:
            return

        return self.node.asset_path

    def get_attributes(self):
        """
        Returns attributes current node is storing
        :return: dict
        """

        if not self.node:
            return {}
        return self._params

    def get_icon(self):
        """
        Returns the icon of the node
        :return: QIcon
        """

        if not self.node:
            return

        return self.node.get_icon()

    def reference_alembic(self, namespace=None):
        """
        References into current DCC scene wrapped node Alembic file
        :param namespace:
        :return:
        """

        if not self.node or not self._asset:
            artellapipe.logger.warning('Impossible to reference layout node: {}'.format(self._name))
            return

        self._asset.reference_alembic_file(namespace=namespace)

    def import_alembic(self, namespace=None):
        """
        Imports into current DCC scene wrapped node Alembic file
        :param namespace:
        :return:
        """

        if not self.node or not self._asset:
            artellapipe.logger.warning('Impossible to reference layout node: {}'.format(self._name))
            return

        self._asset.import_alembic_file(namespace=namespace)


class LayoutShotFile(assetitem.ShotAssetFileItem, object):

    FILE_TYPE = solstice_defines.SOLSTICE_LAYOUT_SHOT_FILE_TYPE
    FILE_ICON = artellapipe.solstice.resource.icon('layout')
    FILE_EXTENSION = solstice_defines.SOLSTICE_LAYOUT_EXTENSION

    def __init__(self, asset_file, parent=None):

        self._assets = dict()

        super(LayoutShotFile, self).__init__(asset_file=asset_file, parent=parent)

    def set_assets(self, assets):
        """
        Sets cache of current assets to be used
        :param assets: dict
        """

        self._assets = assets

    def get_data(self):
        """
        Overrides base ShotAssetItem get_data function
        Returns data of the current asset file
        :return: dict
        """

        asset_data = super(LayoutShotFile, self).get_data()
        if not asset_data:
            return asset_data

        layout_data_version = asset_data['data_version']
        exporter_version = asset_data['exporter_version']
        if layout_data_version != artellapipe.solstice.DataVersions.LAYOUT:
            artellapipe.solstice.logger.warning('Layout Asset File {} is not compatible with current format. Please contact TD!'.format(self._asset_file))
            return
        if exporter_version != shotexporter.ShotExporter.VERSION:
            artellapipe.logger.warning('Layout Asset File {} was exported with an older version. Please contact TD!'.format(self._asset_file))
            return

        layout_data = dict()
        for node_name, node_info in asset_data['assets'].items():
            layout_data[node_name] = dict()
            layout_data[node_name]['data'] = node_info
        ordered_data = OrderedDict(sorted(layout_data.items(), reverse=True))

        return ordered_data

    def get_nodes(self):
        """
        Overrides base ShotAssetItem get_nodes function
        Returns nodes that are stored inside asset file
        :return: list
        """

        data = self.get_data()
        if not data:
            return

        nodes = list()

        if not self._assets:
            self._update_assets()
            if not self._assets:
                artellapipe.logger.warning('No Assets Found!')
                return

        for node_name, node_data in data.items():
            clean_name = node_name.rstrip(string.digits)
            if clean_name not in self._assets:
                artellapipe.logger.warning('Node {} not found in current assets! Skipping ...'.format(node_name))
                continue

            node_asset = self._assets[clean_name]

            new_node = NodeAsset(
                asset=node_asset,
                name=node_name,
                path=node_data['data']['path'],
                params=node_data['data']['attrs'],
                layout_file=self._asset_file
            )
            nodes.append(new_node)

        return nodes

    def _update_assets(self):
        """
        Internal function that updates the cache of current assets
        """

        all_assets = artellapipe.solstice.find_all_assets()
        for asset in all_assets:
            asset_name = asset.get_name()
            if asset_name in self._assets:
                artellapipe.logger.warning('Asset {} is duplicated!'.format(asset_name))
                continue
            self._assets[asset_name] = asset


shotassembler.register_file_type(LayoutShotFile)
