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

import solstice
from solstice.core import defines as solstice_defines, node

if tp.is_maya():
    from tpMayaLib.core import scene as maya_scene


class NodeAsset(assetitem.ShotAssetItem, object):

    def __init__(self, asset, name, path, type, params, layout_file, parent=None):
        self._asset = asset
        self._name = name
        self._path = path
        self._params = params
        self._layout_file = layout_file

        self._node = None
        if path:
            self._node = node.SolsticeAssetNode(project=artellapipe.solstice, name=os.path.basename(path))

        super(NodeAsset, self).__init__(asset_file=name, type=type, parent=parent)

        if self._asset:
            self.set_icon(self._asset.get_icon())
        else:
            self.set_icon(artellapipe.resource.icon('teapot'))

    def load(self):
        """
        Overrides base ShotAssetItem laod function
        Function that loads item into current DCC scene
        """

        if not tp.is_maya():
            artellapipe.solstice.logger.warning('NodeAsset only can be loaded in Maya!')
            return

        track = maya_scene.TrackNodes(full_path=False)
        track.load()
        # namespace = os.path.basename(self.layout_file).split('.')[0]
        self.import_alembic()
        res = track.get_delta()

        if self._name not in res:
            artellapipe.logger.warning('Node "{}" is not loaded!'.format(self._name))
            return

        for attr, attr_value in self.get_attributes().items():
            self.set_attribute(attr, attr_value)

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

    def set_attribute(self, name, value):
        """
        Sets the attribute to the given name and value
        :param name: str
        :param value: str
        """

        if type(value) is float:
            tp.Dcc.set_float_attribute_value(node=self._name, attribute_name=name, attribute_value=value)
        else:
            # artellapipe.logger.warning('Attributes of type "{}" are not supported yet! Skipping:\n\t {} | {}\n'.format(type(value), name, value))
            # artellapipe.logger.warning('Attributes of type "{}" are not supported yet! Skipping:\n\t {} | {}\n'.format(type(value), name, value))
            return

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

    def import_alembic(self):
        """
        Imports into current DCC scene wrapped node Alembic file
        :param namespace:
        :return:
        """

        if not self.node or not self._asset:
            artellapipe.logger.warning('Impossible to reference layout node: {}'.format(self._name))
            return

        self._asset.import_alembic_file(parent_name=self._name)

    def _get_type_icon(self):
        """
        Overrides base ShotAssetItem _get_type_icon function
        Internal function that returns the icon depending of the asset file type being used
        :return: QIcon
        """

        current_extension = self._type
        if current_extension == solstice_defines.SOLSTICE_RIG_EXTENSION:
            return artellapipe.solstice.resource.icon('rig')
        elif current_extension == solstice_defines.SOLSTICE_ALEMBIC_EXTENSION:
            return artellapipe.solstice.resource.icon('alembic')
        else:
            return artellapipe.solstice.resource.icon('standin')


class LayoutShotFile(assetitem.ShotAssetFileItem, object):

    FILE_TYPE = solstice_defines.SOLSTICE_LAYOUT_SHOT_FILE_TYPE
    FILE_ICON = solstice.resource.icon('layout')
    FILE_EXTENSION = solstice_defines.SOLSTICE_LAYOUT_EXTENSION

    def __init__(self, asset_file, asset_data=None, extra_data=None, parent=None):

        self._assets = dict()

        super(LayoutShotFile, self).__init__(asset_file=asset_file, asset_data=asset_data, extra_data=extra_data, parent=parent)

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

        if self._asset_data:
            asset_data = self._asset_data
        else:
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
            layout_data[node_name] = node_info
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

        if not self._assets:
            self._update_assets()
            if not self._assets:
                artellapipe.logger.warning('No Assets Found!')
                return

        data_nodes = self._get_nodes_from_data(data=data)

        if self._extra_data:
            extra_nodes = self._get_nodes_from_data(data=self._extra_data)
            data_nodes.extend(extra_nodes)

        return data_nodes

    def _get_nodes_from_data(self, data):
        """
        Internal function that returns asset nodes from given data
        :param data: dict
        :return: list
        """

        nodes = list()
        for node_name, node_data in data.items():
            clean_name = node_name.rstrip(string.digits)
            if clean_name not in self._assets:
                artellapipe.logger.warning('Node {} not found in current assets! Skipping ...'.format(node_name))
                continue

            node_asset = self._assets[clean_name]

            new_node = NodeAsset(
                asset=node_asset,
                name=node_name,
                path=node_data['path'],
                type=node_data['type'],
                params=node_data['attrs'],
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
