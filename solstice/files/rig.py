#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for rig asset files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

import tpDccLib as tp
if tp.is_maya():
    import tpMayaLib as maya

from artellapipe.core import assetfile


class SolsticeRigAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset):
        super(SolsticeRigAssetFile, self).__init__(file_asset=asset)

    def _reference_file(self, file_path, sync=False, *args, **kwargs):

        namespace = self.asset.get_id()

        if tp.is_maya():
            if not namespace:
                use_rename = maya.cmds.optionVar(q='referenceOptionsUseRenamePrefix')
                if use_rename:
                    namespace = maya.cmds.optionVar(q='referenceOptionsRenamePrefix')
                else:
                    filename = os.path.basename(file_path)
                    namespace, _ = os.path.splitext(filename)
            if tp.Dcc.namespace_exists(namespace):
                namespace = tp.Dcc.unique_namespace(namespace)
            return tp.Dcc.reference_file(file_path=file_path, namespace=namespace)
        else:
            return tp.Dcc.reference_file(file_path=file_path)
