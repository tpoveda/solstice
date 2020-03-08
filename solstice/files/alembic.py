#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for alembic asset files
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


class SolsticeAlembicAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None):
        super(SolsticeAlembicAssetFile, self).__init__(file_asset=asset)


class SolsticeGpuAlembicAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None):
        super(SolsticeGpuAlembicAssetFile, self).__init__(file_asset=asset)

    def _import_file(self, file_path, *args, **kwargs):
        namespace = kwargs.get('namespace', None)
        unique_namespace = kwargs.get('unique_namespace', True)
        if not namespace:
            namespace = self.asset.get_id()
            if tp.Dcc.namespace_exists(namespace) and unique_namespace:
                namespace = tp.Dcc.unique_namespace(namespace)

        if tp.is_maya():
            gpu_node = artellapipe.Alembic().import_alembic(
                file_path, namespace=namespace, as_gpu_cache=True, unique_namespace=unique_namespace)
            gpu_node_parent = tp.Dcc.node_parent(node=gpu_node)
            return gpu_node_parent
        else:
            LOGGER.warning(
                'GPU Cache is not supported in "{}" DCC. Importer standard Alembic!'.format(tp.Dcc.get_name()))
            return artellapipe.Alembic().import_alembic(file_path, namespace=namespace)
