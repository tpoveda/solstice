#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for standin asset files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import tpDcc as tp

import artellapipe
from artellapipe.core import assetfile

LOGGER = logging.getLogger()


class SolsticeStandinAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None):
        super(SolsticeStandinAssetFile, self).__init__(file_asset=asset)

    def _import_file(self, file_path, *args, **kwargs):
        namespace = kwargs.get('namespace', None)
        unique_namespace = kwargs.get('unique_namespace', True)
        if not namespace:
            namespace = self.asset.get_id()
            if tp.Dcc.namespace_exists(namespace) and unique_namespace:
                namespace = tp.Dcc.unique_namespace(namespace)

        if tp.Dcc.namespace_exists(namespace) and unique_namespace:
            namespace = tp.Dcc.unique_namespace(namespace)

        ass_node = artellapipe.Arnold().import_standin(
            file_path, namespace=namespace, unique_namespace=unique_namespace)
        ass_node_parent = tp.Dcc.node_parent(node=ass_node)

        return ass_node_parent
